#!/usr/bin/env python3
"""
agent_utils - Utilities for agents to integrate with metasystem KG

Core Components:
- BaseAgent: Abstract base class for all agents
- MetasystemClient: HTTP client for KG operations
- AgentContext: Context data structure
- AgentDecision: Decision data structure

Custom Exceptions:
- MetasystemConnectionError
- ContextLookupError
- DecisionLoggingError
- ValidationError
- TimeoutError
- RetryExhaustedError

Usage:
    from agent_utils import BaseAgent
    
    class MyAgent(BaseAgent):
        def initialize(self):
            pass
        
        def work(self):
            context = self.get_context("My scenario")
            decision = self.log_decision("Use async/await", category="architecture")
            similar = self.query_similar_decisions()
        
        def shutdown(self):
            pass
    
    agent = MyAgent("my-agent", project="myproject")
    agent.run()
"""

from .base_agent import BaseAgent, AgentContext, AgentDecision
from .metasystem_client import MetasystemClient
from .errors import (
    MetasystemError,
    MetasystemConnectionError,
    ContextLookupError,
    DecisionLoggingError,
    ValidationError,
    TimeoutError,
    RetryExhaustedError
)

__version__ = '1.0.0'
__all__ = [
    'BaseAgent',
    'AgentContext',
    'AgentDecision',
    'MetasystemClient',
    'MetasystemError',
    'MetasystemConnectionError',
    'ContextLookupError',
    'DecisionLoggingError',
    'ValidationError',
    'TimeoutError',
    'RetryExhaustedError',
]
