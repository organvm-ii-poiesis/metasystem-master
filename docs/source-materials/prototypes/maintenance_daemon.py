#!/usr/bin/env python3
"""
Maintenance Daemon - Orchestrates all autonomous agents

Runs on schedule to maintain system health:
- Health checks and auto-repair (Maintainer)
- Project discovery (Cataloger)
- Documentation generation (Synthesizer)

Designed to run via LaunchAgent for hands-free operation.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add agents directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.maintainer import MaintainerAgent
from agents.cataloger import CatalogerAgent
from agents.synthesizer import SynthesizerAgent
from agents.dotfile_watcher import DotfileWatcher
from sync_chezmoi import ChezmoiSync


class MaintenanceDaemon:
    """Master daemon that orchestrates all maintenance agents."""

    def __init__(self):
        self.maintainer = MaintainerAgent()
        self.cataloger = CatalogerAgent()
        self.synthesizer = SynthesizerAgent()
        self.dotfile_watcher = DotfileWatcher()
        self.chezmoi_sync = ChezmoiSync()

    def run_daily_maintenance(self):
        """Run daily maintenance tasks."""
        print("🤖 Starting daily maintenance...\n")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        print("=" * 60)

        # 1. Health checks
        print("\n📋 STEP 1: Health Checks\n")
        health_report = self.maintainer.run_health_checks(auto_repair=True)

        # 2. Discovery scan
        print("\n📋 STEP 2: Discovery Scan\n")
        discovery_report = self.cataloger.run_discovery_scan()

        # 3. Dotfile tracking
        print("\n📋 STEP 3: Dotfile Tracking\n")
        dotfile_report = self.dotfile_watcher.sync_dotfiles_to_kg()
        dotfile_changes = self.dotfile_watcher.track_recent_changes(since_days=1)

        # 3b. Sync chezmoi state (if dotfile changes detected)
        if dotfile_changes['changes_found'] > 0:
            print("\n📋 STEP 3b: Chezmoi State Sync\n")
            chezmoi_sync_result = self.chezmoi_sync.sync_all()
        else:
            chezmoi_sync_result = {'icloud': False, 'external': False}

        # 4. Documentation generation (only if changes detected)
        if (discovery_report['new_projects'] > 0 or
            discovery_report['updated_projects'] > 0 or
            health_report['repairs_made'] > 0 or
            dotfile_changes['changes_found'] > 0):

            print("\n📋 STEP 4: Documentation Update\n")
            docs_report = self.synthesizer.generate_all_docs()
        else:
            print("\n📋 STEP 4: Documentation Update\n")
            print("  ⏭️  Skipped (no changes detected)")
            docs_report = {'files_generated': []}

        # Summary
        print("\n" + "=" * 60)
        print("MAINTENANCE SUMMARY")
        print("=" * 60)
        print(f"Health: {health_report['total_issues']} issues, "
              f"{health_report['repairs_made']} repairs")
        print(f"Discovery: {discovery_report['new_projects']} new projects, "
              f"{discovery_report['new_tools']} new tools")
        print(f"Dotfiles: {dotfile_report['total_managed']} managed, "
              f"{dotfile_changes['changes_found']} changes")
        print(f"Docs: {len(docs_report['files_generated'])} files generated")
        print("=" * 60)

        return {
            'health': health_report,
            'discovery': discovery_report,
            'dotfiles': dotfile_report,
            'dotfile_changes': dotfile_changes,
            'chezmoi_sync': chezmoi_sync_result,
            'docs': docs_report
        }

    def run_hourly_tasks(self):
        """Run lightweight hourly tasks."""
        print("🤖 Running hourly tasks...\n")

        # Just health checks (no discovery/docs)
        health_report = self.maintainer.run_health_checks(auto_repair=True)

        print(f"\n✅ Hourly maintenance complete")
        print(f"   Issues: {health_report['total_issues']}, "
              f"Repairs: {health_report['repairs_made']}")

        return {'health': health_report}


def main():
    parser = argparse.ArgumentParser(description='Maintenance daemon')
    parser.add_argument('schedule', choices=['daily', 'hourly'],
                        help='Maintenance schedule')
    parser.add_argument('--log', type=str,
                        help='Write report to log file')

    args = parser.parse_args()

    daemon = MaintenanceDaemon()

    if args.schedule == 'daily':
        report = daemon.run_daily_maintenance()
    else:  # hourly
        report = daemon.run_hourly_tasks()

    # Write log if requested
    if args.log:
        log_path = Path(args.log)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, 'a') as f:
            f.write(f"\n\n{'=' * 60}\n")
            f.write(f"Maintenance Run ({args.schedule}): "
                   f"{datetime.now().isoformat()}\n")
            f.write(f"{'=' * 60}\n")

            if 'health' in report:
                f.write(f"Health: {report['health']['total_issues']} issues, "
                       f"{report['health']['repairs_made']} repairs\n")

            if 'discovery' in report:
                f.write(f"Discovery: {report['discovery']['new_projects']} new projects, "
                       f"{report['discovery']['new_tools']} new tools\n")

            if 'docs' in report:
                f.write(f"Docs: {len(report['docs']['files_generated'])} files\n")


if __name__ == '__main__':
    main()
