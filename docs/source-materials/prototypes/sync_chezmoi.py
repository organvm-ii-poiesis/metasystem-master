#!/usr/bin/env python3
"""
Chezmoi State Sync - Sync chezmoi source across machines

Syncs ~/.local/share/chezmoi (git repository) to iCloud Drive
for seamless dotfile management across machines.

Uses git for versioning and rsync for backup.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


class ChezmoiSync:
    """Sync chezmoi source directory across machines."""

    def __init__(self):
        self.chezmoi_source = Path.home() / ".local" / "share" / "chezmoi"
        self.icloud_backup = (
            Path.home() / "Library" / "Mobile Documents" /
            "com~apple~CloudDocs" / ".chezmoi-backup"
        )
        self.external_backup = Path("/Volumes/4444-iivii/.chezmoi-backup")

    def sync_to_icloud(self) -> bool:
        """Sync chezmoi source to iCloud Drive.

        Uses rsync to backup the entire directory.

        Returns:
            True if successful, False otherwise
        """
        print("📦 Syncing chezmoi to iCloud Drive...")

        if not self.chezmoi_source.exists():
            print("  ⚠️  Chezmoi source not found")
            return False

        # Ensure iCloud backup directory exists
        self.icloud_backup.mkdir(parents=True, exist_ok=True)

        try:
            # Use rsync to sync (preserves git history)
            subprocess.run([
                "rsync", "-av", "--delete",
                "--exclude", ".DS_Store",
                str(self.chezmoi_source) + "/",
                str(self.icloud_backup) + "/"
            ], check=True, capture_output=True)

            print(f"  ✓ Synced to iCloud: {self.icloud_backup}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Sync failed: {e}")
            return False

    def sync_to_external(self) -> bool:
        """Sync chezmoi source to external drive.

        Returns:
            True if successful, False otherwise
        """
        if not Path("/Volumes/4444-iivii").exists():
            print("  ⏭️  External drive not mounted (skipped)")
            return False

        print("📦 Syncing chezmoi to external drive...")

        # Ensure external backup directory exists
        self.external_backup.mkdir(parents=True, exist_ok=True)

        try:
            subprocess.run([
                "rsync", "-av", "--delete",
                "--exclude", ".DS_Store",
                str(self.chezmoi_source) + "/",
                str(self.external_backup) + "/"
            ], check=True, capture_output=True)

            print(f"  ✓ Synced to external: {self.external_backup}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Sync failed: {e}")
            return False

    def restore_from_icloud(self) -> bool:
        """Restore chezmoi source from iCloud Drive.

        Returns:
            True if successful, False otherwise
        """
        print("📥 Restoring chezmoi from iCloud Drive...")

        if not self.icloud_backup.exists():
            print("  ⚠️  iCloud backup not found")
            return False

        # Backup current local state
        if self.chezmoi_source.exists():
            backup_path = self.chezmoi_source.parent / f"chezmoi.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            subprocess.run(["mv", str(self.chezmoi_source), str(backup_path)])
            print(f"  💾 Backed up current state to: {backup_path}")

        try:
            # Restore from iCloud
            self.chezmoi_source.mkdir(parents=True, exist_ok=True)
            subprocess.run([
                "rsync", "-av",
                str(self.icloud_backup) + "/",
                str(self.chezmoi_source) + "/"
            ], check=True, capture_output=True)

            print(f"  ✓ Restored from iCloud")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Restore failed: {e}")
            return False

    def status(self) -> dict:
        """Get sync status for all locations.

        Returns:
            Status dict with sync information
        """
        status = {
            'local_exists': self.chezmoi_source.exists(),
            'icloud_exists': self.icloud_backup.exists(),
            'external_exists': self.external_backup.exists(),
            'local_files': 0,
            'icloud_files': 0,
            'external_files': 0
        }

        if status['local_exists']:
            # Count files in local chezmoi
            result = subprocess.run(
                ["find", str(self.chezmoi_source), "-type", "f"],
                capture_output=True,
                text=True
            )
            status['local_files'] = len(result.stdout.strip().split('\n'))

        if status['icloud_exists']:
            result = subprocess.run(
                ["find", str(self.icloud_backup), "-type", "f"],
                capture_output=True,
                text=True
            )
            status['icloud_files'] = len(result.stdout.strip().split('\n'))

        if status['external_exists']:
            result = subprocess.run(
                ["find", str(self.external_backup), "-type", "f"],
                capture_output=True,
                text=True
            )
            status['external_files'] = len(result.stdout.strip().split('\n'))

        return status

    def sync_all(self) -> dict:
        """Sync to all available locations.

        Returns:
            Report with sync results
        """
        print("🔄 Syncing chezmoi state to all locations...\n")

        results = {
            'icloud': self.sync_to_icloud(),
            'external': self.sync_to_external(),
            'timestamp': datetime.now().isoformat()
        }

        print(f"\n✅ Sync complete")
        print(f"   iCloud: {'✓' if results['icloud'] else '✗'}")
        print(f"   External: {'✓' if results['external'] else '⏭️ (not mounted)'}")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Chezmoi state sync')
    parser.add_argument(
        'action',
        choices=['sync', 'restore', 'status'],
        help='Action to perform'
    )

    args = parser.parse_args()

    sync = ChezmoiSync()

    if args.action == 'sync':
        sync.sync_all()
    elif args.action == 'restore':
        sync.restore_from_icloud()
    elif args.action == 'status':
        status = sync.status()
        print("📊 Chezmoi Sync Status\n")
        print(f"Local: {'✓' if status['local_exists'] else '✗'} ({status['local_files']} files)")
        print(f"iCloud: {'✓' if status['icloud_exists'] else '✗'} ({status['icloud_files']} files)")
        print(f"External: {'✓' if status['external_exists'] else '✗'} ({status['external_files']} files)")


if __name__ == '__main__':
    main()
