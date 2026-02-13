#!/usr/bin/env python3
"""
Phase 17: Metrics Collector
Collects and stores system performance metrics for monitoring and alerting.
"""

import json
import logging
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class Metric:
    """Represents a single metric datapoint."""
    
    def __init__(self, name: str, value: float, unit: str = "", tags: Optional[Dict] = None):
        self.name = name
        self.value = value
        self.unit = unit
        self.tags = tags or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'tags': self.tags,
            'timestamp': self.timestamp.isoformat()
        }


class MetricsCollector:
    """
    Phase 17: Metrics Collection System
    
    Tracks system performance metrics including:
    - Sync success/failure rates
    - Circuit breaker state transitions
    - Health check results
    - Agent execution times
    - Resource usage (disk, memory, CPU)
    - Error rates and types
    
    Provides:
    - Real-time metric collection
    - Aggregation and statistics
    - Time-series queries
    - Anomaly detection capabilities
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize metrics collector.
        
        Args:
            db_path: Path to knowledge graph database
        """
        self.db_path = db_path or str(Path.home() / ".metasystem" / "metastore.db")
        self.metrics: List[Metric] = []
        self.thresholds = {}
        self._initialize_metrics_table()
    
    def _initialize_metrics_table(self):
        """Create metrics table if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT,
                    tags TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (id) REFERENCES entities(id)
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp 
                ON metrics(name, timestamp)
            """)
            
            conn.commit()
            conn.close()
            logger.info("Metrics table initialized")
        except Exception as e:
            logger.warning(f"Could not initialize metrics table: {e}")
    
    # Metric Recording
    
    def record_sync_metric(self, target: str, success: bool, duration: float, 
                          files_synced: int = 0, conflicts: int = 0):
        """Record sync operation metric.
        
        Args:
            target: icloud or external
            success: Whether sync succeeded
            duration: Sync duration in seconds
            files_synced: Number of files synced
            conflicts: Number of conflicts resolved
        """
        metric_name = f"sync_{target}_{'success' if success else 'failure'}"
        
        self.record_metric(
            name=metric_name,
            value=duration,
            unit="seconds",
            tags={
                'target': target,
                'success': str(success),
                'files': files_synced,
                'conflicts': conflicts,
            }
        )
    
    def record_circuit_breaker_metric(self, breaker_name: str, state: str, 
                                     failure_count: int = 0, success_count: int = 0):
        """Record circuit breaker state change.
        
        Args:
            breaker_name: Name of circuit breaker
            state: closed, open, or half_open
            failure_count: Number of failures
            success_count: Number of successes
        """
        self.record_metric(
            name=f"circuit_breaker_{breaker_name}",
            value=1.0,  # Event marker
            unit="event",
            tags={
                'breaker': breaker_name,
                'state': state,
                'failures': failure_count,
                'successes': success_count,
            }
        )
    
    def record_agent_metric(self, agent_name: str, duration: float, 
                           success: bool, items_processed: int = 0):
        """Record agent execution metric.
        
        Args:
            agent_name: Name of agent (cataloger, maintainer, etc.)
            duration: Execution duration in seconds
            success: Whether execution succeeded
            items_processed: Number of items processed
        """
        self.record_metric(
            name=f"agent_{agent_name}",
            value=duration,
            unit="seconds",
            tags={
                'agent': agent_name,
                'success': str(success),
                'items': items_processed,
            }
        )
    
    def record_health_metric(self, check_type: str, status: str, 
                            details: Optional[Dict] = None):
        """Record health check result.
        
        Args:
            check_type: disk, database, sync, breaker, etc.
            status: ok, warning, critical
            details: Additional details
        """
        self.record_metric(
            name=f"health_check_{check_type}",
            value=1.0,  # Event marker
            unit="event",
            tags={
                'type': check_type,
                'status': status,
                **(details or {}),
            }
        )
    
    def record_metric(self, name: str, value: float, unit: str = "", 
                     tags: Optional[Dict] = None):
        """Record a generic metric.
        
        Args:
            name: Metric name
            value: Metric value
            unit: Unit of measurement
            tags: Additional tags
        """
        metric = Metric(name, value, unit, tags)
        self.metrics.append(metric)
        
        # Persist to database
        self._persist_metric(metric)
        
        logger.debug(f"Recorded metric: {name}={value}{unit}")
    
    def _persist_metric(self, metric: Metric):
        """Persist metric to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (name, value, unit, tags, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metric.name,
                metric.value,
                metric.unit,
                json.dumps(metric.tags),
                metric.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Could not persist metric: {e}")
    
    # Metric Querying
    
    def get_metrics(self, name: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get metrics from past N hours.
        
        Args:
            name: Metric name or pattern (supports *)
            hours: Number of hours to look back
            
        Returns:
            List of metric records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Support wildcard matching
            like_pattern = name.replace('*', '%')
            cutoff = datetime.now() - timedelta(hours=hours)
            
            cursor.execute("""
                SELECT name, value, unit, tags, timestamp
                FROM metrics
                WHERE name LIKE ? AND timestamp > ?
                ORDER BY timestamp DESC
            """, (like_pattern, cutoff.isoformat()))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'name': row['name'],
                    'value': row['value'],
                    'unit': row['unit'],
                    'tags': json.loads(row['tags']) if row['tags'] else {},
                    'timestamp': row['timestamp'],
                })
            
            conn.close()
            return results
        except Exception as e:
            logger.warning(f"Could not query metrics: {e}")
            return []
    
    def get_metric_stats(self, name: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a metric.
        
        Args:
            name: Metric name
            hours: Number of hours to look back
            
        Returns:
            Statistics dict with min, max, avg, count
        """
        metrics = self.get_metrics(name, hours)
        
        if not metrics:
            return {'count': 0}
        
        values = [m['value'] for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'sum': sum(values),
            'latest': metrics[0]['value'] if metrics else None,
            'timestamp_latest': metrics[0]['timestamp'] if metrics else None,
        }
    
    # Success/Failure Rates
    
    def get_success_rate(self, metric_name: str, hours: int = 24) -> float:
        """Calculate success rate for a metric.
        
        Args:
            metric_name: Base metric name (e.g., 'sync_icloud')
            hours: Number of hours to look back
            
        Returns:
            Success rate as percentage (0-100)
        """
        success_metrics = self.get_metrics(f"{metric_name}_success", hours)
        failure_metrics = self.get_metrics(f"{metric_name}_failure", hours)
        
        total = len(success_metrics) + len(failure_metrics)
        if total == 0:
            return 100.0
        
        return (len(success_metrics) / total) * 100
    
    # Anomaly Detection
    
    def detect_anomalies(self, metric_name: str, hours: int = 24, 
                        std_dev_threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical analysis.
        
        Args:
            metric_name: Metric name
            hours: Hours to analyze
            std_dev_threshold: Z-score threshold for anomaly
            
        Returns:
            List of anomalous datapoints
        """
        metrics = self.get_metrics(metric_name, hours)
        
        if len(metrics) < 3:  # Need at least 3 points
            return []
        
        values = [m['value'] for m in metrics]
        mean = sum(values) / len(values)
        
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        if std_dev == 0:  # No variation
            return []
        
        # Find anomalies (values beyond threshold std devs from mean)
        anomalies = []
        for metric in metrics:
            z_score = abs((metric['value'] - mean) / std_dev)
            if z_score > std_dev_threshold:
                anomalies.append({
                    **metric,
                    'z_score': round(z_score, 2),
                    'mean': round(mean, 2),
                    'std_dev': round(std_dev, 2),
                })
        
        return anomalies
    
    # Summary and Reporting
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get summary of key system metrics.
        
        Returns:
            Dictionary with current state of key metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'sync_icloud_rate': self.get_success_rate('sync_icloud'),
            'sync_external_rate': self.get_success_rate('sync_external'),
            'agent_execution_time': self.get_metric_stats('agent_*'),
            'health_checks': self.get_metrics('health_check_*', hours=1),
        }
    
    def get_performance_report(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed performance report.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Comprehensive performance report
        """
        return {
            'period_hours': hours,
            'generated': datetime.now().isoformat(),
            'sync_metrics': {
                'icloud': {
                    'success_rate': self.get_success_rate('sync_icloud', hours),
                    'stats': self.get_metric_stats('sync_icloud_success', hours),
                },
                'external': {
                    'success_rate': self.get_success_rate('sync_external', hours),
                    'stats': self.get_metric_stats('sync_external_success', hours),
                },
            },
            'agent_metrics': {
                'cataloger': self.get_metric_stats('agent_cataloger', hours),
                'maintainer': self.get_metric_stats('agent_maintainer', hours),
                'synthesizer': self.get_metric_stats('agent_synthesizer', hours),
            },
            'circuit_breakers': {
                'states': self.get_metrics('circuit_breaker_*', hours),
            },
        }
    
    # Cleanup
    
    def cleanup_old_metrics(self, days: int = 30):
        """Remove metrics older than N days.
        
        Args:
            days: Number of days to retain
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff = datetime.now() - timedelta(days=days)
            
            cursor.execute(
                "DELETE FROM metrics WHERE timestamp < ?",
                (cutoff.isoformat(),)
            )
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old metrics")
        except Exception as e:
            logger.warning(f"Could not cleanup metrics: {e}")
