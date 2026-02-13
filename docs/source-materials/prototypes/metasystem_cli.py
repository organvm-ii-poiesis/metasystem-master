#!/usr/bin/env python3
"""
Unified Metasystem CLI - Central command interface
Provides a cohesive interface to all metasystem components.

Usage:
  metasystem status                    # Show system overview
  metasystem discover [--force]        # Run discovery engine
  metasystem sync [--force]            # Run synchronization
  metasystem health [--force]          # Run health check
  metasystem daemon <name> start|stop  # Control daemons
  metasystem config get|set <key>      # View/modify config
  metasystem knowledge search <query>  # Query knowledge graph
  metasystem dashboard                 # Start web dashboard
  metasystem logs <daemon>             # View daemon logs
"""

import argparse
import json
import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import time

from meta_orchestrator import MetaOrchestrator
from knowledge_graph import KnowledgeGraph


# Setup logging
log_dir = Path.home() / '.metasystem' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('MetasystemCLI')


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_status(status: Dict[str, Any], pretty: bool = True):
    """Print status with colors."""
    if not pretty:
        print(json.dumps(status, indent=2))
        return

    print(f"\n{Colors.BOLD}{Colors.CYAN}🤖 METASYSTEM STATUS{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")

    # Overall status
    running = status.get('running', False)
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if running else f"{Colors.RED}✗{Colors.RESET}"
    print(f"  Status: {status_icon} {'Running' if running else 'Stopped'}")
    print(f"  Updated: {status.get('timestamp', 'unknown')}\n")

    # Knowledge Graph
    print(f"{Colors.BOLD}Knowledge Graph:{Colors.RESET}")
    print(f"  Path: {status.get('kg_path', 'unknown')}")
    print(f"  Config: {status.get('config_path', 'unknown')}\n")

    # Daemons
    print(f"{Colors.BOLD}Daemons:{Colors.RESET}")
    daemons = status.get('daemons', {})
    for name, daemon_info in daemons.items():
        enabled = daemon_info.get('enabled', False)
        running = daemon_info.get('running', False)
        
        enabled_icon = f"{Colors.GREEN}●{Colors.RESET}" if enabled else f"{Colors.GRAY}○{Colors.RESET}"
        running_icon = f"{Colors.GREEN}◆{Colors.RESET}" if running else f"{Colors.GRAY}◇{Colors.RESET}"
        
        restarts = daemon_info.get('restart_count', 0)
        restart_info = f" ({Colors.YELLOW}{restarts} restarts{Colors.RESET})" if restarts > 0 else ""
        
        print(f"  {enabled_icon} {running_icon} {name}{restart_info}")

    # Last operations
    print(f"\n{Colors.BOLD}Last Operations:{Colors.RESET}")
    print(f"  Discovery: {status.get('last_discovery', 'never')}")
    print(f"  Sync:      {status.get('last_sync', 'never')}")
    print(f"  Health:    {status.get('last_health_check', 'never')}")

    print(f"\n{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")


