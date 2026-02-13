#!/usr/bin/env python3
"""
Meta-Orchestrator - Central Daemon Coordinator

Coordinates all metasystem daemons and components:
- Knowledge Graph management
- Discovery Engine (auto-discovery)
- Sorting Daemon (file organization)
- Sync Engine (multi-machine sync)
- Terminal Monitor (session export)
- Health monitoring

This is the central "brain" of the metasystem - all other components
report to and are coordinated by this orchestrator.
"""

import logging
import sys
import json
import signal
import time
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import argparse

from knowledge_graph import KnowledgeGraph
from discovery_engine import DiscoveryEngine
from context_manager import ConversationManager
from health_monitor import HealthMonitor

# Optional: Import MFM integration for clipboard sync
try:
    from mfm_integration import MFMIntegration
    HAS_MFM_INTEGRATION = True
except ImportError:
    HAS_MFM_INTEGRATION = False

# Optional: Import Phase 13 & 14 agents (self-maintaining agents)
try:
    from agents.cataloger import CatalogerAgent
    from agents.maintainer import MaintainerAgent
    from agents.synthesizer import SynthesizerAgent
    HAS_AUTONOMOUS_AGENTS = True
except ImportError:
    HAS_AUTONOMOUS_AGENTS = False

# Optional: Import Phase 15 & 16 agents (multi-machine sync & resilience)
try:
    from agents.resilience import ResilienceAgent
    HAS_RESILIENCE_AGENT = True
except ImportError:
    HAS_RESILIENCE_AGENT = False


# Setup logging
log_dir = Path.home() / '.metasystem' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'meta_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('MetaOrchestrator')


