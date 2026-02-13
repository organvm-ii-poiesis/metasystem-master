#!/usr/bin/env python3
"""
Dotfile Watcher Agent - Tracks chezmoi-managed dotfiles

Monitors dotfile changes and logs them to the knowledge graph:
- Scans chezmoi managed files
- Detects changes via git log
- Tracks modification history
- Enables queries like "what dotfiles changed this week?"

Integrates with chezmoi's git repository for change tracking.
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_graph import KnowledgeGraph


class DotfileWatcher:
    """Agent that monitors and tracks dotfile changes."""

    def __init__(self, kg: KnowledgeGraph = None):
        self.kg = kg or KnowledgeGraph()
        self.chezmoi_source = Path.home() / ".local" / "share" / "chezmoi"

    def get_managed_files(self) -> List[str]:
        """Get list of all chezmoi-managed files.

        Returns:
            List of file paths (relative to home)
        """
        try:
            result = subprocess.run(
                ["chezmoi", "managed"],
                capture_output=True,
                text=True,
                check=True
            )
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed to get managed files: {e}")
            return []

    def get_recent_changes(self, since_days: int = 7) -> List[Dict[str, Any]]:
        """Get recent dotfile changes from chezmoi git log.

        Args:
            since_days: Number of days to look back

        Returns:
            List of change records with commit info
        """
        since_date = datetime.now() - timedelta(days=since_days)
        since_str = since_date.strftime("%Y-%m-%d")

        try:
            # Get git log from chezmoi source directory
            result = subprocess.run(
                ["git", "log", f"--since={since_str}",
                 "--pretty=format:%H|%ai|%s", "--name-only"],
                cwd=str(self.chezmoi_source),
                capture_output=True,
                text=True,
                check=True
            )

            changes = []
            current_commit = None

            for line in result.stdout.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if '|' in line:
                    # Commit info line
                    parts = line.split('|')
                    if len(parts) >= 3:
                        current_commit = {
                            'hash': parts[0],
                            'timestamp': parts[1],
                            'message': parts[2],
                            'files': []
                        }
                        changes.append(current_commit)
                elif current_commit is not None:
                    # File changed in this commit
                    current_commit['files'].append(line)

            return changes

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Failed to get git log: {e}")
            return []

    def sync_dotfiles_to_kg(self) -> Dict[str, Any]:
        """Sync all managed dotfiles to knowledge graph.

        Creates/updates dotfile entities with current state.

        Returns:
            Report with counts
        """
        print("📂 Syncing dotfiles to knowledge graph...\n")

        managed_files = self.get_managed_files()
        new_count = 0
        updated_count = 0

        for dotfile in managed_files:
            file_path = Path.home() / dotfile

            # Check if dotfile entity already exists
            existing = self.kg.query_entities(
                type='dotfile',
                path_like=dotfile,
                limit=1
            )

            metadata = {
                'path': dotfile,
                'full_path': str(file_path),
                'managed_by': 'chezmoi',
                'file_exists': file_path.exists(),
                'last_checked': datetime.now().isoformat()
            }

            if file_path.exists():
                stat = file_path.stat()
                metadata['size'] = stat.st_size
                metadata['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()

            if not existing:
                # Create new dotfile entity
                entity_id = self.kg.insert_entity({
                    'name': dotfile,
                    'type': 'dotfile',
                    'path': dotfile,
                    'metadata': metadata
                })
                new_count += 1
                print(f"  + New dotfile: {dotfile}")
            else:
                # Update existing entity
                entity_id = existing[0]['id']
                self.kg.update_entity(entity_id, {'metadata': metadata})
                updated_count += 1

        print(f"\n✅ Sync complete: {new_count} new, {updated_count} updated")

        return {
            'total_managed': len(managed_files),
            'new_entities': new_count,
            'updated_entities': updated_count,
            'timestamp': datetime.now().isoformat()
        }

    def track_recent_changes(self, since_days: int = 7) -> Dict[str, Any]:
        """Track recent changes and create decision entities.

        Args:
            since_days: Number of days to look back

        Returns:
            Report with change counts
        """
        print(f"🔍 Tracking dotfile changes (last {since_days} days)...\n")

        changes = self.get_recent_changes(since_days)

        import uuid
        for change in changes:
            # Create decision entity for each commit
            decision_text = f"Dotfile update: {change['message']}"
            rationale = f"Modified {len(change['files'])} file(s): {', '.join(change['files'][:5])}"
            if len(change['files']) > 5:
                rationale += f" and {len(change['files']) - 5} more"

            # Log as decision entity
            self.kg.insert_entity({
                'id': str(uuid.uuid4()),
                'type': 'decision',
                'name': decision_text[:100],  # Short name
                'metadata': {
                    'decision': decision_text,
                    'rationale': rationale,
                    'tags': ['dotfile', 'chezmoi', 'configuration'],
                    'commit_hash': change['hash'],
                    'commit_timestamp': change['timestamp'],
                    'files_changed': change['files']
                }
            })

            print(f"  📝 Logged: {change['message'][:60]}")
            print(f"     Files: {len(change['files'])} changed")

        print(f"\n✅ Tracked {len(changes)} changes")

        return {
            'changes_found': len(changes),
            'since_days': since_days,
            'timestamp': datetime.now().isoformat()
        }

    def query_changes(self, since_days: int = 7) -> List[Dict[str, Any]]:
        """Query dotfile changes from knowledge graph.

        Args:
            since_days: Number of days to look back

        Returns:
            List of change records
        """
        # Search for dotfile-related decisions (using query_entities for decisions)
        decisions = self.kg.query_entities(
            type='decision',
            name_like='%dotfile%',
            limit=100
        )

        # Filter by date
        since_date = datetime.now() - timedelta(days=since_days)
        recent = []

        for decision in decisions:
            created = datetime.fromisoformat(decision['created_at'])
            if created >= since_date:
                recent.append(decision)

        return recent

    def generate_report(self, since_days: int = 7) -> str:
        """Generate human-readable report of dotfile changes.

        Args:
            since_days: Number of days to look back

        Returns:
            Formatted report text
        """
        changes = self.query_changes(since_days)

        report = f"# Dotfile Changes Report\n\n"
        report += f"**Period**: Last {since_days} days\n"
        report += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        report += "---\n\n"

        if not changes:
            report += "No dotfile changes found in this period.\n"
            return report

        report += f"## Summary\n\n"
        report += f"- Total changes: {len(changes)}\n\n"
        report += "## Changes\n\n"

        for change in sorted(changes, key=lambda x: x['created_at'], reverse=True):
            date = datetime.fromisoformat(change['created_at']).strftime('%Y-%m-%d %H:%M')
            report += f"### {date}\n\n"
            report += f"**Change**: {change['name']}\n\n"

            metadata = change.get('metadata', {})
            if 'commit_hash' in metadata:
                report += f"- Commit: `{metadata['commit_hash'][:8]}`\n"
            if 'files_changed' in metadata:
                files = metadata['files_changed']
                report += f"- Files: {', '.join(f'`{f}`' for f in files[:3])}"
                if len(files) > 3:
                    report += f" and {len(files) - 3} more"
                report += "\n"
            report += "\n"

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Dotfile watcher agent'
    )
    parser.add_argument(
        'action',
        choices=['sync', 'track', 'query', 'report'],
        help='Action to perform'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for report'
    )

    args = parser.parse_args()

    watcher = DotfileWatcher()

    if args.action == 'sync':
        report = watcher.sync_dotfiles_to_kg()
        print(f"\nTotal managed: {report['total_managed']}")

    elif args.action == 'track':
        report = watcher.track_recent_changes(since_days=args.days)
        print(f"\nTracked {report['changes_found']} changes")

    elif args.action == 'query':
        changes = watcher.query_changes(since_days=args.days)
        print(f"\nFound {len(changes)} dotfile changes in last {args.days} days:\n")
        for change in changes:
            date = datetime.fromisoformat(change['created_at']).strftime('%Y-%m-%d %H:%M')
            print(f"  • {date}: {change['name']}")

    elif args.action == 'report':
        report_text = watcher.generate_report(since_days=args.days)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(report_text)
            print(f"✅ Report written to: {output_path}")
        else:
            print(report_text)


if __name__ == '__main__':
    main()
