#!/usr/bin/env python3
"""
Agent Template - Minimal working example of metasystem-integrated agent

This template shows how to:
1. Initialize with metasystem context
2. Get context before making decisions
3. Log architectural decisions
4. Query similar work from other projects
5. Handle errors gracefully

Copy this file and modify initialize(), work(), and shutdown() methods
for your specific agent logic.
"""

import logging
import sys
from pathlib import Path

# Add metasystem-core to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_utils import BaseAgent, MetasystemConnectionError, ValidationError


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TemplateAgent')


class TemplateAgent(BaseAgent):
    """
    Minimal agent template showing all integration patterns.
    
    To use:
    1. Copy this file to your agents directory
    2. Modify class name to match your agent
    3. Implement initialize(), work(), shutdown()
    4. Run: agent = TemplateAgent(...); agent.run()
    """
    
    def initialize(self):
        """
        Setup phase - called before work.
        
        Use this to:
        - Load configuration
        - Get initial context from KG
        - Setup internal state
        - Validate prerequisites
        """
        logger.info("═" * 60)
        logger.info(f"Initializing {self.agent_name} for project '{self.project}'")
        logger.info("═" * 60)
        
        try:
            # Get context before starting work
            scenario = "Review codebase and log architectural decisions"
            self.context = self.get_context(scenario=scenario)
            
            # Log initialization
            logger.info(f"Found {len(self.context.past_decisions)} past decisions")
            logger.info(f"Found {len(self.context.patterns)} patterns")
            logger.info(f"Found {len(self.context.recent_files)} recent files")
            
        except MetasystemConnectionError as e:
            logger.error(f"Failed to connect to metasystem: {e}")
            # Can continue with fallback behavior if needed
            raise
    
    def work(self):
        """
        Main work loop - implement your agent logic here.
        
        Pattern 1: Log a simple decision
        - Use when making a straightforward choice
        - Include rationale for future reference
        
        Pattern 2: Query similar decisions
        - Use to find if this problem was solved before
        - Apply patterns from similar projects
        
        Pattern 3: Access clipboard context
        - Use to get recent clipboard history
        - Reference user's recent work
        
        Pattern 4: Search knowledge graph
        - Use for general entity lookups
        - Find related decisions or files
        """
        logger.info("\n" + "═" * 60)
        logger.info("Starting agent work")
        logger.info("═" * 60)
        
        try:
            # PATTERN 1: Simple decision logging
            logger.info("\n[Pattern 1] Logging a simple decision...")
            
            decision = self.log_decision(
                decision="Use async/await for I/O operations",
                category="architecture",
                rationale="Better handling of concurrent requests",
                tags=["performance", "concurrency", "async"]
            )
            logger.info(f"✓ Decision logged: {decision.id}")
            
            # PATTERN 2: Query similar decisions
            logger.info("\n[Pattern 2] Finding similar decisions...")
            
            similar = self.query_similar_decisions(
                pattern="async/await",
                limit=5
            )
            
            if similar:
                logger.info(f"✓ Found {len(similar)} similar decisions:")
                for decision in similar[:3]:
                    logger.info(f"  - {decision.get('metadata', {}).get('decision', 'N/A')[:60]}...")
            else:
                logger.info("No similar decisions found")
            
            # PATTERN 3: Access clipboard context
            logger.info("\n[Pattern 3] Accessing clipboard history...")
            
            clipboard = self.get_clipboard(limit=10)
            
            if clipboard.get('status') == 'success':
                clips = clipboard.get('recent_clips', [])
                logger.info(f"✓ Retrieved {len(clips)} recent clipboard items")
                
                if clips:
                    recent_app = clips[0].get('app', 'unknown')
                    logger.info(f"  Most recent: from {recent_app}")
            else:
                logger.info(f"Clipboard unavailable: {clipboard.get('error')}")
            
            # PATTERN 4: Search knowledge graph
            logger.info("\n[Pattern 4] Searching knowledge graph...")
            
            results = self.search_kg("async performance", limit=5)
            
            if results:
                logger.info(f"✓ Found {len(results)} matching entities:")
                for entity in results[:3]:
                    logger.info(f"  - {entity.get('name', 'Unknown')}")
            else:
                logger.info("No entities found")
            
            # PATTERN 5: Log another decision based on findings
            logger.info("\n[Pattern 5] Logging decision based on context...")
            
            related_count = len(results)
            decision2 = self.log_decision(
                decision=f"Implement async pattern (found {related_count} related entities)",
                category="implementation",
                rationale="Patterns found in knowledge graph and clipboard",
                tags=["implementation", "async", "informed-decision"],
                context={
                    "based_on_searches": related_count,
                    "similar_decisions": len(similar),
                    "clipboard_items": len(clips) if 'clips' in locals() else 0
                }
            )
            logger.info(f"✓ Context-aware decision logged: {decision2.id}")
            
            # Summary
            logger.info("\n" + "═" * 60)
            logger.info(f"Work complete! Logged {len(self.decisions_logged)} decisions")
            logger.info("═" * 60)
            
            return {
                'status': 'success',
                'decisions_logged': len(self.decisions_logged),
                'similar_found': len(similar),
                'clipboard_items': len(clips) if 'clips' in locals() else 0
            }
        
        except ValidationError as e:
            logger.error(f"Validation error: {e.to_dict()}")
            raise
        
        except MetasystemConnectionError as e:
            logger.error(f"Connection error: {e.to_dict()}")
            # Could implement fallback behavior here
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
    
    def shutdown(self):
        """
        Cleanup phase - called after work completes.
        
        Use this to:
        - Log final statistics
        - Save agent state
        - Close resources
        - Report results
        """
        logger.info("\n" + "═" * 60)
        logger.info("Agent shutdown")
        logger.info("═" * 60)
        
        # Log final summary
        logger.info(f"Total decisions logged: {len(self.decisions_logged)}")
        
        if self.decisions_logged:
            logger.info("Decisions:")
            for i, decision in enumerate(self.decisions_logged, 1):
                logger.info(f"  {i}. {decision.id} ({decision.category})")
        
        if self.last_error:
            logger.error(f"Last error encountered: {self.last_error}")
        
        logger.info("═" * 60)


# Example usage
if __name__ == '__main__':
    # Create agent
    agent = TemplateAgent(
        agent_name='template-agent',
        project='example-project'
    )
    
    try:
        # Run agent lifecycle
        result = agent.run()
        logger.info(f"\n✓ Agent completed successfully: {result}")
    
    except Exception as e:
        logger.error(f"\n✗ Agent failed: {e}")
        sys.exit(1)
