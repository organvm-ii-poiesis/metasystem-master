#!/usr/bin/env python3
"""
Discovery Engine - Auto-discovers projects, files, and tools

Scans workspace for projects (via seed.yaml), indexes files, discovers
installed tools. Keeps knowledge graph current without manual intervention.

Critical for auto-cataloging and zero-maintenance operation.
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

# Import knowledge graph
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_graph import KnowledgeGraph


class DiscoveryEngine:
    """Auto-discovers and indexes system entities."""

    def __init__(self, kg_path: str = None):
        """Initialize discovery engine.

        Args:
            kg_path: Path to knowledge graph database
        """
        self.kg = KnowledgeGraph(kg_path)
        self.workspace_root = Path.home() / "Workspace"

    def discover_projects(self, force_rescan: bool = False) -> List[Dict[str, Any]]:
        """Discover projects in workspace via seed.yaml files.

        Args:
            force_rescan: Re-index even if project already exists

        Returns:
            List of discovered project entities
        """
        print(f"🔍 Scanning workspace for projects: {self.workspace_root}")

        if not self.workspace_root.exists():
            print(f"⚠️  Workspace not found: {self.workspace_root}")
            return []

        discovered = []

        # Find all seed.yaml files in workspace
        for seed_file in self.workspace_root.rglob("seed.yaml"):
            try:
                project_dir = seed_file.parent
                project_name = project_dir.name

                # Skip if already indexed (unless force_rescan)
                if not force_rescan:
                    existing = self.kg.query_entities(
                        type='project',
                        path_like=f"%{project_dir}%"
                    )
                    if existing:
                        print(f"  ⏭️  {project_name} (already indexed)")
                        continue

                # Parse seed.yaml
                import yaml
                with open(seed_file) as f:
                    seed_data = yaml.safe_load(f)

                # Create project entity
                project = seed_data.get('project', {})
                arch = seed_data.get('architecture', {})

                entity = {
                    'id': str(uuid.uuid4()),
                    'type': 'project',
                    'path': str(project_dir),
                    'name': project.get('name', project_name),
                    'metadata': {
                        'description': project.get('description', ''),
                        'category': project.get('category', ''),
                        'created': project.get('created', ''),
                        'tech_stack': arch.get('tech_stack', {}),
                        'seed_path': str(seed_file),
                        'components': arch.get('components', []),
                        'dependencies': seed_data.get('dependencies', {}),
                        'priority': seed_data.get('metadata', {}).get('priority', 'normal')
                    }
                }

                entity_id = self.kg.insert_entity(entity)

                # Add facts about project
                if arch.get('tech_stack'):
                    tech_stack = arch['tech_stack']
                    if 'language' in tech_stack:
                        self.kg.add_fact(
                            entity_id,
                            'language',
                            tech_stack['language'],
                            'seed-yaml',
                            confidence=1.0
                        )

                discovered.append(entity)
                print(f"  ✅ {project.get('name', project_name)} ({entity_id[:8]})")

            except Exception as e:
                print(f"  ❌ Error processing {seed_file}: {e}")

        print(f"\n📊 Discovered {len(discovered)} new projects")
        return discovered

    def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover installed tools (Homebrew, npm, pipx, etc.).

        Returns:
            List of discovered tool entities
        """
        print("🔍 Discovering installed tools...")

        discovered = []

        # Homebrew packages
        try:
            result = subprocess.run(
                ['brew', 'list', '--formula'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                packages = result.stdout.strip().split('\n')
                print(f"  Found {len(packages)} Homebrew formulae")

                # Sample a few for indexing (avoid overwhelming database)
                for package in packages[:50]:  # Index first 50
                    entity = {
                        'id': str(uuid.uuid4()),
                        'type': 'tool',
                        'name': package,
                        'path': f"/opt/homebrew/Cellar/{package}",
                        'metadata': {
                            'package_manager': 'homebrew',
                            'category': 'formula'
                        }
                    }

                    self.kg.insert_entity(entity)
                    discovered.append(entity)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("  ⚠️  Homebrew not available")

        # npm global packages
        try:
            result = subprocess.run(
                ['npm', 'list', '-g', '--depth=0', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                npm_data = json.loads(result.stdout)
                deps = npm_data.get('dependencies', {})
                print(f"  Found {len(deps)} npm global packages")

                for package, info in list(deps.items())[:20]:  # Index first 20
                    entity = {
                        'id': str(uuid.uuid4()),
                        'type': 'tool',
                        'name': package,
                        'metadata': {
                            'package_manager': 'npm',
                            'version': info.get('version', '')
                        }
                    }

                    self.kg.insert_entity(entity)
                    discovered.append(entity)

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            print("  ⚠️  npm not available")

        print(f"📊 Discovered {len(discovered)} tools")
        return discovered

    def discover_files(self, directory: Path = None, max_files: int = 1000) -> List[Dict[str, Any]]:
        """Discover and index files in a directory.

        Args:
            directory: Directory to scan (defaults to ~/Downloads)
            max_files: Maximum files to index

        Returns:
            List of discovered file entities
        """
        if directory is None:
            directory = Path.home() / "Downloads"

        print(f"🔍 Scanning files in: {directory}")

        if not directory.exists():
            print(f"⚠️  Directory not found: {directory}")
            return []

        discovered = []
        count = 0

        for file_path in directory.rglob("*"):
            if count >= max_files:
                break

            if not file_path.is_file():
                continue

            try:
                stat = file_path.stat()

                entity = {
                    'id': str(uuid.uuid4()),
                    'type': 'file',
                    'path': str(file_path),
                    'name': file_path.name,
                    'metadata': {
                        'size': stat.st_size,
                        'extension': file_path.suffix,
                        'directory': str(file_path.parent),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                }

                entity_id = self.kg.insert_entity(entity)

                # Add facts
                self.kg.add_fact(entity_id, 'file_size', str(stat.st_size), 'filesystem')

                discovered.append(entity)
                count += 1

            except (OSError, PermissionError):
                continue

        print(f"📊 Discovered {len(discovered)} files")
        return discovered

    def scan_workspace(self, full: bool = False):
        """Full workspace scan - projects, tools, files.

        Args:
            full: If True, includes files (slower)
        """
        print("=" * 60)
        print("🔍 METASYSTEM DISCOVERY ENGINE")
        print("=" * 60)
        print()

        # Always discover projects
        projects = self.discover_projects()

        # Discover tools
        tools = self.discover_tools()

        # Optionally discover files (slower)
        files = []
        if full:
            files = self.discover_files()

        print()
        print("=" * 60)
        print("✅ DISCOVERY COMPLETE")
        print("=" * 60)
        print(f"  Projects: {len(projects)}")
        print(f"  Tools: {len(tools)}")
        print(f"  Files: {len(files)}")
        print()

        # Print stats
        stats = self.kg.get_stats()
        print(f"📊 Knowledge Graph Statistics:")
        print(f"  Total entities: {stats['total_entities']}")
        print(f"  Database size: {stats['db_size_mb']} MB")
        print()

    def continuous_discover(self, interval_seconds: int = 300):
        """Continuously discover and update knowledge graph.

        Args:
            interval_seconds: Seconds between scans (default: 5 minutes)
        """
        import time

        print(f"🔄 Starting continuous discovery (every {interval_seconds}s)")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                self.scan_workspace(full=False)
                print(f"💤 Sleeping for {interval_seconds} seconds...")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n✅ Stopped continuous discovery")


def main():
    """CLI for discovery engine."""
    import argparse

    parser = argparse.ArgumentParser(description='Metasystem Discovery Engine')
    parser.add_argument('command', choices=['scan', 'projects', 'tools', 'files', 'daemon'],
                       help='Discovery command')
    parser.add_argument('--full', action='store_true',
                       help='Full scan including files (slower)')
    parser.add_argument('--directory', type=str,
                       help='Directory to scan for files')
    parser.add_argument('--interval', type=int, default=300,
                       help='Interval in seconds for daemon mode')

    args = parser.parse_args()

    engine = DiscoveryEngine()

    if args.command == 'scan':
        engine.scan_workspace(full=args.full)

    elif args.command == 'projects':
        projects = engine.discover_projects(force_rescan=True)
        print(json.dumps([p['name'] for p in projects], indent=2))

    elif args.command == 'tools':
        tools = engine.discover_tools()
        print(json.dumps([t['name'] for t in tools], indent=2))

    elif args.command == 'files':
        directory = Path(args.directory) if args.directory else None
        files = engine.discover_files(directory=directory)
        print(json.dumps([f['path'] for f in files][:20], indent=2))

    elif args.command == 'daemon':
        engine.continuous_discover(interval_seconds=args.interval)


if __name__ == '__main__':
    main()
