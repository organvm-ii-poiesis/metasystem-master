#!/usr/bin/env python3
"""
Cataloger Agent - Continuous Project Discovery

Continuously scans workspace for new projects and indexes them automatically:
- Detects new seed.yaml files
- Discovers new tools/software
- Tracks file system changes
- Updates entity metadata
"""

import os
import sys
import yaml
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Set

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_graph import KnowledgeGraph
from discovery_engine import DiscoveryEngine


class CatalogerAgent:
    """Autonomous cataloging agent for continuous discovery."""

    def __init__(self, kg: KnowledgeGraph = None,
                 discovery: DiscoveryEngine = None):
        self.kg = kg or KnowledgeGraph()
        self.discovery = discovery or DiscoveryEngine()

        # Track state between runs
        self.state_file = Path.home() / ".metasystem" / "cataloger-state.json"
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load cataloger state from disk."""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)

        return {
            'last_scan': None,
            'known_projects': {},  # path -> hash
            'known_tools': set(),
            'scan_count': 0
        }

    def _save_state(self):
        """Save cataloger state to disk."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert sets to lists for JSON serialization
        state_copy = self.state.copy()
        state_copy['known_tools'] = list(state_copy['known_tools'])

        with open(self.state_file, 'w') as f:
            json.dump(state_copy, f, indent=2)

    def run_discovery_scan(self) -> Dict[str, Any]:
        """Run a full discovery scan.

        Returns:
            Report dict with discovered entities
        """
        print("🔍 Running discovery scan...\n")

        new_projects = 0
        updated_projects = 0
        new_tools = 0

        # Discover projects
        print("Scanning for projects...")
        projects = self.discovery.discover_projects(force_rescan=True)

        for project in projects:
            project_path = project['path']
            project_hash = self._hash_seed_yaml(project_path)

            if project_path not in self.state['known_projects']:
                # New project
                new_projects += 1
                print(f"  + New project: {project['name']}")
                self.state['known_projects'][project_path] = project_hash

            elif self.state['known_projects'][project_path] != project_hash:
                # Updated project
                updated_projects += 1
                print(f"  ↻ Updated project: {project['name']}")
                self.state['known_projects'][project_path] = project_hash

        # Discover tools
        print("\nScanning for tools...")
        tools = self.discovery.discover_tools()

        for tool in tools:
            tool_name = tool['name']

            if tool_name not in self.state['known_tools']:
                new_tools += 1
                print(f"  + New tool: {tool_name}")
                self.state['known_tools'].add(tool_name)

        # Update state
        self.state['last_scan'] = datetime.now().isoformat()
        self.state['scan_count'] += 1
        self._save_state()

        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'scan_count': self.state['scan_count'],
            'total_projects': len(projects),
            'new_projects': new_projects,
            'updated_projects': updated_projects,
            'total_tools': len(tools),
            'new_tools': new_tools
        }

        print("\n" + "=" * 60)
        print("DISCOVERY REPORT")
        print("=" * 60)
        print(f"Total projects: {report['total_projects']}")
        print(f"New projects: {report['new_projects']}")
        print(f"Updated projects: {report['updated_projects']}")
        print(f"Total tools: {report['total_tools']}")
        print(f"New tools: {report['new_tools']}")
        print("=" * 60)

        return report

    def watch_for_changes(self, interval: int = 300):
        """Continuously watch for changes.

        Args:
            interval: Seconds between scans (default: 5 minutes)
        """
        import time

        print(f"👁️  Watching for changes (scanning every {interval}s)...")
        print("Press Ctrl+C to stop\n")

        try:
            while True:
                report = self.run_discovery_scan()

                if report['new_projects'] > 0 or report['updated_projects'] > 0:
                    print(f"\n✨ Discovered changes! "
                          f"{report['new_projects']} new, "
                          f"{report['updated_projects']} updated\n")

                print(f"\nNext scan in {interval}s...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n👋 Stopped watching")

    def _hash_seed_yaml(self, project_path: str) -> str:
        """Calculate hash of seed.yaml file.

        Args:
            project_path: Path to project directory

        Returns:
            SHA256 hash of seed.yaml
        """
        seed_file = Path(project_path) / "seed.yaml"

        if not seed_file.exists():
            return ""

        with open(seed_file, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Continuous project discovery')
    parser.add_argument('command', choices=['scan', 'watch'],
                        help='Run single scan or watch for changes')
    parser.add_argument('--interval', type=int, default=300,
                        help='Watch interval in seconds (default: 300)')
    parser.add_argument('--log', type=str,
                        help='Write report to log file')

    args = parser.parse_args()

    cataloger = CatalogerAgent()

    if args.command == 'scan':
        report = cataloger.run_discovery_scan()

        # Write log if requested
        if args.log:
            log_path = Path(args.log)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a') as f:
                f.write(f"\n\n{'=' * 60}\n")
                f.write(f"Discovery Scan: {report['timestamp']}\n")
                f.write(f"{'=' * 60}\n")
                f.write(f"Total projects: {report['total_projects']}\n")
                f.write(f"New projects: {report['new_projects']}\n")
                f.write(f"Updated projects: {report['updated_projects']}\n")
                f.write(f"Total tools: {report['total_tools']}\n")
                f.write(f"New tools: {report['new_tools']}\n")

    elif args.command == 'watch':
        cataloger.watch_for_changes(interval=args.interval)


if __name__ == '__main__':
    main()
