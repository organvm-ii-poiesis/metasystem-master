#!/usr/bin/env python3
"""
Sync Engine - Multi-Machine Synchronization

Syncs knowledge graph and metasystem data across machines using:
1. iCloud Drive (cloud backup)
2. External drive (local backup when mounted)

Conflict resolution: Newest file wins (configurable)
"""

import os
import sys
import shutil
import sqlite3
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional


class SyncEngine:
    def __init__(self, local_path: str = None, icloud_path: str = None,
                 external_path: str = None):
        """Initialize sync engine.

        Args:
            local_path: Local metasystem directory (default: ~/.metasystem)
            icloud_path: iCloud Drive sync location
            external_path: External drive sync location (when mounted)
        """
        if local_path is None:
            local_path = str(Path.home() / ".metasystem")

        if icloud_path is None:
            icloud_path = str(Path.home() / "Library" / "Mobile Documents" /
                            "com~apple~CloudDocs" / ".metasystem")

        if external_path is None:
            external_path = "/Volumes/4444-iivii/.metasystem"

        self.local_path = Path(local_path)
        self.icloud_path = Path(icloud_path)
        self.external_path = Path(external_path)

        # Files to sync
        self.sync_files = [
            "metastore.db",
            "sorting-rules.yaml",
        ]

        # Conflict resolution strategy
        self.conflict_strategy = "newest"  # newest | manual | local | remote

    def sync_all(self, direction: str = "bidirectional"):
        """Sync all locations.

        Args:
            direction: sync direction (bidirectional | push | pull)
        """
        print("🔄 Starting multi-machine sync...")

        # Ensure local directory exists
        self.local_path.mkdir(parents=True, exist_ok=True)

        results = {
            'icloud': {'status': 'skipped', 'synced': 0, 'conflicts': 0},
            'external': {'status': 'skipped', 'synced': 0, 'conflicts': 0}
        }

        # Sync to iCloud Drive
        if self._is_icloud_available():
            print("\n📱 Syncing to iCloud Drive...")
            results['icloud'] = self._sync_location(
                self.local_path,
                self.icloud_path,
                "iCloud Drive",
                direction
            )
        else:
            print("⚠️  iCloud Drive not available, skipping")

        # Sync to external drive
        if self._is_external_drive_mounted():
            print("\n💾 Syncing to external drive...")
            results['external'] = self._sync_location(
                self.local_path,
                self.external_path,
                "External Drive",
                direction
            )
        else:
            print("⚠️  External drive not mounted, skipping")

        # Summary
        print("\n✅ Sync complete!")
        print(f"   iCloud: {results['icloud']['status']} "
              f"({results['icloud']['synced']} files, "
              f"{results['icloud']['conflicts']} conflicts)")
        print(f"   External: {results['external']['status']} "
              f"({results['external']['synced']} files, "
              f"{results['external']['conflicts']} conflicts)")

        return results

    def _sync_location(self, local: Path, remote: Path, name: str,
                       direction: str) -> Dict:
        """Sync with a specific location.

        Args:
            local: Local directory
            remote: Remote directory
            name: Location name for logging
            direction: Sync direction

        Returns:
            Dict with sync results
        """
        result = {'status': 'success', 'synced': 0, 'conflicts': 0}

        # Ensure remote directory exists
        try:
            remote.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Cannot create {name} directory: {e}")
            result['status'] = 'error'
            return result

        # Sync each file
        for filename in self.sync_files:
            local_file = local / filename
            remote_file = remote / filename

            if not local_file.exists() and not remote_file.exists():
                continue  # Neither exists, skip

            try:
                sync_result = self._sync_file(local_file, remote_file, direction)

                if sync_result == 'synced':
                    result['synced'] += 1
                    print(f"  ✓ Synced {filename}")
                elif sync_result == 'conflict':
                    result['conflicts'] += 1
                    print(f"  ⚠️  Conflict resolved for {filename}")
                elif sync_result == 'skipped':
                    print(f"  - Skipped {filename} (identical)")

            except Exception as e:
                print(f"  ❌ Error syncing {filename}: {e}")
                result['status'] = 'partial'

        return result

    def _sync_file(self, local: Path, remote: Path, direction: str) -> str:
        """Sync a single file.

        Args:
            local: Local file path
            remote: Remote file path
            direction: Sync direction

        Returns:
            'synced' | 'conflict' | 'skipped' | 'error'
        """
        local_exists = local.exists()
        remote_exists = remote.exists()

        # Case 1: Only local exists → push
        if local_exists and not remote_exists:
            if direction in ['bidirectional', 'push']:
                shutil.copy2(local, remote)
                return 'synced'
            return 'skipped'

        # Case 2: Only remote exists → pull
        if remote_exists and not local_exists:
            if direction in ['bidirectional', 'pull']:
                shutil.copy2(remote, local)
                return 'synced'
            return 'skipped'

        # Case 3: Both exist → check for differences
        if local_exists and remote_exists:
            # Compare file hashes
            local_hash = self._file_hash(local)
            remote_hash = self._file_hash(remote)

            if local_hash == remote_hash:
                return 'skipped'  # Identical

            # Files differ → resolve conflict
            return self._resolve_conflict(local, remote, direction)

        return 'error'

    def _resolve_conflict(self, local: Path, remote: Path, direction: str) -> str:
        """Resolve file conflict.

        Args:
            local: Local file
            remote: Remote file
            direction: Sync direction

        Returns:
            'synced' | 'conflict'
        """
        if self.conflict_strategy == "newest":
            # Use newest file
            local_mtime = local.stat().st_mtime
            remote_mtime = remote.stat().st_mtime

            if local_mtime > remote_mtime:
                # Local is newer
                if direction in ['bidirectional', 'push']:
                    # Backup remote before overwriting
                    self._create_backup(remote)
                    shutil.copy2(local, remote)
                    return 'conflict'
            else:
                # Remote is newer
                if direction in ['bidirectional', 'pull']:
                    # Backup local before overwriting
                    self._create_backup(local)
                    shutil.copy2(remote, local)
                    return 'conflict'

        elif self.conflict_strategy == "local":
            # Always use local
            if direction in ['bidirectional', 'push']:
                self._create_backup(remote)
                shutil.copy2(local, remote)
                return 'conflict'

        elif self.conflict_strategy == "remote":
            # Always use remote
            if direction in ['bidirectional', 'pull']:
                self._create_backup(local)
                shutil.copy2(remote, local)
                return 'conflict'

        return 'synced'

    def _create_backup(self, file_path: Path):
        """Create timestamped backup of file.

        Args:
            file_path: File to backup
        """
        if not file_path.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = file_path.parent / f"{file_path.name}.backup-{timestamp}"
        shutil.copy2(file_path, backup_path)

    def _file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.

        Args:
            file_path: File to hash

        Returns:
            Hex digest of file hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def _is_icloud_available(self) -> bool:
        """Check if iCloud Drive is available.

        Returns:
            True if iCloud Drive path exists
        """
        # Check if iCloud Drive directory exists
        icloud_base = Path.home() / "Library" / "Mobile Documents" / "com~apple~CloudDocs"
        return icloud_base.exists()

    def _is_external_drive_mounted(self) -> bool:
        """Check if external drive is mounted.

        Returns:
            True if external drive is mounted
        """
        return Path("/Volumes/4444-iivii").exists()

    def status(self):
        """Show sync status for all locations."""
        print("🔍 Sync Status\n")

        print(f"Local: {self.local_path}")
        print(f"  Exists: {self.local_path.exists()}")
        if self.local_path.exists():
            for filename in self.sync_files:
                file_path = self.local_path / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"  - {filename}: {size:,} bytes, modified {mtime}")
        print()

        print(f"iCloud Drive: {self.icloud_path}")
        icloud_available = self._is_icloud_available()
        print(f"  Available: {icloud_available}")
        if icloud_available and self.icloud_path.exists():
            for filename in self.sync_files:
                file_path = self.icloud_path / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"  - {filename}: {size:,} bytes, modified {mtime}")
        print()

        print(f"External Drive: {self.external_path}")
        external_mounted = self._is_external_drive_mounted()
        print(f"  Mounted: {external_mounted}")
        if external_mounted and self.external_path.exists():
            for filename in self.sync_files:
                file_path = self.external_path / filename
                if file_path.exists():
                    size = file_path.stat().st_size
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"  - {filename}: {size:,} bytes, modified {mtime}")

    def verify_integrity(self):
        """Verify database integrity across all locations."""
        print("🔍 Verifying database integrity...\n")

        locations = [
            ('Local', self.local_path / 'metastore.db'),
            ('iCloud', self.icloud_path / 'metastore.db'),
            ('External', self.external_path / 'metastore.db')
        ]

        for name, db_path in locations:
            if not db_path.exists():
                print(f"{name}: Not found")
                continue

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Run integrity check
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]

                # Count entities
                cursor.execute("SELECT COUNT(*) FROM entities")
                entity_count = cursor.fetchone()[0]

                # Count conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                conv_count = cursor.fetchone()[0]

                conn.close()

                status = "✅" if result == "ok" else "❌"
                print(f"{name}: {status} {result}")
                print(f"  Entities: {entity_count}")
                print(f"  Conversations: {conv_count}")

            except Exception as e:
                print(f"{name}: ❌ Error - {e}")

            print()


def main():
    parser = argparse.ArgumentParser(description='Multi-machine sync for metasystem')
    parser.add_argument('command', choices=['sync', 'status', 'verify', 'push', 'pull'],
                        help='Sync command to run')
    parser.add_argument('--strategy', choices=['newest', 'local', 'remote'],
                        default='newest',
                        help='Conflict resolution strategy')

    args = parser.parse_args()

    engine = SyncEngine()
    engine.conflict_strategy = args.strategy

    if args.command == 'sync':
        engine.sync_all(direction='bidirectional')
    elif args.command == 'push':
        engine.sync_all(direction='push')
    elif args.command == 'pull':
        engine.sync_all(direction='pull')
    elif args.command == 'status':
        engine.status()
    elif args.command == 'verify':
        engine.verify_integrity()


if __name__ == '__main__':
    main()
