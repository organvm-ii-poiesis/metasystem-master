#!/usr/bin/env python3
"""
BaseAgent - Abstract base class for metasystem-integrated agents

Provides lifecycle management and convenient methods for:
- Getting context before work
- Logging decisions
- Querying similar work
- Error handling and recovery
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from .metasystem_client import MetasystemClient
from .errors import MetasystemError


logger = logging.getLogger('BaseAgent')


class AgentContext:
    """Context passed to agent during work."""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.past_decisions = data.get('past_decisions', [])
        self.recent_files = data.get('recent_files', [])
        self.patterns = data.get('patterns', [])
        self.similar_work = data.get('similar_work', [])
    
    def __str__(self):
        return (f"AgentContext(decisions={len(self.past_decisions)}, "
                f"files={len(self.recent_files)}, patterns={len(self.patterns)})")


class AgentDecision:
    """Represents a decision logged by agent."""
    
    def __init__(self, decision_id: str, decision_text: str, category: str):
        self.id = decision_id
        self.text = decision_text
        self.category = category
    
    def __str__(self):
        return f"AgentDecision({self.category}: {self.text[:50]}...)"


class BaseAgent(ABC):
    """
    Abstract base class for agents integrated with metasystem.
    
    Subclasses must implement:
    - initialize() - Setup before work
    - work() - Main work loop
    - shutdown() - Cleanup after work
    
    Available methods:
    - get_context() - Retrieve context from KG
    - log_decision() - Log a decision to KG
    - query_similar_decisions() - Find similar work
    - get_clipboard_context() - Access clipboard history
    - search_kg() - General KG search
    """
    
    def __init__(self, agent_name: str, project: str = 'unknown',
                 base_url: str = 'http://127.0.0.1:5000'):
        """
        Initialize agent.
        
        Args:
            agent_name: Name of this agent
            project: Project this agent works on
            base_url: MCP bridge URL
        """
        self.agent_name = agent_name
        self.project = project
        self.client = MetasystemClient(
            base_url=base_url,
            agent_name=agent_name
        )
        self.context = None
        self.decisions_logged = []
        self.last_error = None
        
        logger.info(f"Agent '{agent_name}' initialized for project '{project}'")
    
    @abstractmethod
    def initialize(self):
        """
        Initialize agent before work.
        
        Override this to:
        - Load configuration
        - Get initial context
        - Setup internal state
        """
        pass
    
    @abstractmethod
    def work(self):
        """
        Main work loop.
        
        Override this with agent's actual work logic.
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """
        Cleanup after work.
        
        Override this to:
        - Save state
        - Close resources
        - Final logging
        """
        pass
    
    def run(self):
        """
        Execute agent lifecycle: initialize → work → shutdown.
        
        Returns:
            Agent result or None
        """
        try:
            logger.info(f"Starting agent '{self.agent_name}'")
            
            self.initialize()
            logger.info("Agent initialization complete")
            
            result = self.work()
            logger.info(f"Agent work complete. Logged {len(self.decisions_logged)} decisions")
            
            self.shutdown()
            logger.info("Agent shutdown complete")
            
            return result
        
        except MetasystemError as e:
            self.last_error = e
            logger.error(f"Metasystem error: {e.to_dict()}")
            raise
        
        except Exception as e:
            self.last_error = e
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
    
    def get_context(self, scenario: str = '') -> AgentContext:
        """
        Get context from knowledge graph.
        
        Args:
            scenario: Description of work scenario
            
        Returns:
            AgentContext with decisions, files, patterns
        """
        try:
            logger.info(f"Getting context for {self.project}: {scenario}")
            data = self.client.get_context(
                project=self.project,
                scenario=scenario
            )
            
            self.context = AgentContext(data)
            logger.info(f"Context retrieved: {self.context}")
            
            return self.context
        
        except Exception as e:
            logger.error(f"Failed to get context: {e}")
            raise
    
    def log_decision(self, decision: str, category: str,
                     rationale: str = '', tags: Optional[List[str]] = None,
                     context: Optional[Dict] = None) -> AgentDecision:
        """
        Log a decision to knowledge graph.
        
        Args:
            decision: Decision description
            category: Decision type (architecture, design, implementation, testing, deployment)
            rationale: Why this decision was made
            tags: Tags for organization
            context: Additional context data
            
        Returns:
            AgentDecision object
        """
        try:
            logger.info(f"Logging decision: {decision[:50]}... (category={category})")
            
            decision_id = self.client.log_decision(
                agent_name=self.agent_name,
                decision=decision,
                category=category,
                rationale=rationale,
                project=self.project,
                tags=tags or [],
                context=context or {}
            )
            
            decision_obj = AgentDecision(decision_id, decision, category)
            self.decisions_logged.append(decision_obj)
            
            logger.info(f"Decision logged: {decision_obj}")
            
            return decision_obj
        
        except Exception as e:
            logger.error(f"Failed to log decision: {e}")
            raise
    
    def query_similar_decisions(self, pattern: str = '', limit: int = 10) -> List[Dict]:
        """
        Find similar decisions from other projects.
        
        Args:
            pattern: Search pattern (empty = use last logged decision)
            limit: Maximum results
            
        Returns:
            List of similar decision dicts
        """
        try:
            search_text = pattern or (self.decisions_logged[-1].text if self.decisions_logged else '')
            
            if not search_text:
                logger.warning("No pattern provided and no decisions logged yet")
                return []
            
            logger.info(f"Querying similar decisions: '{search_text[:50]}...'")
            
            decisions = self.client.query_similar_decisions(
                decision_text=search_text,
                project=self.project,
                limit=limit
            )
            
            logger.info(f"Found {len(decisions)} similar decisions")
            
            return decisions
        
        except Exception as e:
            logger.error(f"Failed to query similar decisions: {e}")
            return []
    
    def get_clipboard(self, search: str = '', limit: int = 20) -> Dict[str, Any]:
        """
        Get clipboard context (recent clips and tags).
        
        Args:
            search: Optional search query
            limit: Maximum clips
            
        Returns:
            Clipboard context dict
        """
        try:
            logger.info(f"Getting clipboard context (search={search})")
            
            context = self.client.get_clipboard_context(
                limit=limit,
                search=search
            )
            
            if context.get('status') == 'success':
                clips = context.get('recent_clips', [])
                logger.info(f"Retrieved {len(clips)} clipboard items")
            
            return context
        
        except Exception as e:
            logger.error(f"Failed to get clipboard context: {e}")
            return {'status': 'unavailable', 'error': str(e)}
    
    def search_kg(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search knowledge graph.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching entities
        """
        try:
            logger.info(f"Searching KG: {query}")
            results = self.client.search(query, limit=limit)
            logger.info(f"Found {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def log_activity(self, activity_type: str, description: str, **kwargs):
        """
        Log general activity (non-decision).
        
        Args:
            activity_type: Type of activity
            description: Activity description
            **kwargs: Additional data
        """
        logger.info(f"Activity: {activity_type} - {description}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.client.close()
    
    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.agent_name}' project='{self.project}'>"
