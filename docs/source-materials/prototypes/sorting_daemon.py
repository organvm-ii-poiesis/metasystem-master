#!/usr/bin/env python3
"""
Sorting Daemon - Automated File Organization

Watches directories and automatically organizes files based on configurable
rules. Supports ML classification, duplicate detection, and knowledge graph
integration.

Critical for keeping system organized without manual intervention.
"""

import hashlib
import json
import os
import re
import shutil
import sys
import time
import zipfile
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import uuid

import yaml

# Import knowledge graph
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_graph import KnowledgeGraph


class SortingDaemon:
    """Automated file organization daemon."""

    def __init__(self, config_path: str = None, kg_path: str = None):
        """Initialize sorting daemon.

        Args:
            config_path: Path to sorting-rules.yaml
            kg_path: Path to knowledge graph database
        """
        if config_path is None:
            config_path = str(Path.home() / ".metasystem" / "sorting-rules.yaml")

        self.config_path = Path(config_path)
        self.kg = KnowledgeGraph(kg_path)
        self.rules = self._load_rules()
        self.settings = self.rules.get('settings', {})
        self.ml_classifiers = self.rules.get('ml_classifiers', {})

        # File hash cache for duplicate detection
        self.hash_cache: Dict[str, str] = {}

    def _load_rules(self) -> Dict[str, Any]:
        """Load sorting rules from YAML file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Rules file not found: {self.config_path}")

        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _expand_path(self, path: str) -> Path:
        """Expand ~ and environment variables in path."""
        expanded = os.path.expanduser(os.path.expandvars(path))
        return Path(expanded)

    def _expand_template(self, template: str, file_path: Path) -> str:
        """Expand template variables.

        Args:
            template: Template string with {{ variables }}
            file_path: File to extract metadata from

        Returns:
            Expanded string
        """
        now = datetime.now()
        file_stat = file_path.stat() if file_path.exists() else None

        replacements = {
            '{{ year }}': str(now.year),
            '{{ month }}': now.strftime('%m'),
            '{{ day }}': now.strftime('%d'),
            '{{ date }}': now.strftime('%Y-%m-%d'),
            '{{ filename }}': file_path.name,
            '{{ extension }}': file_path.suffix,
            '{{ size_mb }}': str(round(file_stat.st_size / (1024 * 1024), 2)) if file_stat else '0'
        }

        result = template
        for var, value in replacements.items():
            result = result.replace(var, value)

        return result

    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        """Check if file matches glob pattern.

        Args:
            file_path: File to check
            pattern: Glob pattern (supports *, ?, {a,b,c})

        Returns:
            True if matches
        """
        import fnmatch

        # Handle {a,b,c} brace expansion
        if '{' in pattern and '}' in pattern:
            # Extract brace content
            match = re.search(r'\{([^}]+)\}', pattern)
            if match:
                options = match.group(1).split(',')
                base_pattern = pattern[:match.start()] + '{}' + pattern[match.end():]

                for option in options:
                    expanded = base_pattern.replace('{}', option)
                    if fnmatch.fnmatch(file_path.name, expanded):
                        return True
                return False

        return fnmatch.fnmatch(file_path.name, pattern)

    def _classify_file_ml(self, file_path: Path) -> Dict[str, float]:
        """Classify file using ML (keyword-based for now).

        Args:
            file_path: File to classify

        Returns:
            Dictionary of {category: confidence}
        """
        results = {}

        # Only try to read text-based files
        if file_path.suffix.lower() not in ['.pdf', '.txt', '.md', '.doc', '.docx']:
            return results

        try:
            # For PDF, try to extract text (simplified - just read raw)
            if file_path.suffix.lower() == '.pdf':
                # Read first 10KB of PDF as text (crude but works for keywords)
                with open(file_path, 'rb') as f:
                    content = f.read(10240).decode('utf-8', errors='ignore').lower()
            else:
                # Read text files
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(10240).lower()

            # Check against each classifier
            for category, config in self.ml_classifiers.items():
                if 'keywords' not in config:
                    continue

                keywords = config['keywords']
                threshold = config.get('confidence_threshold', 0.5)

                # Count keyword matches
                matches = sum(1 for kw in keywords if kw.lower() in content)
                confidence = matches / len(keywords)

                if confidence >= threshold:
                    results[category] = confidence

        except (OSError, UnicodeDecodeError):
            pass

        return results

    def _check_contains_code(self, file_path: Path) -> bool:
        """Check if archive contains code files.

        Args:
            file_path: Archive file to check

        Returns:
            True if contains code
        """
        try:
            code_extensions = self.ml_classifiers.get('contains_code', {}).get('file_extensions', [])
            min_files = self.ml_classifiers.get('contains_code', {}).get('min_code_files', 3)

            code_file_count = 0

            if file_path.suffix == '.zip':
                with zipfile.ZipFile(file_path, 'r') as archive:
                    for name in archive.namelist():
                        if any(name.endswith(ext) for ext in code_extensions):
                            code_file_count += 1
                            if code_file_count >= min_files:
                                return True

            elif file_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(file_path, 'r:*') as archive:
                    for member in archive.getmembers():
                        if any(member.name.endswith(ext) for ext in code_extensions):
                            code_file_count += 1
                            if code_file_count >= min_files:
                                return True

        except (zipfile.BadZipFile, tarfile.TarError, OSError):
            pass

        return False

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file.

        Args:
            file_path: File to hash

        Returns:
            Hex digest of hash
        """
        if str(file_path) in self.hash_cache:
            return self.hash_cache[str(file_path)]

        sha256 = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)

            hash_value = sha256.hexdigest()
            self.hash_cache[str(file_path)] = hash_value
            return hash_value

        except OSError:
            return ""

    def _is_duplicate(self, file_path: Path) -> Tuple[bool, Optional[str]]:
        """Check if file is a duplicate.

        Args:
            file_path: File to check

        Returns:
            (is_duplicate, original_path)
        """
        file_hash = self._compute_file_hash(file_path)
        if not file_hash:
            return (False, None)

        # Query knowledge graph for files with same hash
        facts = self.kg.query_entities(type='file')

        for entity in facts:
            entity_facts = self.kg.get_facts(entity['id'], fact_type='file_hash')
            for fact in entity_facts:
                if fact['value'] == file_hash and entity['path'] != str(file_path):
                    return (True, entity['path'])

        return (False, None)

    def _check_conditions(self, file_path: Path, conditions: Dict[str, Any]) -> bool:
        """Check if file meets rule conditions.

        Args:
            file_path: File to check
            conditions: Condition dictionary from rule

        Returns:
            True if all conditions met
        """
        # ML category check
        if 'ml_category' in conditions:
            classifications = self._classify_file_ml(file_path)
            if conditions['ml_category'] not in classifications:
                return False

        # Size check
        if 'size_gt' in conditions:
            size_str = conditions['size_gt']
            # Parse size (e.g., "1GB", "50MB")
            multiplier = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}
            for unit, mult in multiplier.items():
                if unit in size_str.upper():
                    threshold = float(size_str.upper().replace(unit, '')) * mult
                    if file_path.stat().st_size <= threshold:
                        return False
                    break

        # Age check
        if 'age_days' in conditions:
            age_days = conditions['age_days']
            file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age.days < age_days:
                return False

        # Contains code check
        if 'contains_code' in conditions and conditions['contains_code']:
            if not self._check_contains_code(file_path):
                return False

        # Duplicate check
        if 'is_duplicate' in conditions and conditions['is_duplicate']:
            is_dup, _ = self._is_duplicate(file_path)
            if not is_dup:
                return False

        # External drive mounted check
        if 'external_mounted' in conditions and conditions['external_mounted']:
            external_path = Path('/Volumes/4444-iivii')
            if not external_path.exists():
                return False

        return True

    def _execute_action(self, file_path: Path, action: Dict[str, Any], dry_run: bool = False) -> bool:
        """Execute file action.

        Args:
            file_path: File to act on
            action: Action dictionary from rule
            dry_run: If True, only print what would be done

        Returns:
            True if action executed successfully
        """
        # Delete action
        if action.get('delete'):
            if dry_run:
                print(f"  [DRY RUN] Would delete: {file_path}")
                return True

            try:
                file_path.unlink()
                print(f"  ✅ Deleted: {file_path.name}")
                return True
            except OSError as e:
                print(f"  ❌ Failed to delete {file_path.name}: {e}")
                return False

        # Move action
        if 'move_to' in action:
            target_dir = self._expand_path(self._expand_template(action['move_to'], file_path))

            if dry_run:
                print(f"  [DRY RUN] Would move: {file_path.name} → {target_dir}")
                return True

            try:
                # Create target directory
                if self.settings.get('create_dirs', True):
                    target_dir.mkdir(parents=True, exist_ok=True)

                target_path = target_dir / file_path.name

                # Handle name conflicts
                if target_path.exists():
                    base = target_path.stem
                    suffix = target_path.suffix
                    counter = 1
                    while target_path.exists():
                        target_path = target_dir / f"{base}_{counter}{suffix}"
                        counter += 1

                # Move file
                shutil.move(str(file_path), str(target_path))
                print(f"  ✅ Moved: {file_path.name} → {target_dir}")

                # Create symlink if requested
                if action.get('create_symlink'):
                    symlink_path = file_path.parent / file_path.name
                    symlink_path.symlink_to(target_path)
                    print(f"    ↳ Created symlink: {symlink_path}")

                # Log to knowledge graph
                if self.settings.get('log_all_moves', True):
                    self._log_file_move(file_path, target_path)

                return True

            except (OSError, shutil.Error) as e:
                print(f"  ❌ Failed to move {file_path.name}: {e}")
                return False

        # Prompt action (interactive)
        if 'prompt' in action:
            prompt_text = self._expand_template(action['prompt'], file_path)
            response = input(f"  ❓ {prompt_text} [y/N]: ")

            if response.lower() in ['y', 'yes']:
                if action.get('on_yes') == 'delete':
                    return self._execute_action(file_path, {'delete': True}, dry_run)
                elif action.get('on_yes', {}).get('move_to'):
                    return self._execute_action(file_path, {'move_to': action['on_yes']['move_to']}, dry_run)
            else:
                if action.get('on_no') == 'move_to_review':
                    review_dir = self._expand_path("~/Downloads/Review")
                    return self._execute_action(file_path, {'move_to': str(review_dir)}, dry_run)

        return False

    def _log_file_move(self, source_path: Path, target_path: Path):
        """Log file move to knowledge graph.

        Args:
            source_path: Original file path
            target_path: New file path
        """
        try:
            # Check if file entity exists
            existing = self.kg.query_entities(type='file', path_like=f"%{source_path.name}%")

            if existing:
                # Update existing entity
                entity_id = existing[0]['id']
                self.kg.update_entity(entity_id, {
                    'path': str(target_path),
                    'last_seen': datetime.now().isoformat()
                })
            else:
                # Create new entity
                entity = {
                    'id': str(uuid.uuid4()),
                    'type': 'file',
                    'path': str(target_path),
                    'name': target_path.name,
                    'metadata': {
                        'previous_path': str(source_path),
                        'moved_at': datetime.now().isoformat(),
                        'moved_by': 'sorting_daemon'
                    }
                }
                self.kg.insert_entity(entity)

        except Exception as e:
            print(f"    ⚠️  Failed to log to KG: {e}")

    def scan_directory(self, directory: Path = None, dry_run: bool = None) -> Dict[str, int]:
        """Scan directory and apply sorting rules.

        Args:
            directory: Directory to scan (default: ~/Downloads)
            dry_run: Override global dry_run setting

        Returns:
            Statistics dictionary
        """
        if directory is None:
            directory = self._expand_path("~/Downloads")

        if dry_run is None:
            dry_run = self.settings.get('dry_run', False)

        print(f"🔍 Scanning: {directory}")
        if dry_run:
            print("   [DRY RUN MODE - No files will be moved]")
        print()

        stats = {
            'scanned': 0,
            'matched': 0,
            'moved': 0,
            'deleted': 0,
            'skipped': 0,
            'errors': 0
        }

        # Get all files in directory
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return stats

        files = [f for f in directory.iterdir() if f.is_file()]
        stats['scanned'] = len(files)

        print(f"Found {len(files)} files")
        print()

        # Process each file
        for file_path in files:
            try:
                # Check min age
                min_age_hours = self.settings.get('min_file_age_hours', 0)
                if min_age_hours > 0:
                    file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age.total_seconds() < min_age_hours * 3600:
                        stats['skipped'] += 1
                        continue

                # Try each rule in priority order
                rules_sorted = sorted(
                    self.rules.get('rules', []),
                    key=lambda r: {'high': 0, 'medium': 1, 'low': 2}.get(r.get('priority', 'medium'), 1)
                )

                matched = False

                for rule in rules_sorted:
                    # Check pattern
                    if not self._matches_pattern(file_path, rule['pattern']):
                        continue

                    # Check source directory
                    source = self._expand_path(rule.get('source', '~/Downloads'))
                    if file_path.parent != source:
                        continue

                    # Check conditions
                    conditions = rule.get('conditions', {})
                    if conditions and not self._check_conditions(file_path, conditions):
                        continue

                    # Execute action
                    print(f"📋 Rule: {rule['name']}")
                    print(f"   File: {file_path.name}")

                    action = rule.get('action', {})
                    if self._execute_action(file_path, action, dry_run):
                        stats['matched'] += 1
                        if action.get('delete'):
                            stats['deleted'] += 1
                        elif action.get('move_to'):
                            stats['moved'] += 1
                        matched = True
                        break

                if not matched:
                    stats['skipped'] += 1

            except Exception as e:
                print(f"  ❌ Error processing {file_path.name}: {e}")
                stats['errors'] += 1

        print()
        print("=" * 60)
        print("📊 Summary")
        print("=" * 60)
        print(f"  Scanned: {stats['scanned']}")
        print(f"  Matched: {stats['matched']}")
        print(f"  Moved: {stats['moved']}")
        print(f"  Deleted: {stats['deleted']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Errors: {stats['errors']}")
        print()

        return stats

    def watch(self, directory: Path = None, interval: int = 60):
        """Watch directory and continuously sort files.

        Args:
            directory: Directory to watch (default: ~/Downloads)
            interval: Seconds between scans (default: 60)
        """
        if directory is None:
            directory = self._expand_path("~/Downloads")

        print(f"👀 Watching: {directory}")
        print(f"   Scan interval: {interval} seconds")
        print("   Press Ctrl+C to stop")
        print()

        try:
            while True:
                self.scan_directory(directory)
                print(f"💤 Sleeping for {interval} seconds...")
                print()
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n✅ Stopped watching")


def main():
    """CLI for sorting daemon."""
    import argparse

    parser = argparse.ArgumentParser(description='Metasystem Sorting Daemon')
    parser.add_argument('command', choices=['scan', 'watch', 'test'],
                       help='Command to run')
    parser.add_argument('--directory', type=str,
                       help='Directory to scan (default: ~/Downloads)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview actions without executing')
    parser.add_argument('--interval', type=int, default=60,
                       help='Watch interval in seconds (default: 60)')
    parser.add_argument('--config', type=str,
                       help='Path to sorting-rules.yaml')

    args = parser.parse_args()

    daemon = SortingDaemon(config_path=args.config)

    directory = Path(args.directory) if args.directory else None

    if args.command == 'scan':
        daemon.scan_directory(directory, dry_run=args.dry_run)

    elif args.command == 'watch':
        daemon.watch(directory, interval=args.interval)

    elif args.command == 'test':
        # Test rules without executing
        print("🧪 Testing sorting rules...")
        daemon.scan_directory(directory, dry_run=True)


if __name__ == '__main__':
    main()
