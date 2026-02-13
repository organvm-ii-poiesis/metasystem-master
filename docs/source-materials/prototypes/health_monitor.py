#!/usr/bin/env python3
"""
Health Monitor Daemon

Monitors system health and metasystem components.
"""

import logging
import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import os

# Setup logging
log_dir = Path.home() / '.metasystem' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('HealthMonitor')


class HealthMonitor:
    """Monitor system and component health."""

    def __init__(self):
        """Initialize health monitor."""
        self.kg_path = Path.home() / '.metasystem' / 'metastore.db'
        self.export_dir = Path.home() / 'Documents' / 'TerminalExports'
        logger.info("Health Monitor initialized")

    def check_knowledge_graph(self):
        """Check knowledge graph database health."""
        if not self.kg_path.exists():
            logger.warning("Knowledge graph database not found")
            return {'status': 'missing', 'message': 'Database file not found'}

        try:
            conn = sqlite3.connect(str(self.kg_path))
            cursor = conn.cursor()

            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()

            if result[0] != 'ok':
                logger.error(f"KG integrity check failed: {result[0]}")
                return {'status': 'error', 'message': f'Integrity check: {result[0]}'}

            # Get stats
            cursor.execute("SELECT COUNT(*) FROM entities")
            entity_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]

            conn.close()

            logger.info(f"KG health: {entity_count} entities, {conv_count} conversations")
            return {
                'status': 'healthy',
                'entities': entity_count,
                'conversations': conv_count,
                'size_mb': self.kg_path.stat().st_size / (1024 * 1024)
            }

        except Exception as e:
            logger.error(f"KG health check failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def check_disk_space(self):
        """Check disk space availability."""
        try:
            result = os.statvfs(str(Path.home()))
            free_gb = (result.f_bavail * result.f_frsize) / (1024 ** 3)
            total_gb = (result.f_blocks * result.f_frsize) / (1024 ** 3)
            used_percent = ((total_gb - free_gb) / total_gb) * 100

            status = 'healthy' if free_gb > 10 else 'warning' if free_gb > 5 else 'critical'

            if status != 'healthy':
                logger.warning(f"Low disk space: {free_gb:.1f}GB free")

            return {
                'status': status,
                'free_gb': round(free_gb, 2),
                'total_gb': round(total_gb, 2),
                'used_percent': round(used_percent, 1)
            }

        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def check_export_directory(self):
        """Check export directory health."""
        if not self.export_dir.exists():
            logger.info("Export directory doesn't exist (will be created on first export)")
            return {'status': 'not_created', 'message': 'Will be created on first use'}

        try:
            # Count exports
            exports = list(self.export_dir.rglob('*.txt'))
            total_size = sum(f.stat().st_size for f in exports)

            # Get age of newest export
            if exports:
                newest = max(exports, key=lambda f: f.stat().st_mtime)
                age_hours = (datetime.now() - datetime.fromtimestamp(newest.stat().st_mtime)).total_seconds() / 3600
            else:
                age_hours = None

            logger.info(f"Exports: {len(exports)} files, {total_size / (1024 * 1024):.2f}MB")

            return {
                'status': 'healthy',
                'exports_count': len(exports),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'newest_age_hours': round(age_hours) if age_hours else None
            }

        except Exception as e:
            logger.error(f"Export directory check failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def check_launchagents(self):
        """Check LaunchAgent status."""
        launchagents_dir = Path.home() / 'Library' / 'LaunchAgents'
        metasystem_agents = list(launchagents_dir.glob('com.metasystem*.plist'))

        status = {
            'installed_count': len(metasystem_agents),
            'agents': []
        }

        for agent_file in metasystem_agents:
            agent_name = agent_file.stem
            status['agents'].append({
                'name': agent_name,
                'file': str(agent_file),
                'exists': True
            })

        logger.info(f"Found {len(metasystem_agents)} LaunchAgents")

        return status

    def run_health_check(self):
        """Run complete health check."""
        logger.info("Starting health check")

        health = {
            'timestamp': datetime.now().isoformat(),
            'knowledge_graph': self.check_knowledge_graph(),
            'disk_space': self.check_disk_space(),
            'exports': self.check_export_directory(),
            'launchagents': self.check_launchagents()
        }

        # Determine overall status
        statuses = [
            health['knowledge_graph'].get('status'),
            health['disk_space'].get('status'),
            health['exports'].get('status')
        ]

        if 'error' in statuses or 'critical' in statuses:
            health['overall_status'] = 'unhealthy'
            logger.error("Health check revealed issues")
        elif 'warning' in statuses:
            health['overall_status'] = 'warning'
            logger.warning("Health check revealed warnings")
        else:
            health['overall_status'] = 'healthy'
            logger.info("Health check passed")

        return health

    def print_health_report(self, health):
        """Print health report in human-readable format."""
        print("\n" + "=" * 80)
        print("📊 METASYSTEM HEALTH REPORT")
        print("=" * 80)

        print(f"\nTimestamp: {health['timestamp']}")
        print(f"Overall Status: {health['overall_status'].upper()}")

        print("\n🗄️  Knowledge Graph:")
        kg = health['knowledge_graph']
        if kg['status'] == 'healthy':
            print(f"   Status: ✅ Healthy")
            print(f"   Entities: {kg['entities']}")
            print(f"   Conversations: {kg['conversations']}")
            print(f"   Size: {kg['size_mb']:.2f}MB")
        else:
            print(f"   Status: ❌ {kg['status']}")
            print(f"   Message: {kg.get('message')}")

        print("\n💾 Disk Space:")
        disk = health['disk_space']
        if disk['status'] == 'healthy':
            print(f"   Status: ✅ Healthy")
            print(f"   Free: {disk['free_gb']}GB / {disk['total_gb']}GB")
            print(f"   Used: {disk['used_percent']}%")
        elif disk['status'] == 'warning':
            print(f"   Status: ⚠️  Warning")
            print(f"   Free: {disk['free_gb']}GB (low disk space)")
        else:
            print(f"   Status: ❌ {disk['status']}")

        print("\n📁 Terminal Exports:")
        exports = health['exports']
        if exports['status'] == 'healthy':
            print(f"   Status: ✅ Healthy")
            print(f"   Exports: {exports['exports_count']}")
            print(f"   Size: {exports['total_size_mb']}MB")
            if exports['newest_age_hours']:
                print(f"   Newest: {exports['newest_age_hours']}h ago")
        elif exports['status'] == 'not_created':
            print(f"   Status: ℹ️  Not yet created")
        else:
            print(f"   Status: ❌ {exports['status']}")

        print("\n🚀 LaunchAgents:")
        agents = health['launchagents']
        print(f"   Installed: {agents['installed_count']}")
        for agent in agents['agents']:
            print(f"   • {agent['name']}")

        print("\n" + "=" * 80 + "\n")


def main():
    """CLI interface for health monitor."""
    import argparse

    parser = argparse.ArgumentParser(description='Health Monitor')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--interval', type=int, default=3600, help='Check interval in seconds')

    args = parser.parse_args()

    monitor = HealthMonitor()

    if args.check:
        health = monitor.run_health_check()
        monitor.print_health_report(health)

    elif args.daemon:
        import time
        logger.info(f"Starting health monitor daemon (interval: {args.interval}s)")

        try:
            while True:
                health = monitor.run_health_check()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Health monitor stopped")
            sys.exit(0)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
