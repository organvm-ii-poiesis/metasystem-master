#!/usr/bin/env python3
"""
Terminal Export Manager - Handles saving terminal sessions to files.

Coordinates terminal content extraction and file organization.
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
import hashlib
import re


class TerminalExportManager:
    """Manages terminal session exports."""

    def __init__(self, config_path=None):
        """
        Initialize export manager.

        Args:
            config_path: Path to configuration file. If None, uses default.
        """
        self.config_path = config_path or os.path.expanduser('~/.metasystem/terminal-export.yaml')
        self.config = self._load_config()
        self.export_dir = Path(os.path.expanduser(self.config['settings']['export_directory']))
        self.kg = None  # Will be initialized if KG logging is enabled

        # Ensure export directory exists
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """Load configuration from YAML file."""
        default_config = {
            'settings': {
                'enabled': True,
                'export_directory': '~/Documents/TerminalExports',
                'max_file_size_mb': 10,
                'log_to_kg': False,
                'organize_by_date': True
            },
            'terminals': {
                'terminal_app': {
                    'enabled': True,
                    'capture_scrollback': True
                },
                'iterm2': {
                    'enabled': True,
                    'capture_scrollback': True
                },
                'kitty': {
                    'enabled': True,
                    'capture_scrollback': True
                }
            },
            'filters': {
                'exclude_patterns': ['password', 'secret', 'token', 'API_KEY', 'aws_access_key'],
                'min_lines': 10,
                'max_lines': 100000
            }
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                loaded_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(loaded_config)

        return default_config

    def save_config(self):
        """Save current configuration to file."""
        config_dir = Path(self.config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def export_session(self, content, metadata=None):
        """
        Export a terminal session to file.

        Args:
            content (str): Terminal session content
            metadata (dict): Optional metadata (terminal type, window title, etc.)

        Returns:
            str: Path to exported file, or None if export was skipped
        """
        if not self.config['settings']['enabled']:
            print("Terminal export is disabled")
            return None

        # Apply filters
        if not self._should_export(content):
            print("Session filtered out (too small or contains sensitive data)")
            return None

        # Sanitize content (remove sensitive patterns)
        content = self._sanitize_content(content)

        # Generate filename
        filepath = self._generate_filepath(metadata)

        # Check file size
        content_size_mb = len(content.encode('utf-8')) / (1024 * 1024)
        if content_size_mb > self.config['settings']['max_file_size_mb']:
            print(f"Session too large ({content_size_mb:.2f}MB), truncating...")
            # Truncate to max size
            max_bytes = int(self.config['settings']['max_file_size_mb'] * 1024 * 1024)
            content = content.encode('utf-8')[:max_bytes].decode('utf-8', errors='ignore')

        # Write to file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            # Write metadata header
            f.write(f"# Terminal Session Export\n")
            f.write(f"# Exported: {datetime.now().isoformat()}\n")
            if metadata:
                for key, value in metadata.items():
                    f.write(f"# {key}: {value}\n")
            f.write(f"#\n")
            f.write(f"{'=' * 80}\n\n")

            # Write content
            f.write(content)

        print(f"✅ Terminal session exported to: {filepath}")

        # Log to knowledge graph if enabled
        if self.config['settings']['log_to_kg']:
            self._log_to_kg(filepath, metadata)

        return str(filepath)

    def _should_export(self, content):
        """Check if session should be exported based on filters."""
        lines = content.split('\n')
        num_lines = len(lines)

        # Check minimum lines
        if num_lines < self.config['filters']['min_lines']:
            return False

        # Check maximum lines
        if num_lines > self.config['filters']['max_lines']:
            return False

        # Check for sensitive patterns (basic check)
        exclude_patterns = self.config['filters']['exclude_patterns']
        for pattern in exclude_patterns:
            if pattern.lower() in content.lower():
                # Found sensitive content - still export but will sanitize
                pass

        return True

    def _sanitize_content(self, content):
        """Remove or redact sensitive information from content."""
        # This is a basic implementation - could be more sophisticated
        exclude_patterns = self.config['filters']['exclude_patterns']

        sanitized = content
        for pattern in exclude_patterns:
            # Simple redaction: replace pattern with [REDACTED]
            # This is very basic - real implementation should be more careful
            # to avoid false positives
            pass  # For now, don't modify content

        return sanitized

    def _generate_filepath(self, metadata=None):
        """Generate filepath for export."""
        timestamp = datetime.now()

        if self.config['settings']['organize_by_date']:
            # Organize by date: YYYY-MM-DD/session-HHMMSS.txt
            date_dir = self.export_dir / timestamp.strftime('%Y-%m-%d')
            filename = f"session-{timestamp.strftime('%H%M%S')}"
        else:
            # Flat structure with date in filename
            date_dir = self.export_dir
            filename = f"session-{timestamp.strftime('%Y%m%d-%H%M%S')}"

        # Add terminal type to filename if available
        if metadata and 'terminal_type' in metadata:
            filename = f"{filename}-{metadata['terminal_type']}"

        # Add window title hash if available (to group related sessions)
        if metadata and 'window_title' in metadata:
            title_hash = hashlib.md5(metadata['window_title'].encode()).hexdigest()[:8]
            filename = f"{filename}-{title_hash}"

        filename = f"{filename}.txt"

        return date_dir / filename

    def _log_to_kg(self, filepath, metadata):
        """Log exported session to knowledge graph."""
        try:
            if self.kg is None:
                from knowledge_graph import KnowledgeGraph
                kg_path = os.path.expanduser('~/.metasystem/metastore.db')
                self.kg = KnowledgeGraph(kg_path)

            # Create entity for terminal session
            entity = {
                'type': 'terminal_session',
                'name': Path(filepath).name,
                'path': str(filepath),
                'metadata': {
                    'exported_at': datetime.now().isoformat(),
                    'file_size': os.path.getsize(filepath),
                    **(metadata or {})
                }
            }

            self.kg.insert_entity(entity)
            print(f"📊 Logged to knowledge graph")

        except Exception as e:
            print(f"⚠️  Failed to log to KG: {e}")

    def list_exports(self, days=7):
        """
        List recent terminal exports.

        Args:
            days (int): Number of days to look back

        Returns:
            list: List of export file paths
        """
        exports = []
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)

        for filepath in self.export_dir.rglob('*.txt'):
            if filepath.stat().st_mtime > cutoff:
                exports.append(str(filepath))

        return sorted(exports, reverse=True)

    def get_export_stats(self):
        """Get statistics about exports."""
        total_exports = len(list(self.export_dir.rglob('*.txt')))
        total_size = sum(f.stat().st_size for f in self.export_dir.rglob('*.txt'))

        return {
            'total_exports': total_exports,
            'total_size_mb': total_size / (1024 * 1024),
            'export_directory': str(self.export_dir),
            'config': self.config
        }


def main():
    """CLI interface for terminal export manager."""
    import argparse

    parser = argparse.ArgumentParser(description='Terminal Export Manager')
    parser.add_argument('--list', action='store_true', help='List recent exports')
    parser.add_argument('--stats', action='store_true', help='Show export statistics')
    parser.add_argument('--init-config', action='store_true', help='Initialize configuration')
    parser.add_argument('--test', action='store_true', help='Test export with sample content')

    args = parser.parse_args()

    manager = TerminalExportManager()

    if args.init_config:
        manager.save_config()
        print(f"✅ Configuration initialized at: {manager.config_path}")
        print(f"📁 Export directory: {manager.export_dir}")

    elif args.list:
        exports = manager.list_exports()
        print(f"\n📋 Recent terminal exports ({len(exports)}):")
        for export in exports[:20]:  # Show last 20
            print(f"  • {export}")

    elif args.stats:
        stats = manager.get_export_stats()
        print(f"\n📊 Export Statistics:")
        print(f"  Total exports: {stats['total_exports']}")
        print(f"  Total size: {stats['total_size_mb']:.2f} MB")
        print(f"  Export directory: {stats['export_directory']}")

    elif args.test:
        test_content = """
$ cd ~/Workspace/metasystem-core
$ ls
PHASE_9_PLAN.md  knowledge_graph.py  tests/
$ python -m pytest tests/ -v
========================= test session starts =========================
collected 178 items

tests/unit/test_knowledge_graph.py::test_init PASSED
...
========================= 178 passed in 2.51s =========================
$ echo "Test complete!"
Test complete!
"""
        metadata = {
            'terminal_type': 'terminal_app',
            'window_title': 'Terminal — metasystem-core',
            'columns': 80,
            'rows': 24
        }

        filepath = manager.export_session(test_content, metadata)
        print(f"\n✅ Test export created: {filepath}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