class DaemonProcess:
    """Wrapper for managing a daemon subprocess."""

    def __init__(self, name: str, cmd: List[str], enabled: bool = True):
        """Initialize daemon process wrapper.
        
        Args:
            name: Name of daemon
            cmd: Command to run as list (e.g., ['python3', 'sorting_daemon.py'])
            enabled: Whether daemon should be started
        """
        self.name = name
        self.cmd = cmd
        self.enabled = enabled
        self.process = None
        self.last_start = None
        self.restart_count = 0

    def start(self) -> bool:
        """Start the daemon process."""
        if not self.enabled:
            logger.info(f"[{self.name}] Daemon is disabled, skipping start")
            return False

        try:
            logger.info(f"[{self.name}] Starting daemon...")
            self.process = subprocess.Popen(
                self.cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            self.last_start = datetime.now()
            logger.info(f"[{self.name}] Started with PID {self.process.pid}")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to start: {e}")
            return False

    def stop(self) -> bool:
        """Stop the daemon process."""
        if self.process is None:
            return False

        try:
            logger.info(f"[{self.name}] Stopping daemon...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"[{self.name}] Didn't stop gracefully, killing...")
                self.process.kill()
            logger.info(f"[{self.name}] Stopped")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to stop: {e}")
            return False

    def is_running(self) -> bool:
        """Check if daemon process is still running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def check_and_restart(self) -> bool:
        """Check if process crashed and restart if needed."""
        if not self.enabled:
            return False

        if not self.is_running():
            self.restart_count += 1
            logger.warning(f"[{self.name}] Process died, restarting (attempt {self.restart_count})")
            
            # Exponential backoff: 1s, 2s, 4s, 8s, then cap at 30s
            backoff = min(2 ** (self.restart_count - 1), 30)
            time.sleep(backoff)
            
            return self.start()

        # Reset restart count if process has been running for >1 hour
        if self.last_start and (datetime.now() - self.last_start) > timedelta(hours=1):
            self.restart_count = 0

        return True


class MetaOrchestrator:
    """Central orchestrator coordinating all metasystem components."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize orchestrator.
        
        Args:
            config_path: Path to configuration file
        """
        self.kg = KnowledgeGraph()
        self.discovery = DiscoveryEngine(self.kg.db_path)
        self.context_mgr = ConversationManager(self.kg.db_path)
        self.health = HealthMonitor()
        
        self.config_path = Path(config_path) if config_path else (
            Path.home() / '.metasystem' / 'metasystem.yaml'
        )
        self.config = self._load_config()
        
        # Daemon processes managed by this orchestrator
        self.daemons: Dict[str, DaemonProcess] = {}
        self._setup_daemons()
        
        self.running = False
        self.last_discovery = None
        self.last_sync = None
        self.last_health_check = None
        self.last_clipboard_sync = None  # NEW
        
        # Phase 13 & 14: Autonomous agent tracking
        self.last_cataloger_scan = None
        self.last_maintainer_check = None
        self.last_docs_generation = None
        
        # Phase 15 & 16: Resilience agent tracking
        self.last_resilience_check = None
        
        # Initialize MFM integration if available
        self.mfm = MFMIntegration() if HAS_MFM_INTEGRATION else None
        
        # Initialize autonomous agents if available
        self.cataloger = CatalogerAgent(self.kg) if HAS_AUTONOMOUS_AGENTS else None
        self.maintainer = MaintainerAgent(self.kg) if HAS_AUTONOMOUS_AGENTS else None
        self.synthesizer = SynthesizerAgent(self.kg) if HAS_AUTONOMOUS_AGENTS else None
        
        # Phase 15 & 16: Initialize resilience agent if available
        self.resilience = ResilienceAgent(self.kg) if HAS_RESILIENCE_AGENT else None

        logger.info("MetaOrchestrator initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            return self._default_config()

        try:
            import yaml
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'orchestrator': {
                'discovery_interval': 300,  # 5 minutes
                'sync_interval': 600,       # 10 minutes
                'health_check_interval': 300,  # 5 minutes
                'clipboard_sync_interval': 600,  # 10 minutes
                'cataloger_scan_interval': 1800,  # 30 minutes (Phase 13)
                'maintainer_check_interval': 3600,  # 1 hour (Phase 13)
                'docs_generation_interval': 86400,  # 1 day (Phase 14)
                'resilience_check_interval': 1800,  # 30 minutes (Phase 16)
                'log_level': 'INFO'
            },
            'daemons': {
                'sorting': {'enabled': True},
                'terminal_monitor': {'enabled': True},
                'health_monitor': {'enabled': False},  # Manual for now
                'documentation': {'enabled': False}    # On-demand
            }
        }

    def _setup_daemons(self):
        """Set up daemon process wrappers."""
        metasystem_dir = Path(__file__).parent
        
        daemons = [
            ('sorting_daemon', [
                sys.executable,
                str(metasystem_dir / 'sorting_daemon.py'),
                '--daemon'
            ]),
            ('terminal_monitor', [
                sys.executable,
                str(metasystem_dir / 'terminal_monitor.py'),
                '--start'
            ]),
            ('health_monitor', [
                sys.executable,
                str(metasystem_dir / 'health_monitor.py'),
                '--daemon'
            ]),
            ('documentation', [
                sys.executable,
                str(metasystem_dir / 'documentation_generator.py'),
                '--daemon'
            ])
        ]

        # Create daemon wrappers with enabled status from config
        for name, cmd in daemons:
            enabled = self.config.get('daemons', {}).get(name, {}).get('enabled', False)
            self.daemons[name] = DaemonProcess(name, cmd, enabled=enabled)
            logger.info(f"[{name}] Configured (enabled={enabled})")

    def start_all_daemons(self) -> Dict[str, bool]:
        """Start all enabled daemons."""
        results = {}
        for name, daemon in self.daemons.items():
            results[name] = daemon.start()
        return results

    def stop_all_daemons(self) -> Dict[str, bool]:
        """Stop all running daemons."""
        results = {}
        for name, daemon in self.daemons.items():
            results[name] = daemon.stop()
        return results

    def check_daemon_health(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all daemons."""
        status = {}
        for name, daemon in self.daemons.items():
            status[name] = {
                'enabled': daemon.enabled,
                'running': daemon.is_running(),
                'last_start': daemon.last_start.isoformat() if daemon.last_start else None,
                'restart_count': daemon.restart_count
            }
        return status

    def trigger_discovery(self, force: bool = False) -> Dict[str, Any]:
        """Trigger discovery engine to scan for new projects/files.
        
        Args:
            force: Force discovery even if recently run
            
        Returns:
            Discovery results
        """
        if not force:
            if self.last_discovery and (datetime.now() - self.last_discovery) < timedelta(seconds=60):
                logger.info("Discovery ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running discovery engine...")
            
            # Run all discovery scans
            projects = self.discovery.discover_projects()
            tools = self.discovery.discover_tools()
            files = self.discovery.scan_workspace()
            
            results = {
                'projects_found': len(projects),
                'tools_found': len(tools),
                'files_scanned': len(files) if files else 0
            }
            
            self.last_discovery = datetime.now()
            
            logger.info(f"Discovery found: {results['projects_found']} projects, {results['tools_found']} tools")
            
            # Log discovery event to knowledge graph
            self.kg.insert_entity({
                'id': f"discovery_{datetime.now().timestamp()}",
                'type': 'discovery_event',
                'metadata': results,
                'created_at': datetime.now().isoformat()
            })
            
            return {'status': 'success', **results}
        except Exception as e:
            logger.error(f"Discovery failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def trigger_sync(self, force: bool = False) -> Dict[str, Any]:
        """Trigger synchronization engine.
        
        Args:
            force: Force sync even if recently run
            
        Returns:
            Sync results
        """
        if not force:
            if self.last_sync and (datetime.now() - self.last_sync) < timedelta(seconds=60):
                logger.info("Sync ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Triggering synchronization...")
            # Import sync engine dynamically to avoid import errors if not available
            from sync_engine import SyncEngine
            sync = SyncEngine()
            results = sync.sync_all()
            self.last_sync = datetime.now()
            
            # Log sync to KG
            self.kg.insert_entity({
                'id': f"sync_event_{datetime.now().timestamp()}",
                'type': 'sync_event',
                'metadata': {
                    'icloud_status': results.get('icloud', {}).get('status', 'unknown'),
                    'external_status': results.get('external', {}).get('status', 'unknown'),
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            logger.info(f"Sync completed: {results}")
            return {'status': 'success', **results}
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            # Log sync failure to KG
            self.kg.insert_entity({
                'id': f"sync_error_{datetime.now().timestamp()}",
                'type': 'sync_error',
                'metadata': {
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
            })
            return {'status': 'error', 'error': str(e)}

    def trigger_clipboard_sync(self, force: bool = False) -> Dict[str, Any]:
        """Trigger clipboard synchronization to knowledge graph.
        
        Args:
            force: Force sync even if recently run
            
        Returns:
            Sync results
        """
        if not self.mfm:
            return {'status': 'skipped', 'reason': 'mfm_integration_not_available'}
        
        if not force:
            if self.last_clipboard_sync and (datetime.now() - self.last_clipboard_sync) < timedelta(seconds=60):
                logger.info("Clipboard sync ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Syncing clipboard to knowledge graph...")
            result = self.mfm.sync_bidirectional()
            self.last_clipboard_sync = datetime.now()
            
            logger.info(f"Clipboard sync completed: {result}")
            
            # Log sync event to knowledge graph
            self.kg.insert_entity({
                'id': f"clipboard_sync_{datetime.now().timestamp()}",
                'type': 'sync_event',
                'metadata': {
                    **result,
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            return {'status': 'success', **result}
        except Exception as e:
            logger.error(f"Clipboard sync failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_health_check(self, force: bool = False) -> Dict[str, Any]:
        """Run system health check.
        
        Args:
            force: Force check even if recently run
            
        Returns:
            Health check results
        """
        if not force:
            if self.last_health_check and (datetime.now() - self.last_health_check) < timedelta(seconds=60):
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running health check...")
            health = self.health.run_health_check()
            
            # Add daemon health
            health['daemons'] = self.check_daemon_health()
            
            self.last_health_check = datetime.now()
            
            # Log health check to KG
            self.kg.insert_entity({
                'id': f"health_check_{datetime.now().timestamp()}",
                'type': 'health_event',
                'metadata': health,
                'created_at': datetime.now().isoformat()
            })
            
            return {'status': 'success', **health}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_cataloger_scan(self, force: bool = False) -> Dict[str, Any]:
        """Run cataloger agent discovery scan (Phase 13).
        
        Args:
            force: Force scan even if recently run
            
        Returns:
            Scan results
        """
        if not self.cataloger:
            return {'status': 'skipped', 'reason': 'cataloger_agent_not_available'}
        
        if not force:
            if self.last_cataloger_scan and (datetime.now() - self.last_cataloger_scan) < timedelta(seconds=60):
                logger.info("Cataloger scan ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running cataloger agent discovery scan...")
            report = self.cataloger.run_discovery_scan()
            self.last_cataloger_scan = datetime.now()
            
            # Log to KG
            self.kg.insert_entity({
                'id': f"cataloger_scan_{datetime.now().timestamp()}",
                'type': 'discovery_agent_event',
                'metadata': report,
                'created_at': datetime.now().isoformat()
            })
            
            logger.info(f"Cataloger scan completed: {report['total_projects']} projects, {report['total_tools']} tools")
            return {'status': 'success', **report}
        except Exception as e:
            logger.error(f"Cataloger scan failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_maintainer_check(self, force: bool = False) -> Dict[str, Any]:
        """Run maintainer agent health checks with auto-repair (Phase 13).
        
        Args:
            force: Force check even if recently run
            
        Returns:
            Health check results
        """
        if not self.maintainer:
            return {'status': 'skipped', 'reason': 'maintainer_agent_not_available'}
        
        if not force:
            if self.last_maintainer_check and (datetime.now() - self.last_maintainer_check) < timedelta(seconds=60):
                logger.info("Maintainer check ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running maintainer agent health checks...")
            report = self.maintainer.run_health_checks(auto_repair=True)
            self.last_maintainer_check = datetime.now()
            
            # Log to KG
            self.kg.insert_entity({
                'id': f"maintainer_check_{datetime.now().timestamp()}",
                'type': 'health_agent_event',
                'metadata': {
                    'total_issues': report['total_issues'],
                    'critical': report['critical'],
                    'warnings': report['warnings'],
                    'repairs_made': report['repairs_made'],
                    'timestamp': datetime.now().isoformat()
                }
            })
            
            logger.info(f"Maintainer check completed: {report['repairs_made']} repairs made")
            return {'status': 'success', **report}
        except Exception as e:
            logger.error(f"Maintainer check failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_docs_generation(self, force: bool = False) -> Dict[str, Any]:
        """Run synthesizer agent documentation generation (Phase 14).
        
        Args:
            force: Force generation even if recently run
            
        Returns:
            Generation results
        """
        if not self.synthesizer:
            return {'status': 'skipped', 'reason': 'synthesizer_agent_not_available'}
        
        if not force:
            if self.last_docs_generation and (datetime.now() - self.last_docs_generation) < timedelta(seconds=60):
                logger.info("Documentation generation ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running synthesizer agent documentation generation...")
            report = self.synthesizer.generate_all_docs()
            self.last_docs_generation = datetime.now()
            
            # Log to KG
            self.kg.insert_entity({
                'id': f"docs_generation_{datetime.now().timestamp()}",
                'type': 'synthesizer_agent_event',
                'metadata': report,
                'created_at': datetime.now().isoformat()
            })
            
            logger.info(f"Documentation generation completed: {len(report['files_generated'])} files generated")
            return {'status': 'success', **report}
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def run_resilience_check(self, force: bool = False) -> Dict[str, Any]:
        """Run resilience agent health checks and recovery (Phase 16).
        
        Args:
            force: Force check even if recently run
            
        Returns:
            Resilience check results
        """
        if not self.resilience:
            return {'status': 'skipped', 'reason': 'resilience_agent_not_available'}
        
        if not force:
            if self.last_resilience_check and (datetime.now() - self.last_resilience_check) < timedelta(seconds=60):
                logger.info("Resilience check ran recently, skipping")
                return {'status': 'skipped', 'reason': 'ran_recently'}

        try:
            logger.info("Running resilience agent checks...")
            report = self.resilience.work()
            self.last_resilience_check = datetime.now()
            
            # Sync circuit breaker status to KG (for monitoring)
            sync_health = self.resilience.check_sync_health()
            
            logger.info(f"Resilience check completed: {report['recoveries_attempted']} recovery attempts, {report['issues_resolved']} issues resolved")
            return {'status': 'success', **report, 'sync_health': sync_health}
        except Exception as e:
            logger.error(f"Resilience check failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            'timestamp': datetime.now().isoformat(),
            'running': self.running,
            'daemons': self.check_daemon_health(),
            'kg_path': self.kg.db_path,
            'config_path': str(self.config_path),
            'last_discovery': self.last_discovery.isoformat() if self.last_discovery else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None,
            'last_clipboard_sync': self.last_clipboard_sync.isoformat() if self.last_clipboard_sync else None,
            'mfm_integration': 'available' if self.mfm else 'unavailable',
            'autonomous_agents': {
                'available': HAS_AUTONOMOUS_AGENTS,
                'last_cataloger_scan': self.last_cataloger_scan.isoformat() if self.last_cataloger_scan else None,
                'last_maintainer_check': self.last_maintainer_check.isoformat() if self.last_maintainer_check else None,
                'last_docs_generation': self.last_docs_generation.isoformat() if self.last_docs_generation else None
            },
            'resilience_agent': {
                'available': HAS_RESILIENCE_AGENT,
                'last_resilience_check': self.last_resilience_check.isoformat() if self.last_resilience_check else None
            }
        }

    def daemon_loop(self):
        """Main orchestrator loop."""
        logger.info("Starting orchestrator daemon loop")
        self.running = True

        discovery_interval = self.config.get('orchestrator', {}).get('discovery_interval', 300)
        sync_interval = self.config.get('orchestrator', {}).get('sync_interval', 600)
        health_interval = self.config.get('orchestrator', {}).get('health_check_interval', 300)
        clipboard_sync_interval = self.config.get('orchestrator', {}).get('clipboard_sync_interval', 600)
        
        # Phase 13 & 14: Agent intervals
        cataloger_scan_interval = self.config.get('orchestrator', {}).get('cataloger_scan_interval', 1800)
        maintainer_check_interval = self.config.get('orchestrator', {}).get('maintainer_check_interval', 3600)
        docs_generation_interval = self.config.get('orchestrator', {}).get('docs_generation_interval', 86400)
        
        # Phase 15 & 16: Resilience interval
        resilience_check_interval = self.config.get('orchestrator', {}).get('resilience_check_interval', 1800)

        next_discovery = datetime.now() + timedelta(seconds=discovery_interval)
        next_sync = datetime.now() + timedelta(seconds=sync_interval)
        next_health = datetime.now() + timedelta(seconds=health_interval)
        next_clipboard_sync = datetime.now() + timedelta(seconds=clipboard_sync_interval)
        
        # Phase 13 & 14: Next agent run times
        next_cataloger_scan = datetime.now() + timedelta(seconds=cataloger_scan_interval)
        next_maintainer_check = datetime.now() + timedelta(seconds=maintainer_check_interval)
        next_docs_generation = datetime.now() + timedelta(seconds=docs_generation_interval)
        
        # Phase 15 & 16: Next resilience check time
        next_resilience_check = datetime.now() + timedelta(seconds=resilience_check_interval)

        try:
            while self.running:
                now = datetime.now()

                # Check daemon health every 30 seconds
                for daemon in self.daemons.values():
                    daemon.check_and_restart()

                # Trigger discovery if due
                if now >= next_discovery:
                    self.trigger_discovery()
                    next_discovery = now + timedelta(seconds=discovery_interval)

                # Trigger sync if due
                if now >= next_sync:
                    self.trigger_sync()
                    next_sync = now + timedelta(seconds=sync_interval)

                # Run health check if due
                if now >= next_health:
                    self.run_health_check()
                    next_health = now + timedelta(seconds=health_interval)

                # Sync clipboard if due
                if now >= next_clipboard_sync:
                    self.trigger_clipboard_sync()
                    next_clipboard_sync = now + timedelta(seconds=clipboard_sync_interval)

                # Phase 13 & 14: Run autonomous agents on schedule
                if now >= next_cataloger_scan:
                    self.run_cataloger_scan()
                    next_cataloger_scan = now + timedelta(seconds=cataloger_scan_interval)

                if now >= next_maintainer_check:
                    self.run_maintainer_check()
                    next_maintainer_check = now + timedelta(seconds=maintainer_check_interval)

                if now >= next_docs_generation:
                    self.run_docs_generation()
                    next_docs_generation = now + timedelta(seconds=docs_generation_interval)

                # Phase 15 & 16: Run resilience check on schedule
                if now >= next_resilience_check:
                    self.run_resilience_check()
                    next_resilience_check = now + timedelta(seconds=resilience_check_interval)

                # Sleep briefly to avoid busy-waiting
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in daemon loop: {e}")
        finally:
            self.stop_all_daemons()
            self.running = False
            logger.info("Orchestrator stopped")

    def run(self, daemon: bool = False):
        """Run orchestrator.
        
        Args:
            daemon: Run as background daemon (via LaunchAgent)
        """
        logger.info("=" * 80)
        logger.info("META-ORCHESTRATOR STARTING")
        logger.info("=" * 80)

        # Start all enabled daemons
        start_results = self.start_all_daemons()
        logger.info(f"Daemon startup results: {start_results}")

        # Trigger initial discovery
        self.trigger_discovery(force=True)

        # Run main loop
        if daemon:
            logger.info("Running in daemon mode")
            self.daemon_loop()
        else:
            logger.info("Running in foreground mode")
            logger.info("Press Ctrl+C to stop")
            self.daemon_loop()


def main():
    """CLI interface for orchestrator."""
    parser = argparse.ArgumentParser(description='Meta-Orchestrator')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--status', action='store_true', help='Show status and exit')
    parser.add_argument('--discover', action='store_true', help='Run discovery and exit')
    parser.add_argument('--sync', action='store_true', help='Run sync and exit')
    parser.add_argument('--health', action='store_true', help='Run health check and exit')
    parser.add_argument('--clipboard-sync', action='store_true', help='Sync clipboard to KG and exit')
    
    # Phase 13 & 14: Agent command-line options
    parser.add_argument('--cataloger-scan', action='store_true', help='Run cataloger agent scan and exit')
    parser.add_argument('--maintainer-check', action='store_true', help='Run maintainer agent check and exit')
    parser.add_argument('--docs-gen', action='store_true', help='Run synthesizer agent docs generation and exit')
    
    # Phase 15 & 16: Resilience command-line options
    parser.add_argument('--resilience-check', action='store_true', help='Run resilience agent check and exit')
    
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--start-daemon', type=str, help='Start specific daemon by name')
    parser.add_argument('--stop-daemon', type=str, help='Stop specific daemon by name')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    orchestrator = MetaOrchestrator(config_path=args.config)

    if args.status:
        status = orchestrator.get_status()
        print("\n📊 METASYSTEM ORCHESTRATOR STATUS")
        print("=" * 80)
        print(json.dumps(status, indent=2))
        return

    if args.discover:
        result = orchestrator.trigger_discovery(force=True)
        print("\n🔍 DISCOVERY RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.sync:
        result = orchestrator.trigger_sync(force=True)
        print("\n🔄 SYNC RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.health:
        result = orchestrator.run_health_check(force=True)
        print("\n💚 HEALTH CHECK RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.clipboard_sync:
        result = orchestrator.trigger_clipboard_sync(force=True)
        print("\n📋 CLIPBOARD SYNC RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.start_daemon:
        if args.start_daemon in orchestrator.daemons:
            daemon = orchestrator.daemons[args.start_daemon]
            daemon.enabled = True
            success = daemon.start()
            print(f"{'✅' if success else '❌'} {args.start_daemon} {'started' if success else 'failed to start'}")
        else:
            print(f"❌ Unknown daemon: {args.start_daemon}")
        return

    if args.stop_daemon:
        if args.stop_daemon in orchestrator.daemons:
            daemon = orchestrator.daemons[args.stop_daemon]
            success = daemon.stop()
            print(f"{'✅' if success else '❌'} {args.stop_daemon} {'stopped' if success else 'failed to stop'}")
        else:
            print(f"❌ Unknown daemon: {args.stop_daemon}")
        return

    # Phase 13 & 14: Agent command handlers
    if args.cataloger_scan:
        result = orchestrator.run_cataloger_scan(force=True)
        print("\n🔍 CATALOGER AGENT RESULTS")
        print("=" * 80)
        print(json.dumps({k: v for k, v in result.items() if k != 'issues'}, indent=2))
        return

    if args.maintainer_check:
        result = orchestrator.run_maintainer_check(force=True)
        print("\n🏥 MAINTAINER AGENT RESULTS")
        print("=" * 80)
        print(f"Total issues: {result.get('total_issues', 0)}")
        print(f"Critical: {result.get('critical', 0)}")
        print(f"Warnings: {result.get('warnings', 0)}")
        print(f"Repairs made: {result.get('repairs_made', 0)}")
        return

    if args.docs_gen:
        result = orchestrator.run_docs_generation(force=True)
        print("\n📚 SYNTHESIZER AGENT RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    # Phase 15 & 16: Resilience check handler
    if args.resilience_check:
        result = orchestrator.run_resilience_check(force=True)
        print("\n🛡️ RESILIENCE AGENT RESULTS")
        print("=" * 80)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Recovery attempts: {result.get('recoveries_attempted', 0)}")
        print(f"Issues resolved: {result.get('issues_resolved', 0)}")
        if 'sync_health' in result:
            print(f"\nSync Health:")
            print(f"  iCloud allowed: {result['sync_health'].get('icloud_sync_allowed')}")
            print(f"  External allowed: {result['sync_health'].get('external_sync_allowed')}")
        print(f"\nCircuit Breakers:")
        for cb_name, cb_status in result.get('circuit_breakers', {}).items():
            print(f"  {cb_name}: {cb_status['state']}")
        return
    
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--start-daemon', type=str, help='Start specific daemon by name')
    parser.add_argument('--stop-daemon', type=str, help='Stop specific daemon by name')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    orchestrator = MetaOrchestrator(config_path=args.config)

    if args.status:
        status = orchestrator.get_status()
        print("\n📊 METASYSTEM ORCHESTRATOR STATUS")
        print("=" * 80)
        print(json.dumps(status, indent=2))
        return

    if args.discover:
        result = orchestrator.trigger_discovery(force=True)
        print("\n🔍 DISCOVERY RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.sync:
        result = orchestrator.trigger_sync(force=True)
        print("\n🔄 SYNC RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.health:
        result = orchestrator.run_health_check(force=True)
        print("\n💚 HEALTH CHECK RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.clipboard_sync:
        result = orchestrator.trigger_clipboard_sync(force=True)
        print("\n📋 CLIPBOARD SYNC RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return

    if args.start_daemon:
        if args.start_daemon in orchestrator.daemons:
            daemon = orchestrator.daemons[args.start_daemon]
            daemon.enabled = True
            success = daemon.start()
            print(f"{'✅' if success else '❌'} {args.start_daemon} {'started' if success else 'failed to start'}")
        else:
            print(f"❌ Unknown daemon: {args.start_daemon}")
        return

    if args.stop_daemon:
        if args.stop_daemon in orchestrator.daemons:
            daemon = orchestrator.daemons[args.stop_daemon]
            success = daemon.stop()
            print(f"{'✅' if success else '❌'} {args.stop_daemon} {'stopped' if success else 'failed to stop'}")
        else:
            print(f"❌ Unknown daemon: {args.stop_daemon}")
        return

    # Run main daemon loop
    orchestrator.run(daemon=args.daemon)

    # Phase 13 & 14: Agent command handlers
    if args.cataloger_scan:
        result = orchestrator.run_cataloger_scan(force=True)
        print("\\n🔍 CATALOGER AGENT RESULTS")
        print("=" * 80)
        print(json.dumps({k: v for k, v in result.items() if k != 'issues'}, indent=2))
        return

    if args.maintainer_check:
        result = orchestrator.run_maintainer_check(force=True)
        print("\\n🏥 MAINTAINER AGENT RESULTS")
        print("=" * 80)
        print(f"Total issues: {result.get('total_issues', 0)}")
        print(f"Critical: {result.get('critical', 0)}")
        print(f"Warnings: {result.get('warnings', 0)}")
        print(f"Repairs made: {result.get('repairs_made', 0)}")
        return

    if args.docs_gen:
        result = orchestrator.run_docs_generation(force=True)
        print("\\n📚 SYNTHESIZER AGENT RESULTS")
        print("=" * 80)
        print(json.dumps(result, indent=2))
        return


if __name__ == '__main__':
    main()
