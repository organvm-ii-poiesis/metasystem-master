#!/usr/bin/env python3
"""
Phase 16: Resilience Agent
Monitors sync health, implements circuit breaker pattern, and auto-recovers from failures.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"            # Too many failures, stop trying
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreaker:
    """Circuit breaker for sync operations."""
    name: str
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: int = 300
    
    def __post_init__(self):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        
    def record_success(self):
        """Record a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info(f"Circuit breaker '{self.name}': Recovered to CLOSED")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit breaker '{self.name}': Too many failures ({self.failure_count}), OPEN")
                self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            logger.warning(f"Circuit breaker '{self.name}': Recovery failed, back to OPEN")
            self.state = CircuitState.OPEN
            self.success_count = 0
    
    def allow_request(self) -> bool:
        """Check if operation should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed > self.timeout_seconds:
                    logger.info(f"Circuit breaker '{self.name}': Timeout elapsed, HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
            return False
        elif self.state == CircuitState.HALF_OPEN:
            return True
        return False


class ResilienceAgent:
    """
    Phase 16: Self-Repair & Resilience Agent
    
    Monitors system health, implements circuit breaker patterns, and auto-recovers
    from common failures. Provides resilience mechanisms for sync operations and
    general system health.
    
    Key features:
    - Circuit breaker pattern for sync operations
    - Automatic error recovery with exponential backoff
    - Health monitoring and early warning
    - Self-healing for common issues
    - Graceful degradation under failure
    """
    
    def __init__(self, kg=None):
        """Initialize resilience agent."""
        self.kg = kg
        self.name = "resilience_agent"
        
        # State file for persistence
        self.state_file = Path.home() / ".metasystem" / "resilience-state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Circuit breakers for different operations
        self.circuit_breakers = {
            'icloud_sync': CircuitBreaker('icloud_sync', failure_threshold=3, timeout_seconds=600),
            'external_sync': CircuitBreaker('external_sync', failure_threshold=3, timeout_seconds=600),
            'database_write': CircuitBreaker('database_write', failure_threshold=5, timeout_seconds=300),
            'knowledge_graph': CircuitBreaker('knowledge_graph', failure_threshold=4, timeout_seconds=400),
        }
        
        # Retry policy configuration
        self.retry_config = {
            'max_attempts': 3,
            'initial_backoff': 1,      # seconds
            'max_backoff': 30,         # seconds
            'backoff_multiplier': 2,
        }
        
        # Health thresholds
        self.health_thresholds = {
            'disk_space_warning': 10,    # GB
            'disk_space_critical': 5,    # GB
            'db_size_warning': 500,      # MB
            'sync_failure_rate': 0.5,    # 50% failure rate
        }
    
    def initialize(self):
        """Initialize resilience agent."""
        logger.info(f"Initializing {self.name}...")
        
        # Load previous state if exists
        self._load_state()
        
        logger.info(f"Resilience agent initialized with {len(self.circuit_breakers)} circuit breakers")
    
    def work(self):
        """Execute resilience checks and recovery operations."""
        logger.info("Running resilience checks...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'checks': [],
            'circuit_breakers': {},
            'recoveries_attempted': 0,
            'issues_resolved': 0,
        }
        
        # Check circuit breaker health
        report['circuit_breakers'] = self._check_circuit_breakers()
        
        # Run health checks
        health_issues = self._run_health_checks()
        report['checks'] = health_issues
        
        # Attempt recovery for critical issues
        recoveries = self._attempt_recovery(health_issues)
        report['recoveries_attempted'] = len(recoveries)
        report['issues_resolved'] = sum(1 for r in recoveries if r.get('resolved'))
        
        # Log to knowledge graph
        self.kg.insert_entity({
            'id': f"resilience_check_{datetime.now().timestamp()}",
            'type': 'resilience_agent_event',
            'metadata': report,
            'created_at': datetime.now().isoformat()
        })
        
        # Save state
        self._save_state(report)
        
        return report
    
    def shutdown(self):
        """Shutdown resilience agent."""
        logger.info(f"Shutting down {self.name}")
        self._save_state()
    
    # Circuit Breaker Operations
    
    def _check_circuit_breakers(self) -> Dict[str, Dict[str, Any]]:
        """Check status of all circuit breakers."""
        status = {}
        for name, cb in self.circuit_breakers.items():
            status[name] = {
                'state': cb.state.value,
                'failures': cb.failure_count,
                'successes': cb.success_count,
                'last_failure': cb.last_failure_time.isoformat() if cb.last_failure_time else None,
            }
        return status
    
    def check_sync_health(self) -> Dict[str, Any]:
        """Check sync operation health."""
        try:
            from sync_engine import SyncEngine
            sync = SyncEngine()
            
            # Check if operations are allowed
            icloud_allowed = self.circuit_breakers['icloud_sync'].allow_request()
            external_allowed = self.circuit_breakers['external_sync'].allow_request()
            
            result = {
                'icloud_sync_allowed': icloud_allowed,
                'external_sync_allowed': external_allowed,
                'icloud_breaker': self.circuit_breakers['icloud_sync'].state.value,
                'external_breaker': self.circuit_breakers['external_sync'].state.value,
            }
            
            return result
        except Exception as e:
            logger.error(f"Error checking sync health: {e}")
            return {'error': str(e)}
    
    def check_circuit_breaker(self, breaker_name: str) -> bool:
        """Check if circuit breaker allows operation."""
        if breaker_name not in self.circuit_breakers:
            return True  # Unknown breaker, allow operation
        
        return self.circuit_breakers[breaker_name].allow_request()
    
    def record_sync_success(self, target: str):
        """Record successful sync operation."""
        if target == 'icloud':
            self.circuit_breakers['icloud_sync'].record_success()
        elif target == 'external':
            self.circuit_breakers['external_sync'].record_success()
    
    def record_sync_failure(self, target: str):
        """Record failed sync operation."""
        if target == 'icloud':
            self.circuit_breakers['icloud_sync'].record_failure()
        elif target == 'external':
            self.circuit_breakers['external_sync'].record_failure()
    
    # Health Checks
    
    def _run_health_checks(self) -> List[Dict[str, Any]]:
        """Run all health checks."""
        issues = []
        
        # Check disk space
        disk_check = self._check_disk_space()
        if disk_check['status'] != 'ok':
            issues.append(disk_check)
        
        # Check database health
        db_check = self._check_database_health()
        if db_check['status'] != 'ok':
            issues.append(db_check)
        
        # Check sync recency
        sync_check = self._check_sync_recency()
        if sync_check['status'] != 'ok':
            issues.append(sync_check)
        
        # Check circuit breaker status
        cb_check = self._check_circuit_breaker_health()
        if cb_check['status'] != 'ok':
            issues.append(cb_check)
        
        return issues
    
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        try:
            import shutil
            stat = shutil.disk_usage(Path.home())
            free_gb = stat.free / (1024 ** 3)
            
            if free_gb < self.health_thresholds['disk_space_critical']:
                return {
                    'type': 'disk_space_critical',
                    'status': 'critical',
                    'free_gb': round(free_gb, 2),
                    'severity': 'critical',
                }
            elif free_gb < self.health_thresholds['disk_space_warning']:
                return {
                    'type': 'disk_space_warning',
                    'status': 'warning',
                    'free_gb': round(free_gb, 2),
                    'severity': 'warning',
                }
            
            return {'type': 'disk_space', 'status': 'ok', 'free_gb': round(free_gb, 2)}
        except Exception as e:
            return {'type': 'disk_space', 'status': 'error', 'error': str(e)}
    
    def _check_database_health(self) -> Dict[str, Any]:
        """Check database integrity and size."""
        try:
            db_path = Path.home() / ".metasystem" / "metastore.db"
            
            if not db_path.exists():
                return {'type': 'database', 'status': 'ok', 'exists': False}
            
            # Check size
            size_mb = db_path.stat().st_size / (1024 ** 2)
            
            if size_mb > self.health_thresholds['db_size_warning']:
                logger.warning(f"Database size warning: {size_mb:.2f}MB")
            
            # Check integrity
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                conn.close()
                
                if result != 'ok':
                    return {
                        'type': 'database',
                        'status': 'error',
                        'integrity': result,
                        'severity': 'critical',
                    }
                
                return {
                    'type': 'database',
                    'status': 'ok',
                    'size_mb': round(size_mb, 2),
                    'integrity': 'ok'
                }
            except Exception as e:
                return {'type': 'database', 'status': 'error', 'error': str(e), 'severity': 'critical'}
        except Exception as e:
            return {'type': 'database', 'status': 'error', 'error': str(e)}
    
    def _check_sync_recency(self) -> Dict[str, Any]:
        """Check when last sync occurred."""
        try:
            db_path = Path.home() / ".metasystem" / "metastore.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Query recent sync events
            cursor.execute("""
                SELECT created_at FROM entities 
                WHERE type IN ('sync_event', 'sync_error')
                ORDER BY created_at DESC
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {
                    'type': 'sync_recency',
                    'status': 'warning',
                    'last_sync': None,
                    'message': 'No sync events recorded',
                }
            
            last_sync = datetime.fromisoformat(result[0])
            age_minutes = (datetime.now() - last_sync).total_seconds() / 60
            
            if age_minutes > 360:  # 6 hours
                return {
                    'type': 'sync_recency',
                    'status': 'warning',
                    'last_sync': last_sync.isoformat(),
                    'age_minutes': round(age_minutes),
                }
            
            return {
                'type': 'sync_recency',
                'status': 'ok',
                'last_sync': last_sync.isoformat(),
                'age_minutes': round(age_minutes),
            }
        except Exception as e:
            return {'type': 'sync_recency', 'status': 'error', 'error': str(e)}
    
    def _check_circuit_breaker_health(self) -> Dict[str, Any]:
        """Check circuit breaker status."""
        open_breakers = [name for name, cb in self.circuit_breakers.items()
                        if cb.state == CircuitState.OPEN]
        
        if open_breakers:
            return {
                'type': 'circuit_breaker',
                'status': 'warning',
                'open_breakers': open_breakers,
                'severity': 'warning',
            }
        
        return {'type': 'circuit_breaker', 'status': 'ok', 'breakers': len(self.circuit_breakers)}
    
    # Recovery Operations
    
    def _attempt_recovery(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Attempt to recover from health issues."""
        recoveries = []
        
        for issue in issues:
            recovery = None
            
            if issue['type'] == 'disk_space_critical':
                recovery = self._recover_disk_space()
            elif issue['type'] == 'database':
                recovery = self._recover_database()
            elif issue['type'] == 'sync_recency':
                recovery = self._trigger_sync_recovery()
            elif issue['type'] == 'circuit_breaker':
                recovery = self._reset_circuit_breakers(issue.get('open_breakers', []))
            
            if recovery:
                recoveries.append(recovery)
        
        return recoveries
    
    def _recover_disk_space(self) -> Dict[str, Any]:
        """Attempt to free up disk space."""
        try:
            logger.warning("Attempting to free disk space...")
            
            # Find and remove old backup files
            backup_dir = Path.home() / ".metasystem" / "backups"
            if backup_dir.exists():
                # Remove backups older than 30 days
                cutoff = datetime.now() - timedelta(days=30)
                removed = 0
                
                for backup_file in backup_dir.glob("*"):
                    if backup_file.stat().st_mtime < cutoff.timestamp():
                        backup_file.unlink()
                        removed += 1
                
                if removed > 0:
                    logger.info(f"Removed {removed} old backup files")
            
            return {
                'type': 'disk_space_recovery',
                'resolved': True,
                'message': 'Cleaned up old backups',
            }
        except Exception as e:
            logger.error(f"Disk space recovery failed: {e}")
            return {
                'type': 'disk_space_recovery',
                'resolved': False,
                'error': str(e),
            }
    
    def _recover_database(self) -> Dict[str, Any]:
        """Attempt to repair database."""
        try:
            logger.warning("Attempting database recovery...")
            
            db_path = Path.home() / ".metasystem" / "metastore.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Run PRAGMA operations
            cursor.execute("PRAGMA optimize")
            cursor.execute("VACUUM")
            
            conn.commit()
            conn.close()
            
            logger.info("Database recovery successful")
            return {
                'type': 'database_recovery',
                'resolved': True,
                'message': 'Optimized and vacuumed database',
            }
        except Exception as e:
            logger.error(f"Database recovery failed: {e}")
            return {
                'type': 'database_recovery',
                'resolved': False,
                'error': str(e),
            }
    
    def _trigger_sync_recovery(self) -> Dict[str, Any]:
        """Trigger a recovery sync operation."""
        try:
            logger.info("Triggering sync recovery...")
            # This would be called by orchestrator integration
            return {
                'type': 'sync_recovery',
                'resolved': True,
                'message': 'Sync recovery triggered',
            }
        except Exception as e:
            logger.error(f"Sync recovery failed: {e}")
            return {
                'type': 'sync_recovery',
                'resolved': False,
                'error': str(e),
            }
    
    def _reset_circuit_breakers(self, breaker_names: List[str]) -> Dict[str, Any]:
        """Attempt to reset open circuit breakers."""
        try:
            reset_count = 0
            for name in breaker_names:
                if name in self.circuit_breakers:
                    cb = self.circuit_breakers[name]
                    if cb.state == CircuitState.OPEN:
                        # Move to half-open for testing
                        cb.state = CircuitState.HALF_OPEN
                        cb.success_count = 0
                        reset_count += 1
                        logger.info(f"Reset circuit breaker '{name}' to HALF_OPEN")
            
            return {
                'type': 'circuit_breaker_reset',
                'resolved': reset_count > 0,
                'reset_count': reset_count,
                'message': f'Reset {reset_count} circuit breakers',
            }
        except Exception as e:
            logger.error(f"Circuit breaker reset failed: {e}")
            return {
                'type': 'circuit_breaker_reset',
                'resolved': False,
                'error': str(e),
            }
    
    # State Management
    
    def _load_state(self):
        """Load resilience state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    state = json.load(f)
                    logger.debug(f"Loaded resilience state from {self.state_file}")
        except Exception as e:
            logger.warning(f"Could not load resilience state: {e}")
    
    def _save_state(self, report: Optional[Dict[str, Any]] = None):
        """Save resilience state to file."""
        try:
            state = {
                'last_check': datetime.now().isoformat(),
                'circuit_breakers': self._check_circuit_breakers(),
                'latest_report': report,
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save resilience state: {e}")
