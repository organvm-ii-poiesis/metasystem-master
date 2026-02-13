#!/usr/bin/env python3
"""
Phase 17: Terminal Monitoring Dashboard
Real-time system status monitoring in the terminal.
"""

import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

from knowledge_graph import KnowledgeGraph
from agents.metrics_collector import MetricsCollector
from agents.alerting_system import AlertingSystem

logger = logging.getLogger(__name__)


class TerminalDashboard:
    """
    Phase 17: Terminal-Based Monitoring Dashboard
    
    Displays real-time system metrics and status in terminal:
    - Sync success rates (iCloud, external)
    - Circuit breaker states
    - Agent execution times
    - Health check status
    - Recent alerts
    - System resource usage
    """
    
    def __init__(self, kg: Optional[KnowledgeGraph] = None):
        """Initialize dashboard.
        
        Args:
            kg: Knowledge graph instance
        """
        self.kg = kg or KnowledgeGraph()
        self.metrics = MetricsCollector(self.kg.db_path)
        self.alerts = AlertingSystem()
        self.running = False
    
    def print_header(self):
        """Print dashboard header."""
        print("\033[2J\033[H")  # Clear screen
        print("╔" + "═" * 78 + "╗")
        print("║" + " METASYSTEM MONITORING DASHBOARD - Phase 17                               ".ljust(79) + "║")
        print("║" + f" Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(79) + "║")
        print("╚" + "═" * 78 + "╝")
        print()
    
    def print_sync_metrics(self):
        """Print sync operation metrics."""
        print("📡 SYNC OPERATIONS")
        print("─" * 80)
        
        # iCloud metrics
        icloud_rate = self.metrics.get_success_rate('sync_icloud', hours=24)
        icloud_stats = self.metrics.get_metric_stats('sync_icloud_success', hours=24)
        icloud_status = "✅" if icloud_rate > 80 else "⚠️ " if icloud_rate > 50 else "❌"
        
        print(f"  iCloud:         {icloud_status} Success Rate: {icloud_rate:.1f}%")
        print(f"                     Attempts (24h): {icloud_stats.get('count', 0)}")
        print(f"                     Avg Duration: {icloud_stats.get('avg', 0):.2f}s")
        
        # External metrics
        external_rate = self.metrics.get_success_rate('sync_external', hours=24)
        external_stats = self.metrics.get_metric_stats('sync_external_success', hours=24)
        external_status = "✅" if external_rate > 80 else "⚠️ " if external_rate > 50 else "❌"
        
        print(f"  External:       {external_status} Success Rate: {external_rate:.1f}%")
        print(f"                     Attempts (24h): {external_stats.get('count', 0)}")
        print(f"                     Avg Duration: {external_stats.get('avg', 0):.2f}s")
        print()
    
    def print_circuit_breakers(self):
        """Print circuit breaker status."""
        print("🔌 CIRCUIT BREAKERS")
        print("─" * 80)
        
        breakers = [
            'icloud_sync',
            'external_sync',
            'database_write',
            'knowledge_graph'
        ]
        
        # Get latest breaker states
        cb_metrics = self.metrics.get_metrics('circuit_breaker_*', hours=1)
        
        # Group by breaker name
        breaker_states = {}
        for metric in cb_metrics:
            cb_name = metric['tags'].get('breaker', 'unknown')
            if cb_name not in breaker_states:
                breaker_states[cb_name] = metric
        
        for breaker in breakers:
            if breaker in breaker_states:
                metric = breaker_states[breaker]
                state = metric['tags'].get('state', 'unknown')
                failures = metric['tags'].get('failures', 0)
                
                state_icon = {
                    'closed': '🟢',
                    'open': '🔴',
                    'half_open': '🟡',
                }.get(state, '⚪')
                
                print(f"  {state_icon} {breaker:<20} State: {state:<10} Failures: {failures}")
            else:
                print(f"  ⚪ {breaker:<20} State: unknown")
        
        print()
    
    def print_agent_metrics(self):
        """Print autonomous agent metrics."""
        print("🤖 AUTONOMOUS AGENTS")
        print("─" * 80)
        
        agents = ['cataloger', 'maintainer', 'synthesizer']
        
        for agent in agents:
            stats = self.metrics.get_metric_stats(f'agent_{agent}', hours=24)
            
            if stats.get('count', 0) > 0:
                latest = stats.get('latest', 0)
                avg = stats.get('avg', 0)
                count = stats.get('count', 0)
                
                status = "✅" if latest < avg * 1.5 else "⚠️ "
                
                print(f"  {status} {agent:<15} Executions: {count:<3} Avg: {avg:.2f}s Latest: {latest:.2f}s")
            else:
                print(f"  ⚪ {agent:<15} No recent executions")
        
        print()
    
    def print_recent_alerts(self):
        """Print recent alerts."""
        print("⚠️  RECENT ALERTS")
        print("─" * 80)
        
        recent = self.alerts.get_recent_alerts(limit=5, hours=24)
        
        if not recent:
            print("  ✅ No alerts in the past 24 hours")
        else:
            for alert in recent:
                severity_icon = {
                    'info': 'ℹ️ ',
                    'warning': '⚠️ ',
                    'critical': '🔴',
                }.get(alert['severity'], '❓')
                
                time_ago = self._time_ago(alert['timestamp'])
                print(f"  {severity_icon} {alert['title']:<40} ({time_ago})")
        
        print()
    
    def print_health_status(self):
        """Print overall health status."""
        print("💚 SYSTEM HEALTH")
        print("─" * 80)
        
        # Get recent health checks
        health_checks = self.metrics.get_metrics('health_check_*', hours=1)
        
        if not health_checks:
            print("  ⚪ No recent health checks")
        else:
            # Group by check type
            check_status = {}
            for check in health_checks:
                check_type = check['tags'].get('type', 'unknown')
                status = check['tags'].get('status', 'unknown')
                
                if check_type not in check_status:
                    check_status[check_type] = status
            
            for check_type, status in sorted(check_status.items()):
                icon = {
                    'ok': '✅',
                    'warning': '⚠️ ',
                    'critical': '❌',
                }.get(status, '❓')
                
                print(f"  {icon} {check_type:<20} Status: {status}")
        
        print()
    
    def print_footer(self):
        """Print dashboard footer."""
        print("─" * 80)
        print("  Press Ctrl+C to exit | Refreshing every 10 seconds")
    
    def run(self, refresh_interval: int = 10):
        """Run dashboard with auto-refresh.
        
        Args:
            refresh_interval: Seconds between refreshes
        """
        self.running = True
        
        try:
            while self.running:
                self.print_header()
                self.print_sync_metrics()
                self.print_circuit_breakers()
                self.print_agent_metrics()
                self.print_recent_alerts()
                self.print_health_status()
                self.print_footer()
                
                time.sleep(refresh_interval)
        
        except KeyboardInterrupt:
            print("\n\n✅ Dashboard stopped")
            self.running = False
    
    # Utility Methods
    
    @staticmethod
    def _time_ago(timestamp_str: str) -> str:
        """Format timestamp as "X minutes ago".
        
        Args:
            timestamp_str: ISO format timestamp
            
        Returns:
            Human-readable time
        """
        try:
            ts = datetime.fromisoformat(timestamp_str)
            delta = datetime.now() - ts
            
            if delta.total_seconds() < 60:
                return "just now"
            elif delta.total_seconds() < 3600:
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes}m ago"
            elif delta.total_seconds() < 86400:
                hours = int(delta.total_seconds() / 3600)
                return f"{hours}h ago"
            else:
                days = int(delta.total_seconds() / 86400)
                return f"{days}d ago"
        except:
            return "unknown"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get dashboard summary as dictionary.
        
        Returns:
            Dictionary with key metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'sync': {
                'icloud_success_rate': self.metrics.get_success_rate('sync_icloud'),
                'external_success_rate': self.metrics.get_success_rate('sync_external'),
            },
            'agents': {
                'cataloger': self.metrics.get_metric_stats('agent_cataloger'),
                'maintainer': self.metrics.get_metric_stats('agent_maintainer'),
                'synthesizer': self.metrics.get_metric_stats('agent_synthesizer'),
            },
            'alerts': {
                'recent': len(self.alerts.get_recent_alerts(hours=24)),
                'critical': len(self.alerts.get_critical_alerts()),
            },
        }


def main():
    """Run monitoring dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Metasystem Monitoring Dashboard')
    parser.add_argument('--refresh', type=int, default=10, help='Refresh interval in seconds')
    parser.add_argument('--summary', action='store_true', help='Print summary and exit')
    
    args = parser.parse_args()
    
    dashboard = TerminalDashboard()
    
    if args.summary:
        summary = dashboard.get_summary()
        import json
        print(json.dumps(summary, indent=2))
    else:
        dashboard.run(refresh_interval=args.refresh)


if __name__ == '__main__':
    main()