def print_discovery(result: Dict[str, Any], pretty: bool = True):
    """Print discovery results."""
    if not pretty:
        print(json.dumps(result, indent=2))
        return

    status = result.get('status', 'unknown')
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status == 'success' else f"{Colors.RED}✗{Colors.RESET}"

    print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 DISCOVERY RESULTS{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
    print(f"  Status: {status_icon} {status}\n")

    if status == 'success':
        print(f"{Colors.BOLD}Found:{Colors.RESET}")
        print(f"  Projects: {Colors.BLUE}{result.get('projects_found', 0)}{Colors.RESET}")
        print(f"  Tools:    {Colors.BLUE}{result.get('tools_found', 0)}{Colors.RESET}")
        print(f"  Files:    {Colors.BLUE}{result.get('files_scanned', 0)}{Colors.RESET}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\n{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")


def print_health(result: Dict[str, Any], pretty: bool = True):
    """Print health check results."""
    if not pretty:
        print(json.dumps(result, indent=2))
        return

    status = result.get('status', 'unknown')
    overall = result.get('overall_status', 'unknown')
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status == 'success' else f"{Colors.RED}✗{Colors.RESET}"

    print(f"\n{Colors.BOLD}{Colors.CYAN}💚 HEALTH CHECK{Colors.RESET}")
    print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
    print(f"  Status: {status_icon} {overall}\n")

    if status == 'success':
        # Knowledge Graph health
        kg = result.get('knowledge_graph', {})
        print(f"{Colors.BOLD}Knowledge Graph:{Colors.RESET}")
        print(f"  Entities: {kg.get('entities', 0)}")
        print(f"  Size:     {kg.get('size_mb', 0):.2f}MB\n")

        # Disk space
        disk = result.get('disk_space', {})
        print(f"{Colors.BOLD}Disk Space:{Colors.RESET}")
        free_pct = (disk.get('free_gb', 0) / disk.get('total_gb', 1)) * 100 if disk.get('total_gb') else 0
        color = Colors.GREEN if free_pct > 20 else Colors.YELLOW if free_pct > 10 else Colors.RED
        print(f"  Free: {color}{disk.get('free_gb', 0):.1f}GB{Colors.RESET} / {disk.get('total_gb', 0):.1f}GB ({free_pct:.1f}%)\n")

        # Daemons
        print(f"{Colors.BOLD}Daemons:{Colors.RESET}")
        daemons = result.get('daemons', {})
        for name, daemon_info in daemons.items():
            running = daemon_info.get('running', False)
            icon = f"{Colors.GREEN}●{Colors.RESET}" if running else f"{Colors.RED}●{Colors.RESET}"
            print(f"  {icon} {name}")
    else:
        print(f"  Error: {result.get('error', 'Unknown error')}")

    print(f"\n{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")


def cmd_status(args):
    """Show orchestrator status."""
    orchestrator = MetaOrchestrator()
    status = orchestrator.get_status()
    print_status(status, pretty=not args.json)


def cmd_discover(args):
    """Run discovery engine."""
    orchestrator = MetaOrchestrator()
    result = orchestrator.trigger_discovery(force=args.force)
    print_discovery(result, pretty=not args.json)


def cmd_sync(args):
    """Run synchronization."""
    orchestrator = MetaOrchestrator()
    result = orchestrator.trigger_sync(force=args.force)
    
    if not args.json:
        status = result.get('status', 'unknown')
        status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status == 'success' else f"{Colors.RED}✗{Colors.RESET}"
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔄 SYNC RESULTS{Colors.RESET}")
        print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
        print(f"  Status: {status_icon} {status}\n")
        if status != 'success':
            print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"\n{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
    else:
        print(json.dumps(result, indent=2))


def cmd_health(args):
    """Run health check."""
    orchestrator = MetaOrchestrator()
    result = orchestrator.run_health_check(force=args.force)
    print_health(result, pretty=not args.json)


def cmd_daemon(args):
    """Control daemons."""
    orchestrator = MetaOrchestrator()
    
    if args.action == 'start':
        if args.daemon_name in orchestrator.daemons:
            daemon = orchestrator.daemons[args.daemon_name]
            daemon.enabled = True
            success = daemon.start()
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if success else f"{Colors.RED}✗{Colors.RESET}"
            print(f"{icon} {args.daemon_name} {'started' if success else 'failed to start'}")
        else:
            print(f"{Colors.RED}✗ Unknown daemon: {args.daemon_name}{Colors.RESET}")
            print(f"Available: {', '.join(orchestrator.daemons.keys())}")
    
    elif args.action == 'stop':
        if args.daemon_name in orchestrator.daemons:
            daemon = orchestrator.daemons[args.daemon_name]
            success = daemon.stop()
            icon = f"{Colors.GREEN}✓{Colors.RESET}" if success else f"{Colors.RED}✗{Colors.RESET}"
            print(f"{icon} {args.daemon_name} {'stopped' if success else 'failed to stop'}")
        else:
            print(f"{Colors.RED}✗ Unknown daemon: {args.daemon_name}{Colors.RESET}")
            print(f"Available: {', '.join(orchestrator.daemons.keys())}")
    
    elif args.action == 'list':
        orchestrator = MetaOrchestrator()
        status = orchestrator.get_status()
        print_status(status, pretty=not args.json)


def cmd_knowledge(args):
    """Query knowledge graph."""
    kg = KnowledgeGraph()
    
    if args.subcommand == 'search':
        results = kg.search(args.query, limit=args.limit)
        
        if not args.json:
            print(f"\n{Colors.BOLD}{Colors.CYAN}🔎 SEARCH RESULTS{Colors.RESET}")
            print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
            
            if results:
                for i, entity in enumerate(results, 1):
                    print(f"  {Colors.BLUE}{i}.{Colors.RESET} {entity.get('type')} | {entity.get('id')}")
                    if 'metadata' in entity and isinstance(entity['metadata'], dict):
                        for key, val in entity['metadata'].items():
                            print(f"     {key}: {val}")
                    print()
            else:
                print("  No results found.\n")
            
            print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
        else:
            print(json.dumps(results, indent=2))
    
    elif args.subcommand == 'stats':
        stats = kg.get_stats()
        
        if not args.json:
            print(f"\n{Colors.BOLD}{Colors.CYAN}📊 KNOWLEDGE GRAPH STATS{Colors.RESET}")
            print(f"{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
            print(f"  Entities: {stats.get('entity_count', 0)}")
            print(f"  Conversations: {stats.get('conversation_count', 0)}")
            print(f"  Size: {stats.get('db_size_mb', 0):.2f}MB")
            print(f"\n{Colors.GRAY}{'=' * 80}{Colors.RESET}\n")
        else:
            print(json.dumps(stats, indent=2))


def cmd_dashboard(args):
    """Start web dashboard."""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 Starting Metasystem Dashboard{Colors.RESET}")
    print(f"{Colors.GRAY}Opening browser at http://localhost:8888{Colors.RESET}\n")
    
    # Start the dashboard server
    dashboard_script = Path(__file__).parent / 'dashboard_server.py'
    
    try:
        # Open browser
        import webbrowser
        webbrowser.open('http://localhost:8888')
        
        # Run dashboard server
        subprocess.run([sys.executable, str(dashboard_script)])
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Dashboard stopped{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}Error starting dashboard: {e}{Colors.RESET}")


def cmd_logs(args):
    """View daemon logs."""
    log_dir = Path.home() / '.metasystem' / 'logs'
    log_file = log_dir / f'{args.daemon}.log'
    
    if not log_file.exists():
        print(f"{Colors.RED}✗ Log file not found: {log_file}{Colors.RESET}")
        return
    
    try:
        # Use 'tail -f' to follow logs
        subprocess.run(['tail', '-f', str(log_file)])
    except KeyboardInterrupt:
        print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Metasystem CLI - Unified control interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  metasystem status                  # Show system overview
  metasystem discover --force        # Force discovery run
  metasystem daemon sorting_daemon start
  metasystem knowledge search "TypeScript"
  metasystem dashboard              # Start web dashboard
        """
    )
    
    parser.add_argument('--json', action='store_true', help='Output JSON (no colors)')
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Status command
    p_status = subparsers.add_parser('status', help='Show system status')
    p_status.set_defaults(func=cmd_status)
    
    # Discovery command
    p_discover = subparsers.add_parser('discover', help='Run discovery engine')
    p_discover.add_argument('--force', action='store_true', help='Force discovery even if recent')
    p_discover.set_defaults(func=cmd_discover)
    
    # Sync command
    p_sync = subparsers.add_parser('sync', help='Run synchronization')
    p_sync.add_argument('--force', action='store_true', help='Force sync even if recent')
    p_sync.set_defaults(func=cmd_sync)
    
    # Health command
    p_health = subparsers.add_parser('health', help='Run health check')
    p_health.add_argument('--force', action='store_true', help='Force check even if recent')
    p_health.set_defaults(func=cmd_health)
    
    # Daemon command
    p_daemon = subparsers.add_parser('daemon', help='Control daemons')
    p_daemon.add_argument('daemon_name', nargs='?', help='Daemon name')
    p_daemon.add_argument('action', nargs='?', default='list', choices=['start', 'stop', 'list'],
                         help='Action to perform')
    p_daemon.set_defaults(func=cmd_daemon)
    
    # Knowledge graph command
    p_knowledge = subparsers.add_parser('knowledge', help='Query knowledge graph')
    p_knowledge_sub = p_knowledge.add_subparsers(dest='subcommand', required=True)
    
    p_kg_search = p_knowledge_sub.add_parser('search', help='Search entities')
    p_kg_search.add_argument('query', help='Search query')
    p_kg_search.add_argument('--limit', type=int, default=10, help='Result limit')
    
    p_kg_stats = p_knowledge_sub.add_parser('stats', help='Show KG statistics')
    
    p_knowledge.set_defaults(func=cmd_knowledge)
    
    # Dashboard command
    p_dashboard = subparsers.add_parser('dashboard', help='Start web dashboard')
    p_dashboard.set_defaults(func=cmd_dashboard)
    
    # Logs command
    p_logs = subparsers.add_parser('logs', help='View daemon logs')
    p_logs.add_argument('daemon', help='Daemon name (e.g., meta-orchestrator)')
    p_logs.set_defaults(func=cmd_logs)
    
    args = parser.parse_args()
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.RESET}")
        logger.exception("Command failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
