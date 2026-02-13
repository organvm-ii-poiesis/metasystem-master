#!/usr/bin/env python3
"""
Context Manager - Conversation Persistence & Resume

Tracks all Claude Code (and other AI tool) conversations, logging file accesses,
decisions made, and entities created. Enables resuming previous conversations
with full context restoration.

Critical for solving the "context loss" problem.
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

# Import knowledge graph
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_graph import KnowledgeGraph


class ConversationManager:
    """Manages conversation persistence and context restoration."""

    def __init__(self, kg_path: str = None):
        """Initialize conversation manager.

        Args:
            kg_path: Path to knowledge graph database
        """
        self.kg = KnowledgeGraph(kg_path)
        self.current_conversation_id: Optional[str] = None

        # Try to detect current conversation from environment
        self._detect_current_conversation()

    def _detect_current_conversation(self):
        """Detect if we're in an active conversation."""
        # Check for Claude Code thread ID in environment
        thread_id = os.getenv('CLAUDE_THREAD_ID')
        if thread_id:
            # Check if conversation exists
            convs = self.kg.query_conversations(tool='claude-code', limit=100)
            for conv in convs:
                if conv.get('thread_id') == thread_id:
                    self.current_conversation_id = conv['id']
                    return

    def start_conversation(self,
                          tool: str = 'claude-code',
                          thread_id: str = None,
                          auto_detect: bool = True) -> str:
        """Start a new conversation.

        Args:
            tool: Tool name (claude-code, chatgpt, gemini)
            thread_id: Optional thread ID (auto-detected if not provided)
            auto_detect: Auto-detect thread ID from environment

        Returns:
            Conversation ID (UUID)
        """
        # Auto-detect thread ID
        if auto_detect and not thread_id:
            thread_id = os.getenv('CLAUDE_THREAD_ID', 'unknown')

        # Check if conversation already exists for this thread
        if thread_id != 'unknown':
            convs = self.kg.query_conversations(tool=tool, limit=100)
            for conv in convs:
                if conv.get('thread_id') == thread_id:
                    # Resume existing conversation
                    self.current_conversation_id = conv['id']
                    self._update_last_message(conv['id'])
                    print(f"📝 Resumed conversation: {conv['id'][:8]}")
                    return conv['id']

        # Create new conversation
        conv_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conversation = {
            'id': conv_id,
            'tool': tool,
            'thread_id': thread_id,
            'started_at': now,
            'last_message_at': now,
            'context': {
                'files_accessed': [],
                'decisions': [],
                'entities_created': [],
                'commands_run': []
            },
            'summary': '',
            'state': {}
        }

        self.kg.insert_conversation(conversation)
        self.current_conversation_id = conv_id

        print(f"🆕 Started new conversation: {conv_id[:8]}")
        return conv_id

    def _update_last_message(self, conv_id: str):
        """Update last message timestamp.

        Args:
            conv_id: Conversation ID
        """
        self.kg.update_conversation(conv_id, {
            'last_message_at': datetime.now().isoformat()
        })

    def log_file_access(self,
                       file_path: str,
                       operation: str = 'read',
                       conv_id: str = None) -> bool:
        """Log a file access in current conversation.

        Args:
            file_path: Path to file accessed
            operation: Type of operation (read, write, edit, execute)
            conv_id: Conversation ID (uses current if not specified)

        Returns:
            True if logged successfully
        """
        if conv_id is None:
            conv_id = self.current_conversation_id

        if not conv_id:
            print("⚠️  No active conversation. Call start_conversation() first.")
            return False

        conv = self.kg.get_conversation(conv_id)
        if not conv:
            return False

        # Update conversation context
        context = conv.get('context', {})
        files = context.get('files_accessed', [])

        file_entry = {
            'path': file_path,
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        }

        files.append(file_entry)
        context['files_accessed'] = files

        self.kg.update_conversation(conv_id, {
            'context': context,
            'last_message_at': datetime.now().isoformat()
        })

        print(f"📁 Logged file access: {Path(file_path).name} ({operation})")
        return True

    def log_decision(self,
                    decision: str,
                    rationale: str = '',
                    category: str = 'general',
                    conv_id: str = None) -> str:
        """Log an architectural decision made in conversation.

        Args:
            decision: Description of decision
            rationale: Why this decision was made
            category: Category (architecture, design, implementation, etc.)
            conv_id: Conversation ID (uses current if not specified)

        Returns:
            Decision entity ID
        """
        if conv_id is None:
            conv_id = self.current_conversation_id

        if not conv_id:
            print("⚠️  No active conversation. Call start_conversation() first.")
            return ""

        # Create decision entity
        decision_id = str(uuid.uuid4())

        entity = {
            'id': decision_id,
            'type': 'decision',
            'name': decision[:100],  # Short name
            'metadata': {
                'decision': decision,
                'rationale': rationale,
                'category': category,
                'conversation_id': conv_id,
                'timestamp': datetime.now().isoformat()
            }
        }

        self.kg.insert_entity(entity)

        # Update conversation context (don't use relationships since conversations are in separate table)
        conv = self.kg.get_conversation(conv_id)
        context = conv.get('context', {})
        decisions = context.get('decisions', [])
        decisions.append(decision_id)
        context['decisions'] = decisions

        self.kg.update_conversation(conv_id, {'context': context})

        print(f"💡 Logged decision: {decision[:50]}...")
        return decision_id

    def log_command(self,
                   command: str,
                   output: str = '',
                   exit_code: int = 0,
                   conv_id: str = None) -> bool:
        """Log a command execution.

        Args:
            command: Command executed
            output: Command output (truncated if too long)
            exit_code: Exit code
            conv_id: Conversation ID (uses current if not specified)

        Returns:
            True if logged successfully
        """
        if conv_id is None:
            conv_id = self.current_conversation_id

        if not conv_id:
            return False

        conv = self.kg.get_conversation(conv_id)
        if not conv:
            return False

        context = conv.get('context', {})
        commands = context.get('commands_run', [])

        command_entry = {
            'command': command,
            'output': output[:500] if len(output) > 500 else output,  # Truncate
            'exit_code': exit_code,
            'timestamp': datetime.now().isoformat()
        }

        commands.append(command_entry)
        context['commands_run'] = commands

        self.kg.update_conversation(conv_id, {'context': context})

        return True

    def log_entity_created(self,
                          entity_id: str,
                          entity_type: str,
                          conv_id: str = None) -> bool:
        """Log an entity created during conversation.

        Args:
            entity_id: Entity ID
            entity_type: Entity type (project, file, tool, etc.)
            conv_id: Conversation ID (uses current if not specified)

        Returns:
            True if logged successfully
        """
        if conv_id is None:
            conv_id = self.current_conversation_id

        if not conv_id:
            return False

        # Update conversation context (don't use relationships since conversations are in separate table)
        conv = self.kg.get_conversation(conv_id)
        context = conv.get('context', {})
        entities = context.get('entities_created', [])
        entities.append({'id': entity_id, 'type': entity_type})
        context['entities_created'] = entities

        self.kg.update_conversation(conv_id, {'context': context})

        print(f"🆕 Logged entity creation: {entity_type} ({entity_id[:8]})")
        return True

    def get_context_for_resume(self, conv_id: str) -> Dict[str, Any]:
        """Get all context needed to resume a conversation.

        Args:
            conv_id: Conversation ID

        Returns:
            Dictionary with full conversation context
        """
        conv = self.kg.get_conversation(conv_id)

        if not conv:
            return {'error': 'Conversation not found'}

        # Get context from conversation
        context = conv.get('context', {})

        # Get all decisions made (from context, not relationships)
        decision_ids = context.get('decisions', [])
        decisions = []
        for decision_id in decision_ids:
            decision_entity = self.kg.get_entity(decision_id)
            if decision_entity:
                decisions.append(decision_entity)

        # Get all entities created (from context, not relationships)
        entities_created = []
        for entity_info in context.get('entities_created', []):
            entity = self.kg.get_entity(entity_info['id'])
            if entity:
                entities_created.append(entity)

        # Try to get my--father-mother clipboard context
        clipboard_context = self._get_clipboard_context(
            since=datetime.fromisoformat(conv['started_at'])
        )

        resume_data = {
            'conversation_id': conv_id,
            'tool': conv['tool'],
            'thread_id': conv.get('thread_id'),
            'started_at': conv['started_at'],
            'last_message_at': conv['last_message_at'],
            'duration_hours': self._calculate_duration(conv),
            'files_accessed': context.get('files_accessed', []),
            'commands_run': context.get('commands_run', []),
            'decisions': decisions,
            'entities_created': entities_created,
            'clipboard_context': clipboard_context,
            'summary': conv.get('summary', ''),
            'state': conv.get('state', {})
        }

        return resume_data

    def _calculate_duration(self, conv: Dict[str, Any]) -> float:
        """Calculate conversation duration in hours.

        Args:
            conv: Conversation dictionary

        Returns:
            Duration in hours
        """
        start = datetime.fromisoformat(conv['started_at'])
        end = datetime.fromisoformat(conv['last_message_at'])
        duration = end - start
        return round(duration.total_seconds() / 3600, 2)

    def _get_clipboard_context(self, since: datetime = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get clipboard context from my--father-mother.

        Args:
            since: Only get clips after this time
            limit: Maximum clips to retrieve

        Returns:
            List of clipboard entries
        """
        try:
            # Try to call my--father-mother
            mfm_path = Path.home() / "Workspace" / "my--father-mother" / "main.py"

            if not mfm_path.exists():
                return []

            # Get recent clips
            args = ['python3', str(mfm_path), 'recent', '--limit', str(limit)]

            if since:
                hours = int((datetime.now() - since).total_seconds() / 3600) + 1
                args.extend(['--since-hours', str(hours)])

            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse output (simplified - actual format may vary)
                clips = []
                for line in result.stdout.split('\n'):
                    if line.strip():
                        clips.append({'content': line[:200]})  # Truncate
                return clips

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        return []

    def search_conversations(self,
                           query: str,
                           tool: str = None,
                           since_days: int = None,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """Search conversations by content.

        Args:
            query: Search query
            tool: Filter by tool
            since_days: Only search last N days
            limit: Maximum results

        Returns:
            List of matching conversations with relevance
        """
        # Get all conversations
        since = None
        if since_days:
            since = datetime.now() - timedelta(days=since_days)

        convs = self.kg.query_conversations(tool=tool, since=since, limit=limit)

        # Simple keyword matching (can be enhanced with semantic search)
        query_lower = query.lower()
        results = []

        for conv in convs:
            relevance = 0

            # Check summary
            if conv.get('summary'):
                if query_lower in conv['summary'].lower():
                    relevance += 5

            # Check context
            context = conv.get('context', {})

            # Check file paths
            for file_entry in context.get('files_accessed', []):
                if query_lower in file_entry['path'].lower():
                    relevance += 2

            # Check decisions (from context)
            for decision_id in context.get('decisions', []):
                decision = self.kg.get_entity(decision_id)
                if decision:
                    decision_text = json.dumps(decision.get('metadata', {})).lower()
                    if query_lower in decision_text:
                        relevance += 3

            # Check commands
            for cmd in context.get('commands_run', []):
                if query_lower in cmd['command'].lower():
                    relevance += 1

            if relevance > 0:
                results.append({
                    'conversation': conv,
                    'relevance': relevance,
                    'preview': self._generate_preview(conv, query)
                })

        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)

        return results

    def _generate_preview(self, conv: Dict[str, Any], query: str) -> str:
        """Generate preview snippet for search result.

        Args:
            conv: Conversation dictionary
            query: Search query

        Returns:
            Preview text
        """
        preview_parts = []

        # Add summary if exists
        if conv.get('summary'):
            preview_parts.append(f"Summary: {conv['summary'][:100]}")

        # Add file count
        context = conv.get('context', {})
        file_count = len(context.get('files_accessed', []))
        if file_count > 0:
            preview_parts.append(f"{file_count} files accessed")

        # Add decision count
        decision_count = len(context.get('decisions', []))
        if decision_count > 0:
            preview_parts.append(f"{decision_count} decisions made")

        return " | ".join(preview_parts) if preview_parts else "No preview available"

    def summarize_conversation(self, conv_id: str, auto_save: bool = True) -> str:
        """Generate AI summary of conversation (placeholder).

        Args:
            conv_id: Conversation ID
            auto_save: Save summary to conversation

        Returns:
            Summary text
        """
        conv = self.kg.get_conversation(conv_id)
        if not conv:
            return ""

        context = conv.get('context', {})

        # Generate simple summary (can be enhanced with AI)
        parts = []

        file_count = len(context.get('files_accessed', []))
        if file_count > 0:
            parts.append(f"Accessed {file_count} files")

        decision_count = len(context.get('decisions', []))
        if decision_count > 0:
            parts.append(f"Made {decision_count} decisions")

        entity_count = len(context.get('entities_created', []))
        if entity_count > 0:
            parts.append(f"Created {entity_count} entities")

        command_count = len(context.get('commands_run', []))
        if command_count > 0:
            parts.append(f"Ran {command_count} commands")

        summary = f"Conversation {conv_id[:8]}: " + ", ".join(parts)

        if auto_save:
            self.kg.update_conversation(conv_id, {'summary': summary})

        return summary

    def get_recent_conversations(self, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations.

        Args:
            hours: Get conversations from last N hours
            limit: Maximum results

        Returns:
            List of recent conversations
        """
        since = datetime.now() - timedelta(hours=hours)
        convs = self.kg.query_conversations(since=since, limit=limit)

        # Enrich with stats
        for conv in convs:
            context = conv.get('context', {})
            conv['stats'] = {
                'files': len(context.get('files_accessed', [])),
                'decisions': len(context.get('decisions', [])),
                'commands': len(context.get('commands_run', [])),
                'duration_hours': self._calculate_duration(conv)
            }

        return convs


def main():
    """CLI for context manager."""
    import argparse

    parser = argparse.ArgumentParser(description='Metasystem Context Manager')
    parser.add_argument('command',
                       choices=['start', 'resume', 'search', 'recent', 'log-file', 'log-decision'],
                       help='Command to run')
    parser.add_argument('--tool', default='claude-code', help='Tool name')
    parser.add_argument('--conv-id', help='Conversation ID')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--file', help='File path to log')
    parser.add_argument('--decision', help='Decision to log')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back')

    args = parser.parse_args()

    cm = ConversationManager()

    if args.command == 'start':
        conv_id = cm.start_conversation(tool=args.tool)
        print(f"Conversation ID: {conv_id}")

    elif args.command == 'resume':
        if not args.conv_id:
            print("Error: --conv-id required")
            sys.exit(1)

        context = cm.get_context_for_resume(args.conv_id)
        print(json.dumps(context, indent=2))

    elif args.command == 'search':
        if not args.query:
            print("Error: --query required")
            sys.exit(1)

        results = cm.search_conversations(args.query, tool=args.tool)

        print(f"Found {len(results)} conversations:")
        for result in results:
            conv = result['conversation']
            print(f"\n  {conv['id'][:8]} (relevance: {result['relevance']})")
            print(f"  Started: {conv['started_at']}")
            print(f"  {result['preview']}")

    elif args.command == 'recent':
        convs = cm.get_recent_conversations(hours=args.hours)

        print(f"Recent conversations (last {args.hours} hours):")
        for conv in convs:
            print(f"\n  {conv['id'][:8]}")
            print(f"  Started: {conv['started_at']}")
            print(f"  Stats: {conv['stats']}")

    elif args.command == 'log-file':
        if not args.file:
            print("Error: --file required")
            sys.exit(1)

        cm.log_file_access(args.file)

    elif args.command == 'log-decision':
        if not args.decision:
            print("Error: --decision required")
            sys.exit(1)

        cm.log_decision(args.decision)


if __name__ == '__main__':
    main()
