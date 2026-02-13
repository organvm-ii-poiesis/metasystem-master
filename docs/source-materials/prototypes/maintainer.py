#!/usr/bin/env python3
"""
Maintainer Agent - System Health Checks and Self-Repair

Monitors system health and automatically repairs issues:
- Database integrity checks
- Missing file detection
- Orphaned entity cleanup
- Broken relationship repair
- Disk space monitoring
- LaunchAgent status checks
"""

import os
import sys
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_graph import KnowledgeGraph


class HealthIssue:
    """Represents a system health issue."""

    def __init__(self, severity: str, category: str, description: str,
                 fix_action: str = None):
        self.severity = severity  # critical | warning | info
        self.category = category  # database | files | agents | disk
        self.description = description
        self.fix_action = fix_action
        self.detected_at = datetime.now()

    def __repr__(self):
        icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}[self.severity]
        return f"{icon} [{self.category}] {self.description}"


class MaintainerAgent:
    """Autonomous maintenance agent for system health."""

    def __init__(self, kg: KnowledgeGraph = None):
        self.kg = kg or KnowledgeGraph()
        self.issues: List[HealthIssue] = []
        self.repairs_made = 0

    def run_health_checks(self, auto_repair: bool = True) -> Dict[str, Any]:
        """Run all health checks and optionally auto-repair.

        Args:
            auto_repair: Automatically fix issues when possible

        Returns:
            Health report dict
        """
        print("🏥 Running system health checks...\n")

        self.issues = []
        self.repairs_made = 0

        # Run all health checks
        self._check_database_integrity()
        self._check_file_entities()
        self._check_orphaned_entities()
        self._check_disk_space()
        self._check_launchagents()
        self._check_sync_status()

        # Auto-repair if enabled
        if auto_repair:
            print("\n🔧 Attempting auto-repair...\n")
            self._auto_repair()

        # Generate report
        return self._generate_report()

    def _check_database_integrity(self):
        """Check SQLite database integrity."""
        print("Checking database integrity...")

        db_path = Path(self.kg.db_path)

        if not db_path.exists():
            self.issues.append(HealthIssue(
                "critical",
                "database",
                f"Database not found: {db_path}",
                "create_database"
            ))
            return

        try:
            with self.kg._get_conn() as conn:
                cursor = conn.cursor()

                # PRAGMA integrity_check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()

                if result and result[0] != "ok":
                    self.issues.append(HealthIssue(
                        "critical",
                        "database",
                        f"Database integrity check failed: {result[0]}",
                        "rebuild_database"
                    ))
                else:
                    print("  ✓ Database integrity: ok")

                # Check for locked database
                cursor.execute("SELECT COUNT(*) FROM entities")
                count = cursor.fetchone()[0]
                print(f"  ✓ Entities accessible: {count}")

        except sqlite3.Error as e:
            self.issues.append(HealthIssue(
                "critical",
                "database",
                f"Database error: {e}",
                "repair_database"
            ))

    def _check_file_entities(self):
        """Check if file entities still exist on disk."""
        print("\nChecking file entities...")

        file_entities = self.kg.query_entities(type='file')
        missing_count = 0
        orphaned_ids = []

        for entity in file_entities:
            file_path = Path(entity.get('path', ''))

            if not file_path.exists():
                missing_count += 1
                orphaned_ids.append(entity['id'])

                if missing_count <= 3:  # Only report first 3
                    self.issues.append(HealthIssue(
                        "warning",
                        "files",
                        f"File entity points to missing file: {file_path}",
                        f"remove_entity:{entity['id']}"
                    ))

        if missing_count > 3:
            self.issues.append(HealthIssue(
                "warning",
                "files",
                f"{missing_count - 3} more file entities point to missing files",
                f"cleanup_orphaned_files"
            ))

        if missing_count == 0:
            print(f"  ✓ All {len(file_entities)} file entities valid")
        else:
            print(f"  ⚠️  {missing_count} file entities orphaned")

    def _check_orphaned_entities(self):
        """Check for orphaned entities (no relationships)."""
        print("\nChecking for orphaned entities...")

        # This is informational - orphaned entities are okay
        # (e.g., standalone projects, files)
        # Just log for awareness

        all_entities = self.kg.query_entities()
        orphaned = []

        for entity in all_entities:
            # Check if entity has any relationships
            with self.kg._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM relationships
                    WHERE source_id = ? OR target_id = ?
                """, (entity['id'], entity['id']))
                rel_count = cursor.fetchone()[0]

                if rel_count == 0:
                    orphaned.append(entity)

        if len(orphaned) > 0:
            self.issues.append(HealthIssue(
                "info",
                "database",
                f"{len(orphaned)} entities have no relationships (may be intentional)",
                None
            ))
            print(f"  ℹ️  {len(orphaned)} orphaned entities (informational)")
        else:
            print(f"  ✓ All entities have relationships")

    def _check_disk_space(self):
        """Check available disk space."""
        print("\nChecking disk space...")

        metasystem_path = Path.home() / ".metasystem"
        stat = shutil.disk_usage(metasystem_path)

        free_gb = stat.free / (1024 ** 3)
        total_gb = stat.total / (1024 ** 3)
        used_percent = (stat.used / stat.total) * 100

        print(f"  ✓ Free space: {free_gb:.2f} GB / {total_gb:.2f} GB ({100-used_percent:.1f}% free)")

        if free_gb < 5:
            self.issues.append(HealthIssue(
                "critical",
                "disk",
                f"Low disk space: {free_gb:.2f} GB remaining",
                "cleanup_old_backups"
            ))
        elif free_gb < 20:
            self.issues.append(HealthIssue(
                "warning",
                "disk",
                f"Disk space below 20 GB: {free_gb:.2f} GB remaining",
                None
            ))

    def _check_launchagents(self):
        """Check if LaunchAgents are running."""
        print("\nChecking LaunchAgents...")

        agents = [
            "com.metasystem.sorting-daemon",
            "com.metasystem.sync-daemon"
        ]

        for agent in agents:
            plist_path = Path.home() / "Library" / "LaunchAgents" / f"{agent}.plist"

            if not plist_path.exists():
                self.issues.append(HealthIssue(
                    "warning",
                    "agents",
                    f"LaunchAgent plist missing: {agent}",
                    None
                ))
                continue

            # Check if running
            import subprocess
            result = subprocess.run(
                ["launchctl", "list"],
                capture_output=True,
                text=True
            )

            if agent in result.stdout:
                print(f"  ✓ {agent}: running")
            else:
                self.issues.append(HealthIssue(
                    "warning",
                    "agents",
                    f"LaunchAgent not running: {agent}",
                    f"restart_agent:{agent}"
                ))

    def _check_sync_status(self):
        """Check if sync is working."""
        print("\nChecking sync status...")

        local_db = Path.home() / ".metasystem" / "metastore.db"
        icloud_db = (Path.home() / "Library" / "Mobile Documents" /
                     "com~apple~CloudDocs" / ".metasystem" / "metastore.db")

        if not icloud_db.exists():
            self.issues.append(HealthIssue(
                "warning",
                "sync",
                "iCloud sync not active (database not found in iCloud)",
                None
            ))
            return

        # Compare modification times
        local_mtime = local_db.stat().st_mtime
        icloud_mtime = icloud_db.stat().st_mtime

        time_diff = abs(local_mtime - icloud_mtime)

        if time_diff > 3600:  # More than 1 hour difference
            self.issues.append(HealthIssue(
                "warning",
                "sync",
                f"Sync may be stale (last sync {time_diff/3600:.1f} hours ago)",
                "trigger_sync"
            ))
        else:
            print(f"  ✓ Sync status: recent (within {time_diff/60:.0f} minutes)")

    def _auto_repair(self):
        """Automatically repair issues where possible."""

        for issue in self.issues:
            if issue.severity == "info":
                continue  # Skip informational issues

            if not issue.fix_action:
                print(f"  - Cannot auto-repair: {issue.description}")
                continue

            try:
                if issue.fix_action.startswith("remove_entity:"):
                    entity_id = issue.fix_action.split(":")[1]
                    self._repair_remove_entity(entity_id)
                    self.repairs_made += 1

                elif issue.fix_action == "cleanup_orphaned_files":
                    self._repair_cleanup_orphaned_files()
                    self.repairs_made += 1

                elif issue.fix_action.startswith("restart_agent:"):
                    agent_name = issue.fix_action.split(":")[1]
                    self._repair_restart_agent(agent_name)
                    self.repairs_made += 1

                elif issue.fix_action == "trigger_sync":
                    self._repair_trigger_sync()
                    self.repairs_made += 1

                elif issue.fix_action == "cleanup_old_backups":
                    self._repair_cleanup_backups()
                    self.repairs_made += 1

            except Exception as e:
                print(f"  ❌ Repair failed: {e}")

    def _repair_remove_entity(self, entity_id: str):
        """Remove orphaned entity."""
        with self.kg._get_conn() as conn:
            conn.execute("DELETE FROM entities WHERE id = ?", (entity_id,))
            conn.execute("DELETE FROM entities_fts WHERE id = ?", (entity_id,))
            print(f"  ✓ Removed orphaned entity: {entity_id[:8]}...")

    def _repair_cleanup_orphaned_files(self):
        """Remove all orphaned file entities."""
        file_entities = self.kg.query_entities(type='file')
        removed = 0

        for entity in file_entities:
            file_path = Path(entity.get('path', ''))
            if not file_path.exists():
                self._repair_remove_entity(entity['id'])
                removed += 1

        print(f"  ✓ Cleaned up {removed} orphaned file entities")

    def _repair_restart_agent(self, agent_name: str):
        """Restart LaunchAgent."""
        import subprocess

        plist_path = Path.home() / "Library" / "LaunchAgents" / f"{agent_name}.plist"

        subprocess.run(
            ["launchctl", "unload", str(plist_path)],
            capture_output=True
        )
        subprocess.run(
            ["launchctl", "load", str(plist_path)],
            capture_output=True
        )

        print(f"  ✓ Restarted LaunchAgent: {agent_name}")

    def _repair_trigger_sync(self):
        """Trigger manual sync."""
        import subprocess

        subprocess.run(
            ["launchctl", "start", "com.metasystem.sync-daemon"],
            capture_output=True
        )

        print(f"  ✓ Triggered sync daemon")

    def _repair_cleanup_backups(self):
        """Clean up old backup files."""
        metasystem_path = Path.home() / ".metasystem"
        icloud_path = (Path.home() / "Library" / "Mobile Documents" /
                      "com~apple~CloudDocs" / ".metasystem")

        removed = 0
        cutoff = datetime.now() - timedelta(days=30)  # Keep last 30 days

        for path in [metasystem_path, icloud_path]:
            if not path.exists():
                continue

            for backup in path.glob("*.backup-*"):
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                if mtime < cutoff:
                    backup.unlink()
                    removed += 1

        print(f"  ✓ Cleaned up {removed} old backup files")

    def _generate_report(self) -> Dict[str, Any]:
        """Generate health report."""
        critical = [i for i in self.issues if i.severity == "critical"]
        warnings = [i for i in self.issues if i.severity == "warning"]
        info = [i for i in self.issues if i.severity == "info"]

        report = {
            'timestamp': datetime.now().isoformat(),
            'total_issues': len(self.issues),
            'critical': len(critical),
            'warnings': len(warnings),
            'info': len(info),
            'repairs_made': self.repairs_made,
            'issues': self.issues
        }

        # Print summary
        print("\n" + "=" * 60)
        print("HEALTH CHECK REPORT")
        print("=" * 60)

        if len(self.issues) == 0:
            print("✅ System is healthy! No issues detected.")
        else:
            print(f"Issues found: {len(critical)} critical, {len(warnings)} warnings, {len(info)} info")
            print()

            for issue in self.issues:
                print(f"{issue}")

        if self.repairs_made > 0:
            print(f"\n🔧 Auto-repaired {self.repairs_made} issues")

        print("=" * 60)

        return report


def main():
    import argparse

    parser = argparse.ArgumentParser(description='System health checks and auto-repair')
    parser.add_argument('--no-repair', action='store_true',
                        help='Check only, do not auto-repair')
    parser.add_argument('--log', type=str,
                        help='Write report to log file')

    args = parser.parse_args()

    maintainer = MaintainerAgent()
    report = maintainer.run_health_checks(auto_repair=not args.no_repair)

    # Write log if requested
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'a') as f:
            f.write(f"\n\n{'=' * 60}\n")
            f.write(f"Health Check: {report['timestamp']}\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Issues: {report['total_issues']} "
                   f"(critical: {report['critical']}, "
                   f"warnings: {report['warnings']}, "
                   f"info: {report['info']})\n")
            f.write(f"Repairs: {report['repairs_made']}\n")

            for issue in report['issues']:
                f.write(f"{issue}\n")

    # Exit code based on issues
    if report['critical'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
