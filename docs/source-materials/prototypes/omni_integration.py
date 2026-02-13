#!/usr/bin/env python3
"""
Integration between omni-dromenon-machina and Metasystem Knowledge Graph

Enables agents to:
1. Query the knowledge graph for context before making decisions
2. Log architectural decisions as they work
3. Share learning across projects
4. Access clipboard history for inspiration

This creates a persistent memory system for autonomous agents.
"""

import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from knowledge_graph import KnowledgeGraph


logger = logging.getLogger('OmniIntegration')


class OmniIntegration:
    """
    Bridge omni-dromenon-machina agents to metasystem knowledge graph.
    """

    def __init__(self):
        """Initialize omni integration."""
        self.kg = KnowledgeGraph()
        self.omni_dir = Path.home() / 'Workspace' / 'omni-dromenon-machina'
        
        if not self.omni_dir.exists():
            logger.warning(f"omni-dromenon-machina directory not found: {self.omni_dir}")
            self.omni_dir = None

    def log_agent_decision(self, agent_name: str, decision: str, rationale: str = '',
                          category: str = 'architecture', project: str = 'unknown',
                          tags: Optional[List[str]] = None, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Log an agent decision to the knowledge graph.
        
        This is called by agents to record decisions they make during
        autonomous work, enabling learning and cross-project patterns.
        
        Args:
            agent_name: Name of the agent (e.g., 'architect', 'builder')
            decision: Description of the decision
            rationale: Why this decision was made
            category: Decision category (architecture, design, implementation, etc.)
            project: Project this decision relates to
            tags: List of tags for categorization
            context: Additional context data
            
        Returns:
            Decision ID and metadata
        """
        decision_entity = {
            'id': f"omni_decision_{datetime.now().timestamp()}",
            'type': 'decision',
            'name': f"{agent_name}: {decision[:100]}",
            'path': f"omni://{project}/{agent_name}/{category}",
            'metadata': {
                'agent_name': agent_name,
                'decision': decision,
                'rationale': rationale,
                'category': category,
                'project': project,
                'tags': tags or [],
                'context': context or {},
                'source': 'omni-dromenon-machina',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        decision_id = self.kg.insert_entity(decision_entity)
        
        logger.info(f"Logged decision from {agent_name} in {project}: {decision[:50]}...")
        
        return {
            'decision_id': decision_id,
            'status': 'logged',
            'timestamp': decision_entity['metadata']['timestamp']
        }

    def get_agent_context(self, project: str, scenario: str = '', hours: int = 168) -> Dict[str, Any]:
        """
        Get knowledge graph context for an agent starting work.
        
        Provides:
        - Past decisions in this project
        - Similar problems solved in other projects
        - Recent file changes in this project
        - Decisions by category (architecture, design, implementation)
        
        Args:
            project: Current project name
            scenario: Work scenario description
            hours: How far back to look (default 1 week)
            
        Returns:
            Context dictionary with decisions, patterns, and insights
        """
        # Get past decisions in this project
        project_decisions = self.kg.search_entities(project, limit=20)
        past_decisions = [
            d for d in project_decisions
            if d.get('type') == 'decision'
        ]
        
        # Get recent files in project
        project_files = self.kg.query_entities(type='file', limit=30)
        recent_files = [
            f for f in project_files
            if project in f.get('path', '')
        ][:10]
        
        # Get decisions by category for reference
        all_decisions = self.kg.query_entities(type='decision', limit=100)
        decisions_by_category = {}
        for decision in all_decisions:
            cat = decision.get('metadata', {}).get('category', 'unknown')
            if cat not in decisions_by_category:
                decisions_by_category[cat] = []
            decisions_by_category[cat].append(decision)
        
        # Find similar work in other projects if scenario provided
        similar_work = []
        if scenario:
            scenario_lower = scenario.lower()
            similar_work = [
                d for d in all_decisions
                if scenario_lower in json.dumps(d).lower()
            ][:5]
        
        context = {
            'project': project,
            'scenario': scenario,
            'past_decisions': past_decisions,
            'recent_files': recent_files,
            'decisions_by_category': decisions_by_category,
            'similar_work': similar_work,
            'patterns': self._extract_patterns(past_decisions),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Generated context for agent in {project}")
        
        return context

    def _extract_patterns(self, decisions: List[Dict]) -> List[str]:
        """Extract common patterns from decisions."""
        if not decisions:
            return []
        
        patterns = []
        categories = {}
        
        # Count decisions by category
        for decision in decisions:
            cat = decision.get('metadata', {}).get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        # Extract patterns
        for cat, count in categories.items():
            if count >= 3:
                patterns.append(f"Frequent pattern: {count} decisions in '{cat}' category")
        
        return patterns

    def query_similar_decisions(self, decision: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find similar decisions made in other projects.
        
        Helps agents learn from past work and apply patterns.
        
        Args:
            decision: Decision to match against
            limit: Maximum results to return
            
        Returns:
            List of similar decisions
        """
        all_decisions = self.kg.search_entities(decision, limit=limit * 2)
        
        # Filter for decisions only
        decisions = [
            d for d in all_decisions
            if d.get('type') == 'decision'
        ]
        
        return decisions[:limit]

    def log_file_created(self, path: str, project: str, description: str = '') -> Dict[str, Any]:
        """
        Log a file created by an agent.
        
        Args:
            path: File path (relative to project root)
            project: Project name
            description: What this file does
            
        Returns:
            File entity ID
        """
        file_entity = {
            'id': f"file_{project}_{path.replace('/', '_')}",
            'type': 'file',
            'path': f"{project}/{path}",
            'name': Path(path).name,
            'metadata': {
                'project': project,
                'description': description,
                'created_by_agent': True,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        file_id = self.kg.insert_entity(file_entity)
        logger.info(f"Logged file creation in {project}: {path}")
        
        return {
            'file_id': file_id,
            'status': 'logged',
            'timestamp': file_entity['metadata']['timestamp']
        }

    def get_project_summary(self, project: str) -> Dict[str, Any]:
        """
        Get a summary of all work done on a project.
        
        Args:
            project: Project name
            
        Returns:
            Project summary with decisions, files, and activity
        """
        # Get all entities related to this project
        project_entities = self.kg.search_entities(project, limit=100)
        
        summary = {
            'project': project,
            'total_entities': len(project_entities),
            'decisions': [e for e in project_entities if e.get('type') == 'decision'],
            'files': [e for e in project_entities if e.get('type') == 'file'],
            'conversations': [e for e in project_entities if e.get('type') == 'conversation'],
            'timeline': {
                'first_activity': min([e.get('created_at') for e in project_entities], default=None),
                'last_activity': max([e.get('updated_at', e.get('created_at')) for e in project_entities], default=None)
            }
        }
        
        return summary

    def inject_mcp_urls(self) -> Dict[str, str]:
        """
        Generate MCP URLs that agents can use to interact with metasystem.
        
        Returns agent-specific MCP URLs for integration.
        
        Returns:
            Dictionary of MCP endpoint URLs
        """
        base_url = 'http://127.0.0.1:5000'
        
        urls = {
            'context_current': f"{base_url}/metasystem/context/current",
            'log_decision': f"{base_url}/metasystem/agents/log-decision",
            'agent_status': f"{base_url}/metasystem/agents/status",
            'clipboard_context': f"{base_url}/metasystem/context/clipboard",
            'cross_project_context': f"{base_url}/metasystem/context/cross-project",
            'search': f"{base_url}/metasystem/search",
            'decisions_by_category': f"{base_url}/metasystem/decisions/by-category"
        }
        
        return urls

    def setup_seed_yaml_integration(self) -> Dict[str, Any]:
        """
        Provide seed.yaml configuration for omni agents to enable KG integration.
        
        Returns configuration snippet that can be added to seed.yaml
        """
        config = {
            'knowledge_graph': {
                'enabled': True,
                'db_path': str(Path.home() / '.metasystem' / 'metastore.db'),
                'mcp_endpoints': self.inject_mcp_urls(),
                'integration': {
                    'query_before_work': True,  # Check KG before starting tasks
                    'log_decisions': True,        # Log all architectural decisions
                    'log_file_changes': True,     # Track file modifications
                    'cross_project_learning': True,  # Learn from other projects
                    'sync_interval_seconds': 300   # Sync context every 5 minutes
                }
            }
        }
        
        return config


def main():
    """Test omni integration."""
    integration = OmniIntegration()
    
    # Test logging a decision
    print("Logging sample decision...")
    result = integration.log_agent_decision(
        agent_name='architect',
        decision='Use async/await for API layer',
        rationale='Better performance and code clarity',
        category='architecture',
        project='omni-dromenon-machina',
        tags=['performance', 'typescript', 'api'],
        context={'framework': 'express', 'language': 'typescript'}
    )
    print(json.dumps(result, indent=2))
    
    # Test getting agent context
    print("\nGetting agent context...")
    context = integration.get_agent_context(
        project='omni-dromenon-machina',
        scenario='Implement new API endpoint'
    )
    print(f"Context: {len(context['past_decisions'])} past decisions found")
    print(f"Patterns: {context['patterns']}")
    
    # Test MCP URLs
    print("\nMCP URLs for agents:")
    urls = integration.inject_mcp_urls()
    for name, url in urls.items():
        print(f"  {name}: {url}")
    
    # Test seed.yaml config
    print("\nRecommended seed.yaml configuration:")
    config = integration.setup_seed_yaml_integration()
    print(json.dumps(config, indent=2))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
