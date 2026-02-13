#!/usr/bin/env python3
"""
Phase 17: Adaptive Retry Strategy
Implements smart retry logic with exponential backoff and jitter.
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Callable, Any, Optional, Dict

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(self,
                 max_attempts: int = 3,
                 initial_backoff: float = 1.0,
                 max_backoff: float = 60.0,
                 backoff_multiplier: float = 2.0,
                 use_jitter: bool = True):
        """Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of retry attempts
            initial_backoff: Initial backoff time in seconds
            max_backoff: Maximum backoff time in seconds
            backoff_multiplier: Multiplier for exponential backoff
            use_jitter: Whether to add random jitter to backoff
        """
        self.max_attempts = max_attempts
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.use_jitter = use_jitter


class AdaptiveRetry:
    """
    Phase 17: Adaptive Retry Strategy
    
    Implements intelligent retry logic with:
    - Exponential backoff (1s, 2s, 4s, 8s, ...)
    - Jitter to prevent thundering herd
    - Adaptive timeout based on previous attempts
    - Failure analysis and learning
    - Circuit breaker integration
    
    Features:
    - Tracks retry history per operation
    - Learns optimal retry parameters
    - Detects permanent vs transient failures
    - Integrates with resilience agent
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize adaptive retry system.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self.attempt_history: Dict[str, list] = {}  # Track attempts per operation
        self.adaptive_params: Dict[str, RetryConfig] = {}  # Per-operation configs
    
    def retry(self, operation: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with automatic retry.
        
        Args:
            operation: Name of operation (for tracking)
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        config = self.adaptive_params.get(operation, self.config)
        
        # Initialize history for this operation
        if operation not in self.attempt_history:
            self.attempt_history[operation] = []
        
        last_exception = None
        
        for attempt in range(1, config.max_attempts + 1):
            try:
                logger.info(f"[{operation}] Attempt {attempt}/{config.max_attempts}")
                result = func(*args, **kwargs)
                
                # Success!
                self._record_success(operation, attempt)
                return result
            
            except Exception as e:
                last_exception = e
                logger.warning(f"[{operation}] Attempt {attempt} failed: {e}")
                
                # Record failure
                self._record_failure(operation, attempt, e)
                
                # Don't retry on last attempt
                if attempt >= config.max_attempts:
                    break
                
                # Calculate backoff
                backoff = self._calculate_backoff(operation, attempt, config)
                logger.info(f"[{operation}] Retrying in {backoff:.2f}s...")
                time.sleep(backoff)
        
        # All retries exhausted
        logger.error(f"[{operation}] All {config.max_attempts} attempts failed")
        raise last_exception
    
    def retry_async(self, operation: str, func: Callable, 
                   *args, **kwargs) -> Optional[Any]:
        """Execute function with retry, returning None on failure (no exception).
        
        Args:
            operation: Name of operation
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None on failure
        """
        try:
            return self.retry(operation, func, *args, **kwargs)
        except Exception as e:
            logger.error(f"[{operation}] Failed permanently: {e}")
            return None
    
    # Backoff Calculation
    
    def _calculate_backoff(self, operation: str, attempt: int, 
                          config: RetryConfig) -> float:
        """Calculate backoff time with exponential growth and jitter.
        
        Args:
            operation: Operation name
            attempt: Current attempt number (1-indexed)
            config: Retry configuration
            
        Returns:
            Backoff time in seconds
        """
        # Exponential backoff: initial * multiplier^(attempt-1)
        backoff = config.initial_backoff * (config.backoff_multiplier ** (attempt - 1))
        
        # Cap at max backoff
        backoff = min(backoff, config.max_backoff)
        
        # Add jitter (±20% of backoff)
        if config.use_jitter:
            jitter = backoff * 0.2 * random.random()
            backoff += jitter if random.random() > 0.5 else -jitter
        
        return max(backoff, 0.1)  # Never less than 100ms
    
    # Tracking and Analysis
    
    def _record_success(self, operation: str, attempt: int):
        """Record successful attempt.
        
        Args:
            operation: Operation name
            attempt: Which attempt succeeded
        """
        self.attempt_history[operation].append({
            'timestamp': datetime.now(),
            'success': True,
            'attempt': attempt,
        })
        
        # Optimize parameters if many retries were needed
        if attempt > 1:
            self._optimize_retry_params(operation, attempt)
    
    def _record_failure(self, operation: str, attempt: int, error: Exception):
        """Record failed attempt.
        
        Args:
            operation: Operation name
            attempt: Which attempt failed
            error: Exception that was raised
        """
        self.attempt_history[operation].append({
            'timestamp': datetime.now(),
            'success': False,
            'attempt': attempt,
            'error': str(error)[:100],  # Truncate long errors
            'error_type': type(error).__name__,
        })
    
    def _optimize_retry_params(self, operation: str, successful_attempt: int):
        """Adaptively optimize retry parameters based on success.
        
        If we succeeded on attempt N, increase backoff for this operation
        to give more time before retrying.
        
        Args:
            operation: Operation name
            successful_attempt: Which attempt succeeded
        """
        if operation not in self.adaptive_params:
            # Initialize with slightly longer backoff
            self.adaptive_params[operation] = RetryConfig(
                max_attempts=self.config.max_attempts,
                initial_backoff=self.config.initial_backoff * successful_attempt,
                max_backoff=self.config.max_backoff,
                backoff_multiplier=self.config.backoff_multiplier,
            )
    
    # Analysis and Statistics
    
    def get_retry_stats(self, operation: str, hours: int = 24) -> Dict[str, Any]:
        """Get retry statistics for an operation.
        
        Args:
            operation: Operation name
            hours: Look back N hours
            
        Returns:
            Statistics dictionary
        """
        if operation not in self.attempt_history:
            return {'total_attempts': 0}
        
        cutoff = datetime.now() - timedelta(hours=hours)
        attempts = [
            a for a in self.attempt_history[operation]
            if a['timestamp'] > cutoff
        ]
        
        if not attempts:
            return {'total_attempts': 0}
        
        successes = sum(1 for a in attempts if a['success'])
        failures = len(attempts) - successes
        
        # Analyze failure patterns
        error_types = {}
        for attempt in attempts:
            if not attempt['success']:
                error = attempt.get('error_type', 'unknown')
                error_types[error] = error_types.get(error, 0) + 1
        
        return {
            'total_attempts': len(attempts),
            'successes': successes,
            'failures': failures,
            'success_rate': (successes / len(attempts) * 100) if attempts else 0,
            'avg_attempts_per_success': len(attempts) / successes if successes > 0 else 0,
            'common_errors': sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:5],
        }
    
    def analyze_failures(self, operation: str) -> Dict[str, Any]:
        """Analyze failure patterns for an operation.
        
        Args:
            operation: Operation name
            
        Returns:
            Analysis results
        """
        if operation not in self.attempt_history:
            return {'total_failures': 0}
        
        failures = [
            a for a in self.attempt_history[operation]
            if not a['success']
        ]
        
        if not failures:
            return {'total_failures': 0}
        
        # Categorize failures
        transient = 0  # Failures that recovered on retry
        permanent = 0  # Failures that never recovered
        
        for i, failure in enumerate(failures):
            # Check if next attempt was success
            next_idx = self.attempt_history[operation].index(failure) + 1
            if next_idx < len(self.attempt_history[operation]):
                next_attempt = self.attempt_history[operation][next_idx]
                if next_attempt['success']:
                    transient += 1
                else:
                    permanent += 1
            else:
                permanent += 1
        
        return {
            'total_failures': len(failures),
            'transient': transient,
            'permanent': permanent,
            'transient_rate': (transient / len(failures) * 100) if failures else 0,
            'recommendation': (
                'Increase backoff - many transient failures'
                if transient > permanent
                else 'Circuit breaker may be needed - many permanent failures'
            ),
        }
    
    # Circuit Breaker Integration
    
    def should_attempt(self, operation: str, circuit_breaker_state: Optional[str] = None) -> bool:
        """Check if operation should be attempted given circuit breaker state.
        
        Args:
            operation: Operation name
            circuit_breaker_state: State of circuit breaker (closed, open, half_open)
            
        Returns:
            True if operation should be attempted
        """
        if circuit_breaker_state == 'open':
            logger.warning(f"Circuit breaker for {operation} is OPEN - skipping")
            return False
        
        # Check recent failure rate
        stats = self.get_retry_stats(operation, hours=1)
        if stats.get('success_rate', 100) < 25:  # Less than 25% success
            logger.warning(f"Low success rate for {operation} - consider circuit breaker")
        
        return True
    
    # Reset and Cleanup
    
    def reset_operation(self, operation: str):
        """Reset tracking for an operation.
        
        Args:
            operation: Operation name
        """
        if operation in self.attempt_history:
            self.attempt_history[operation] = []
        if operation in self.adaptive_params:
            del self.adaptive_params[operation]
        
        logger.info(f"Reset retry tracking for {operation}")
    
    def reset_all(self):
        """Reset all tracking."""
        self.attempt_history.clear()
        self.adaptive_params.clear()
        logger.info("Reset all retry tracking")
