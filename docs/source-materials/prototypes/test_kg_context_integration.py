#!/usr/bin/env python3
"""
Integration tests for KnowledgeGraph + ContextManager interaction.

Tests how the two core components work together for conversation persistence.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_graph import KnowledgeGraph
from context_manager import ConversationManager


# ============================================================================
# Integration Tests: KG + ContextManager
# ============================================================================

class TestKGContextIntegration:
    """Test KnowledgeGraph and ContextManager integration."""

    def test_conversation_lifecycle_integration(self, tmp_path):
        """Test complete conversation lifecycle with KG."""
        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        cm = ConversationManager(str(kg_path))

        # Start conversation
        conv_id = cm.start_conversation(tool='claude-code', auto_detect=False)
        assert conv_id is not None

        # Log file access
        cm.log_file_access('/test/file1.py', operation='read')
        cm.log_file_access('/test/file2.py', operation='edit')

        # Log decision
        cm.log_decision("Using Factory pattern for widget creation")

        # Log command
        cm.log_command('pytest tests/', output='5 passed')

        # Get conversation from KG directly
        conv = kg.get_conversation(conv_id)
        assert conv is not None
        assert conv['tool'] == 'claude-code'
        assert len(conv['context']['files_accessed']) == 2
        assert len(conv['context']['decisions']) == 1
        assert len(conv['context']['commands_run']) == 1

        # Get context for resume
        context = cm.get_context_for_resume(conv_id)
        assert context['conversation_id'] == conv_id
        assert len(context['files_accessed']) == 2
        assert len(context['decisions']) == 1
        assert len(context['commands_run']) == 1

    def test_multi_conversation_isolation(self, tmp_path):
        """Test that multiple conversations are properly isolated."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create two conversations
        conv1 = cm.start_conversation(tool='claude-code', auto_detect=False)
        cm.log_file_access('/project1/file.py', operation='read')
        cm.log_decision("Decision for project 1")

        conv2 = cm.start_conversation(tool='cursor', auto_detect=False)
        cm.log_file_access('/project2/file.py', operation='read')
        cm.log_decision("Decision for project 2")

        # Get contexts
        context1 = cm.get_context_for_resume(conv1)
        context2 = cm.get_context_for_resume(conv2)

        # Verify isolation
        assert len(context1['files_accessed']) == 1
        assert context1['files_accessed'][0]['path'] == '/project1/file.py'

        assert len(context2['files_accessed']) == 1
        assert context2['files_accessed'][0]['path'] == '/project2/file.py'

        assert context1['decisions'][0]['metadata']['decision'] == "Decision for project 1"
        assert context2['decisions'][0]['metadata']['decision'] == "Decision for project 2"

    def test_search_across_conversations(self, tmp_path):
        """Test searching across multiple conversations."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversations with different content
        conv1 = cm.start_conversation(tool='claude-code', auto_detect=False)
        cm.log_file_access('/auth/login.py', operation='edit')
        cm.log_decision("Implementing JWT authentication")

        conv2 = cm.start_conversation(tool='cursor', auto_detect=False)
        cm.log_file_access('/api/users.py', operation='edit')
        cm.log_decision("Adding user CRUD endpoints")

        conv3 = cm.start_conversation(tool='claude-code', auto_detect=False)
        cm.log_file_access('/auth/middleware.py', operation='create')
        cm.log_decision("Adding authentication middleware")

        # Search for "authentication"
        results = cm.search_conversations(query='authentication', limit=10)

        # Should find at least one conversation
        # (FTS search behavior may vary based on indexing)
        assert len(results) >= 1
        # Verify search returns conversation objects
        assert 'conversation' in results[0]
        assert 'relevance' in results[0]

    def test_conversation_summary_generation(self, tmp_path):
        """Test automatic summary generation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversation with activity
        conv_id = cm.start_conversation(tool='claude-code', auto_detect=False)
        cm.log_file_access('/src/main.py', operation='edit')
        cm.log_file_access('/src/utils.py', operation='edit')
        cm.log_decision("Refactored main function")
        cm.log_command('pytest tests/', output='10 passed')

        # Generate summary
        summary = cm.summarize_conversation(conv_id, auto_save=True)

        # Should contain key information
        assert summary is not None
        assert len(summary) > 0

        # Verify summary was saved to KG
        conv = cm.kg.get_conversation(conv_id)
        assert conv['summary'] is not None
        assert len(conv['summary']) > 0

    def test_recent_conversations_retrieval(self, tmp_path):
        """Test retrieving recent conversations."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create multiple conversations with unique thread IDs
        conv1 = cm.start_conversation(tool='claude-code', thread_id='thread-1', auto_detect=False)
        cm.log_file_access('/test1.py', operation='read')

        conv2 = cm.start_conversation(tool='cursor', thread_id='thread-2', auto_detect=False)
        cm.log_file_access('/test2.py', operation='read')

        conv3 = cm.start_conversation(tool='claude-code', thread_id='thread-3', auto_detect=False)
        cm.log_file_access('/test3.py', operation='read')

        # Get recent conversations (default 24 hours)
        recent = cm.get_recent_conversations(limit=10)

        # Should find all 3
        assert len(recent) == 3
        conv_ids = [c['id'] for c in recent]
        assert conv1 in conv_ids
        assert conv2 in conv_ids
        assert conv3 in conv_ids


class TestKGContextStress:
    """Stress tests for integration under load."""

    def test_many_file_accesses(self, tmp_path):
        """Test logging many file accesses in one conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='claude-code', auto_detect=False)

        # Log 100 file accesses
        for i in range(100):
            cm.log_file_access(f'/test/file{i}.py', operation='read')

        # Get context
        context = cm.get_context_for_resume(conv_id)

        # Should have all 100 files
        assert len(context['files_accessed']) == 100

    def test_many_conversations(self, tmp_path):
        """Test creating many conversations."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create 50 conversations with unique thread IDs
        conv_ids = []
        for i in range(50):
            conv_id = cm.start_conversation(
                tool=f'tool-{i % 3}',
                thread_id=f'thread-{i}',
                auto_detect=False
            )
            cm.log_file_access(f'/file{i}.py', operation='read')
            conv_ids.append(conv_id)

        # Get recent conversations
        recent = cm.get_recent_conversations(limit=100)

        # Should find all 50
        assert len(recent) == 50
