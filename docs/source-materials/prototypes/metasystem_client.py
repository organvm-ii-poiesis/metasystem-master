#!/usr/bin/env python3
"""
MetasystemClient - HTTP client for agent communication with metasystem KG

Provides convenient methods for agents to:
- Get context before work
- Log decisions
- Query similar decisions
- Search knowledge graph
- Get agent status
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    raise ImportError("requests library required: pip install requests")

from .errors import (
    MetasystemConnectionError,
    ContextLookupError,
    DecisionLoggingError,
    ValidationError,
    TimeoutError,
    RetryExhaustedError
)


logger = logging.getLogger('MetasystemClient')


class MetasystemClient:
    """
    HTTP client for agent-KG interactions via MCP bridge.
    
    Handles:
    - Connection retry with exponential backoff
    - Request validation
    - Response parsing and error handling
    - Async-compatible async method support
    """
    
    def __init__(self, base_url: str = 'http://127.0.0.1:5000',
                 timeout: float = 30.0,
                 max_retries: int = 3,
                 agent_name: str = 'unknown'):
        """
        Initialize metasystem client.
        
        Args:
            base_url: MCP bridge base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            agent_name: Name of agent (for logging)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.agent_name = agent_name
        self.session = requests.Session()
        
        logger.info(f"MetasystemClient initialized for agent '{agent_name}'")
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dict
            
        Raises:
            MetasystemConnectionError: Connection failed
            TimeoutError: Request timed out
            RetryExhaustedError: All retries exhausted
        """
        url = f"{self.base_url}{endpoint}"
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"[Attempt {attempt+1}/{self.max_retries}] {method} {endpoint}")
                
                if method.upper() == 'GET':
                    response = self.session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                
                data = response.json()
                logger.debug(f"✓ {method} {endpoint}: {response.status_code}")
                return data
                
            except requests.Timeout as e:
                last_error = TimeoutError(
                    f"Request timed out after {self.timeout}s",
                    timeout_seconds=self.timeout
                )
                logger.warning(f"Timeout on {endpoint}: {e}")
            
            except requests.ConnectionError as e:
                last_error = MetasystemConnectionError(
                    f"Connection failed to {self.base_url}: {str(e)}",
                    endpoint=endpoint
                )
                logger.warning(f"Connection error on {endpoint}: {e}")
            
            except Exception as e:
                last_error = MetasystemConnectionError(
                    f"Request failed: {str(e)}",
                    endpoint=endpoint
                )
                logger.error(f"Error on {endpoint}: {e}")
            
            # Exponential backoff for retry
            if attempt < self.max_retries - 1:
                backoff = 2 ** attempt  # 1s, 2s, 4s
                logger.info(f"Retrying in {backoff}s...")
                time.sleep(backoff)
        
        # All retries exhausted
        raise RetryExhaustedError(
            f"Failed after {self.max_retries} attempts: {str(last_error)}",
            attempts=self.max_retries
        )
    
    def get_context(self, project: str, scenario: str = '', hours: int = 168) -> Dict[str, Any]:
        """
        Get context for agent work.
        
        Returns:
        - Past decisions in project
        - Recent files
        - Patterns from past work
        - Similar work from other projects
        
        Args:
            project: Project name
            scenario: Work scenario description
            hours: Look back this many hours
            
        Returns:
            Context dict with decisions, patterns, files
            
        Raises:
            ContextLookupError: Unable to get context
        """
        try:
            params = {'project': project, 'hours': hours}
            if scenario:
                params['scenario'] = scenario
            
            response = self._request(
                'GET',
                '/metasystem/agents/query-context',
                params=params
            )
            
            if response.get('status') != 'success':
                raise ContextLookupError(
                    response.get('error', 'Unknown error'),
                    context_type='agent_context'
                )
            
            logger.info(f"Retrieved context for {project}: {len(response.get('past_decisions', []))} decisions")
            return response
        
        except MetasystemConnectionError:
            raise
        except ContextLookupError:
            raise
        except Exception as e:
            raise ContextLookupError(f"Failed to get context: {str(e)}")
    
    def log_decision(self, agent_name: str, decision: str, category: str,
                     rationale: str = '', project: str = 'unknown',
                     tags: Optional[List[str]] = None,
                     context: Optional[Dict] = None) -> str:
        """
        Log a decision to the knowledge graph.
        
        Args:
            agent_name: Name of agent making decision
            decision: Decision description
            category: Decision category (architecture, design, implementation, etc.)
            rationale: Why this decision was made
            project: Project name
            tags: Tags for categorization
            context: Additional context data
            
        Returns:
            Decision ID
            
        Raises:
            ValidationError: Decision data invalid
            DecisionLoggingError: Failed to log decision
        """
        # Validate inputs
        if not decision or len(decision) > 1000:
            raise ValidationError("Decision must be 1-1000 characters", field='decision')
        
        if not category or category not in ['architecture', 'design', 'implementation', 'testing', 'deployment']:
            raise ValidationError(f"Invalid category: {category}", field='category')
        
        if rationale and len(rationale) > 5000:
            raise ValidationError("Rationale must be ≤5000 characters", field='rationale')
        
        try:
            payload = {
                'agent_name': agent_name or self.agent_name,
                'decision': decision,
                'category': category,
                'rationale': rationale,
                'project': project,
                'tags': tags or [],
                'context': context or {}
            }
            
            response = self._request(
                'POST',
                '/metasystem/agents/log-decision',
                json=payload
            )
            
            if response.get('status') != 'logged':
                raise DecisionLoggingError(
                    response.get('error', 'Unknown error'),
                    decision_id=response.get('decision_id')
                )
            
            decision_id = response['decision_id']
            logger.info(f"Decision logged: {decision_id} ('{decision[:50]}...')")
            return decision_id
        
        except ValidationError:
            raise
        except MetasystemConnectionError:
            raise
        except DecisionLoggingError:
            raise
        except Exception as e:
            raise DecisionLoggingError(f"Failed to log decision: {str(e)}")
    
    def query_similar_decisions(self, decision_text: str, project: str = '',
                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar decisions from other projects.
        
        Args:
            decision_text: Decision to match
            project: Filter by project
            limit: Maximum results
            
        Returns:
            List of similar decisions
        """
        try:
            params = {
                'pattern': decision_text,
                'project': project or 'all',
                'limit': limit
            }
            
            response = self._request(
                'GET',
                '/metasystem/context/cross-project',
                params=params
            )
            
            decisions = response.get('similar_decisions', [])
            logger.info(f"Found {len(decisions)} similar decisions")
            return decisions
        
        except Exception as e:
            logger.warning(f"Failed to query similar decisions: {e}")
            return []
    
    def get_clipboard_context(self, limit: int = 20, search: str = '') -> Dict[str, Any]:
        """
        Get recent clipboard context.
        
        Args:
            limit: Maximum clips to return
            search: Optional search query
            
        Returns:
            Clipboard context with recent clips and tags
        """
        try:
            params = {'limit': limit}
            if search:
                params['search'] = search
            
            response = self._request(
                'GET',
                '/metasystem/context/clipboard',
                params=params
            )
            
            return response
        
        except Exception as e:
            logger.warning(f"Failed to get clipboard context: {e}")
            return {'status': 'unavailable', 'error': str(e)}
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search knowledge graph.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching entities
        """
        try:
            params = {'q': query, 'limit': limit}
            
            response = self._request(
                'GET',
                '/metasystem/search',
                params=params
            )
            
            return response.get('results', [])
        
        except Exception as e:
            logger.warning(f"Search failed: {e}")
            return []
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.
        
        Returns:
            Agent status information
        """
        try:
            response = self._request('GET', '/metasystem/agents/status')
            return response
        except Exception as e:
            logger.warning(f"Failed to get agent status: {e}")
            return {'status': 'unavailable', 'error': str(e)}
    
    def close(self):
        """Close the session."""
        self.session.close()
