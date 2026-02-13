#!/usr/bin/env python3
"""
Custom exceptions for agent integration with metasystem.

Structured error handling for agents interacting with the knowledge graph.
"""


class MetasystemError(Exception):
    """Base exception for all metasystem agent errors."""
    
    def __init__(self, message: str, error_code: str = 'UNKNOWN'):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def to_dict(self):
        """Convert to dict for logging."""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message
        }


class MetasystemConnectionError(MetasystemError):
    """Raised when unable to connect to metasystem MCP bridge."""
    
    def __init__(self, message: str, endpoint: str = None):
        super().__init__(message, 'CONNECTION_ERROR')
        self.endpoint = endpoint


class ContextLookupError(MetasystemError):
    """Raised when unable to retrieve context from knowledge graph."""
    
    def __init__(self, message: str, context_type: str = None):
        super().__init__(message, 'CONTEXT_LOOKUP_ERROR')
        self.context_type = context_type


class DecisionLoggingError(MetasystemError):
    """Raised when unable to log decision to knowledge graph."""
    
    def __init__(self, message: str, decision_id: str = None):
        super().__init__(message, 'DECISION_LOGGING_ERROR')
        self.decision_id = decision_id


class ValidationError(MetasystemError):
    """Raised when decision or context data fails validation."""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, 'VALIDATION_ERROR')
        self.field = field


class TimeoutError(MetasystemError):
    """Raised when MCP bridge request times out."""
    
    def __init__(self, message: str, timeout_seconds: float = None):
        super().__init__(message, 'TIMEOUT_ERROR')
        self.timeout_seconds = timeout_seconds


class RetryExhaustedError(MetasystemError):
    """Raised when all retry attempts have been exhausted."""
    
    def __init__(self, message: str, attempts: int = None):
        super().__init__(message, 'RETRY_EXHAUSTED_ERROR')
        self.attempts = attempts
