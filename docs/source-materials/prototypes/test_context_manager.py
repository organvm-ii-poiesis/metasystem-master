#!/usr/bin/env python3
"""
Unit tests for context_manager.py - conversation persistence and context restoration.

Coverage target: >80% (critical component)
"""

import pytest
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from context_manager import ConversationManager
from tests.test_helpers import assert_conversation_valid


# ============================================================================
# Initialization Tests
# ============================================================================

@pytest.mark.unit
class TestConversationManagerInit:
    """Test ConversationManager initialization."""

    def test_init_creates_kg(self, tmp_path):
        """Should initialize with knowledge graph."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        assert cm.kg is not None
        assert Path(kg_path).exists()

    def test_init_no_current_conversation(self, tmp_path):
        """Should start with no active conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        assert cm.current_conversation_id is None

    @patch.dict(os.environ, {'CLAUDE_THREAD_ID': 'test-thread-123'})
    def test_init_detects_thread_id(self, tmp_path):
        """Should detect thread ID from environment."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Should attempt to detect (won't find anything in empty DB)
        assert cm.current_conversation_id is None  # No existing conversation

    @patch.dict(os.environ, {'CLAUDE_THREAD_ID': 'existing-thread'})
    def test_init_detects_existing_conversation(self, tmp_path):
        """Should detect and set existing conversation from thread ID."""
        kg_path = tmp_path / "test.db"

        # Create conversation first
        cm1 = ConversationManager(str(kg_path))
        conv_id = cm1.start_conversation(tool='claude-code', thread_id='existing-thread', auto_detect=False)

        # Create new manager with same thread ID in environment
        cm2 = ConversationManager(str(kg_path))

        # Should auto-detect the existing conversation
        assert cm2.current_conversation_id == conv_id


# ============================================================================
# Conversation Lifecycle Tests
# ============================================================================

@pytest.mark.unit
class TestConversationLifecycle:
    """Test conversation creation and lifecycle."""

    def test_start_conversation_default(self, tmp_path):
        """Should start new conversation with defaults."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test-tool', auto_detect=False)

        assert conv_id is not None
        assert cm.current_conversation_id == conv_id

        # Verify in knowledge graph
        conv = cm.kg.get_conversation(conv_id)
        assert conv is not None
        assert conv['tool'] == 'test-tool'
        assert 'started_at' in conv
        assert 'context' in conv
        assert isinstance(conv['context']['files_accessed'], list)
        assert isinstance(conv['context']['decisions'], list)

    def test_start_conversation_with_thread_id(self, tmp_path):
        """Should create conversation with thread ID."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='thread-123',
            auto_detect=False
        )

        conv = cm.kg.get_conversation(conv_id)
        assert conv['thread_id'] == 'thread-123'

    def test_start_conversation_resumes_existing(self, tmp_path):
        """Should resume existing conversation with same thread ID."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Start first conversation
        conv_id1 = cm.start_conversation(
            tool='claude-code',
            thread_id='thread-123',
            auto_detect=False
        )

        # Try to start again with same thread ID - should resume
        conv_id2 = cm.start_conversation(
            tool='claude-code',
            thread_id='thread-123',
            auto_detect=False
        )

        # Should be same conversation
        assert conv_id1 == conv_id2

    @patch.dict(os.environ, {'CLAUDE_THREAD_ID': 'env-thread-456'})
    def test_start_conversation_auto_detect(self, tmp_path):
        """Should auto-detect thread ID from environment."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='claude-code', auto_detect=True)

        conv = cm.kg.get_conversation(conv_id)
        assert conv['thread_id'] == 'env-thread-456'

    def test_start_multiple_conversations(self, tmp_path):
        """Should create multiple independent conversations."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id1 = cm.start_conversation(tool='claude-code', thread_id='t1', auto_detect=False)
        conv_id2 = cm.start_conversation(tool='chatgpt', thread_id='t2', auto_detect=False)
        conv_id3 = cm.start_conversation(tool='gemini', thread_id='t3', auto_detect=False)

        assert conv_id1 != conv_id2 != conv_id3
        assert cm.current_conversation_id == conv_id3  # Last one started


# ============================================================================
# File Access Logging Tests
# ============================================================================

@pytest.mark.unit
class TestFileAccessLogging:
    """Test file access tracking."""

    def test_log_file_access_basic(self, tmp_path):
        """Should log file access to conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log file access
        result = cm.log_file_access('/test/file.py', operation='read')

        assert result is True

        # Verify logged
        conv = cm.kg.get_conversation(conv_id)
        files = conv['context']['files_accessed']
        assert len(files) == 1
        assert files[0]['path'] == '/test/file.py'
        assert files[0]['operation'] == 'read'
        assert 'timestamp' in files[0]

    def test_log_file_access_multiple(self, tmp_path):
        """Should log multiple file accesses."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log multiple accesses
        cm.log_file_access('/file1.py', 'read')
        cm.log_file_access('/file2.py', 'write')
        cm.log_file_access('/file3.py', 'edit')

        conv = cm.kg.get_conversation(conv_id)
        files = conv['context']['files_accessed']
        assert len(files) == 3

        operations = [f['operation'] for f in files]
        assert 'read' in operations
        assert 'write' in operations
        assert 'edit' in operations

    def test_log_file_access_no_conversation(self, tmp_path):
        """Should fail gracefully when no active conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # No conversation started
        result = cm.log_file_access('/test/file.py')

        assert result is False

    def test_log_file_access_specific_conversation(self, tmp_path):
        """Should log to specific conversation when provided."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id1 = cm.start_conversation(tool='t1', thread_id='1', auto_detect=False)
        conv_id2 = cm.start_conversation(tool='t2', thread_id='2', auto_detect=False)

        # Log to conv1 explicitly
        cm.log_file_access('/file.py', 'read', conv_id=conv_id1)

        # Verify only in conv1
        conv1 = cm.kg.get_conversation(conv_id1)
        conv2 = cm.kg.get_conversation(conv_id2)

        assert len(conv1['context']['files_accessed']) == 1
        assert len(conv2['context']['files_accessed']) == 0


# ============================================================================
# Decision Logging Tests
# ============================================================================

@pytest.mark.unit
class TestDecisionLogging:
    """Test decision tracking."""

    def test_log_decision_basic(self, tmp_path):
        """Should log decision to conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log decision
        decision_id = cm.log_decision(
            decision='Use pytest for testing',
            rationale='Industry standard, great ecosystem',
            category='tooling'
        )

        assert decision_id is not None
        assert len(decision_id) > 0

        # Verify decision entity created
        decision_entity = cm.kg.get_entity(decision_id)
        assert decision_entity is not None
        assert decision_entity['type'] == 'decision'
        assert decision_entity['metadata']['decision'] == 'Use pytest for testing'
        assert decision_entity['metadata']['rationale'] == 'Industry standard, great ecosystem'
        assert decision_entity['metadata']['category'] == 'tooling'

        # Verify linked to conversation
        conv = cm.kg.get_conversation(conv_id)
        assert decision_id in conv['context']['decisions']

    def test_log_decision_multiple(self, tmp_path):
        """Should log multiple decisions."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log multiple decisions
        d1 = cm.log_decision('Decision 1', 'Reason 1')
        d2 = cm.log_decision('Decision 2', 'Reason 2')
        d3 = cm.log_decision('Decision 3', 'Reason 3')

        conv = cm.kg.get_conversation(conv_id)
        decisions = conv['context']['decisions']

        assert len(decisions) == 3
        assert d1 in decisions
        assert d2 in decisions
        assert d3 in decisions

    def test_log_decision_no_conversation(self, tmp_path):
        """Should fail when no active conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # No conversation
        decision_id = cm.log_decision('Decision', 'Rationale')

        assert decision_id == ""


# ============================================================================
# Command Logging Tests
# ============================================================================

@pytest.mark.unit
class TestCommandLogging:
    """Test command execution tracking."""

    def test_log_command_basic(self, tmp_path):
        """Should log command execution."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log command
        result = cm.log_command(
            command='pytest tests/',
            output='59 tests passed',
            exit_code=0
        )

        assert result is True

        conv = cm.kg.get_conversation(conv_id)
        commands = conv['context']['commands_run']

        assert len(commands) == 1
        assert commands[0]['command'] == 'pytest tests/'
        assert commands[0]['output'] == '59 tests passed'
        assert commands[0]['exit_code'] == 0

    def test_log_command_truncates_output(self, tmp_path):
        """Should truncate long output."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log command with very long output
        long_output = 'x' * 1000
        cm.log_command('test', output=long_output)

        conv = cm.kg.get_conversation(conv_id)
        commands = conv['context']['commands_run']

        # Should be truncated to 500 chars
        assert len(commands[0]['output']) == 500


# ============================================================================
# Entity Creation Logging Tests
# ============================================================================

@pytest.mark.unit
class TestEntityCreationLogging:
    """Test entity creation tracking."""

    def test_log_entity_created(self, tmp_path):
        """Should log entity creation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log entity creation (only entity_id and entity_type, no name)
        result = cm.log_entity_created(
            entity_id='entity-123',
            entity_type='project'
        )

        assert result is True

        conv = cm.kg.get_conversation(conv_id)
        entities = conv['context']['entities_created']

        assert len(entities) == 1
        assert entities[0]['id'] == 'entity-123'
        assert entities[0]['type'] == 'project'


# ============================================================================
# Context Retrieval Tests
# ============================================================================

@pytest.mark.unit
class TestContextRetrieval:
    """Test context retrieval for resume."""

    def test_get_context_for_resume(self, tmp_path):
        """Should retrieve full context for resuming."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversation with data
        conv_id = cm.start_conversation(tool='test', auto_detect=False)
        cm.log_file_access('/file1.py', 'read')
        cm.log_file_access('/file2.py', 'write')
        d1 = cm.log_decision('Decision 1', 'Rationale 1')

        # Get context
        context = cm.get_context_for_resume(conv_id)

        assert context is not None
        assert 'conversation_id' in context  # Key is conversation_id, not conversation
        assert 'files_accessed' in context
        assert 'decisions' in context
        assert 'summary' in context

        assert context['conversation_id'] == conv_id
        assert len(context['files_accessed']) == 2
        assert len(context['decisions']) == 1


# ============================================================================
# Search Tests
# ============================================================================

@pytest.mark.unit
class TestSearchConversations:
    """Test conversation search functionality."""

    def test_search_conversations_by_query(self, tmp_path):
        """Should search conversations by content."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversations with decisions
        conv1 = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_decision('Use TypeScript for frontend', 'Type safety')

        conv2 = cm.start_conversation(tool='test', thread_id='2', auto_detect=False)
        cm.log_decision('Use Python for backend', 'Great libraries')

        # Search for TypeScript
        results = cm.search_conversations(query='TypeScript', limit=10)

        # Results have structure: {'conversation': conv, 'relevance': N, 'preview': str}
        # Should find conv1
        assert any(r['conversation']['id'] == conv1 for r in results)

    def test_search_conversations_by_tool(self, tmp_path):
        """Should filter by tool."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        cm.start_conversation(tool='claude-code', thread_id='1', auto_detect=False)
        cm.start_conversation(tool='chatgpt', thread_id='2', auto_detect=False)
        cm.start_conversation(tool='claude-code', thread_id='3', auto_detect=False)

        # Search with empty query but tool filter
        # Note: search returns results only if query matches something (relevance > 0)
        # With empty query, we need to log something to make it searchable
        cm.log_decision('Decision for testing', 'Test')

        results = cm.search_conversations(query='testing', tool='claude-code', limit=10)

        # Should only find claude-code conversations
        for r in results:
            assert r['conversation']['tool'] == 'claude-code'


# ============================================================================
# Recent Conversations Tests
# ============================================================================

@pytest.mark.unit
class TestRecentConversations:
    """Test recent conversation retrieval."""

    def test_get_recent_conversations_default(self, tmp_path):
        """Should get recent conversations (last 24 hours)."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create some conversations
        for i in range(3):
            cm.start_conversation(tool=f'tool-{i}', thread_id=f't{i}', auto_detect=False)

        recent = cm.get_recent_conversations()

        assert len(recent) == 3

    def test_get_recent_conversations_with_limit(self, tmp_path):
        """Should respect limit parameter."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create 5 conversations
        for i in range(5):
            cm.start_conversation(tool=f'tool-{i}', thread_id=f't{i}', auto_detect=False)

        recent = cm.get_recent_conversations(limit=2)

        assert len(recent) == 2


# ============================================================================
# Summarization Tests
# ============================================================================

@pytest.mark.unit
class TestSummarization:
    """Test conversation summarization."""

    def test_summarize_conversation_basic(self, tmp_path):
        """Should generate summary of conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversation with activity
        conv_id = cm.start_conversation(tool='test', auto_detect=False)
        cm.log_file_access('/file1.py', 'read')
        cm.log_file_access('/file2.py', 'write')
        cm.log_decision('Decision 1', 'Reason 1')
        cm.log_command('pytest', 'passed', 0)

        # Generate summary
        summary = cm.summarize_conversation(conv_id, auto_save=True)

        assert summary is not None
        assert 'Accessed 2 files' in summary
        assert 'Made 1 decisions' in summary
        assert 'Ran 1 commands' in summary

        # Verify saved
        conv = cm.kg.get_conversation(conv_id)
        assert conv['summary'] == summary

    def test_summarize_conversation_no_save(self, tmp_path):
        """Should generate summary without saving."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)
        cm.log_file_access('/file.py', 'read')

        # Generate without saving
        summary = cm.summarize_conversation(conv_id, auto_save=False)

        assert 'Accessed 1 files' in summary

        # Should not be saved
        conv = cm.kg.get_conversation(conv_id)
        assert conv['summary'] == ''

    def test_summarize_empty_conversation(self, tmp_path):
        """Should handle conversation with no activity."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # No activity logged
        summary = cm.summarize_conversation(conv_id)

        assert summary is not None
        assert conv_id[:8] in summary

    def test_summarize_with_entities(self, tmp_path):
        """Should include entity count in summary."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Create and log entities
        entity_id = cm.kg.insert_entity({'type': 'project', 'name': 'test'})
        cm.log_entity_created(entity_id, 'project')

        summary = cm.summarize_conversation(conv_id)

        assert 'Created 1 entities' in summary

    def test_summarize_nonexistent_conversation(self, tmp_path):
        """Should handle nonexistent conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        summary = cm.summarize_conversation('nonexistent-id')

        assert summary == ""


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_log_to_nonexistent_conversation(self, tmp_path):
        """Should handle logging to nonexistent conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Try to log to nonexistent conversation
        result = cm.log_file_access('/file.py', conv_id='nonexistent-id')

        assert result is False

    def test_get_context_nonexistent_conversation(self, tmp_path):
        """Should handle nonexistent conversation gracefully."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Try to get context for nonexistent conversation
        context = cm.get_context_for_resume('nonexistent-id')

        # Should return error dict
        assert context == {'error': 'Conversation not found'}

    def test_empty_decision(self, tmp_path):
        """Should handle empty decision text."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Log empty decision
        decision_id = cm.log_decision('', '')

        # Should still create entity (name will be truncated empty string)
        assert decision_id is not None
        assert len(decision_id) > 0

    def test_very_long_decision(self, tmp_path):
        """Should handle very long decision text."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Very long decision
        long_decision = 'x' * 1000
        decision_id = cm.log_decision(long_decision, 'Rationale')

        # Should truncate name to 100 chars
        entity = cm.kg.get_entity(decision_id)
        assert len(entity['name']) == 100
        # But full text in metadata
        assert len(entity['metadata']['decision']) == 1000

    def test_log_command_no_conversation(self, tmp_path):
        """Should handle logging command without active conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # No conversation started
        result = cm.log_command('test command', 'output', 0)

        assert result is False

    def test_log_command_to_nonexistent_conversation(self, tmp_path):
        """Should handle logging to nonexistent conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        result = cm.log_command('test', 'output', 0, conv_id='nonexistent-id')

        assert result is False

    def test_log_entity_no_conversation(self, tmp_path):
        """Should handle logging entity without active conversation."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # No conversation started
        result = cm.log_entity_created('entity-id', 'project')

        assert result is False

    def test_recent_conversations_with_hours(self, tmp_path):
        """Should filter by hours parameter."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        # Create conversation
        cm.start_conversation(tool='test', thread_id='1', auto_detect=False)

        # Get recent from last 1 hour
        recent = cm.get_recent_conversations(hours=1, limit=10)

        assert len(recent) == 1

    def test_search_with_since_days(self, tmp_path):
        """Should filter search by date range."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_decision('Test decision', 'Test rationale')

        # Search within last 7 days
        results = cm.search_conversations(query='decision', since_days=7, limit=10)

        # Should find the conversation
        assert len(results) > 0

    def test_search_in_file_paths(self, tmp_path):
        """Should search file paths."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_file_access('/test/special_file.py', 'read')

        # Search for file name
        results = cm.search_conversations(query='special_file', limit=10)

        # Should find the conversation with that file
        assert len(results) > 0
        assert results[0]['conversation']['id'] == conv_id

    def test_search_in_commands(self, tmp_path):
        """Should search command text."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_command('special-pytest-test', 'output', 0)

        # Search for command
        results = cm.search_conversations(query='special-pytest', limit=10)

        # Should find the conversation
        assert len(results) > 0
        assert results[0]['conversation']['id'] == conv_id

    def test_search_in_summary(self, tmp_path):
        """Should search conversation summaries."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_file_access('/file.py', 'read')

        # Generate summary
        cm.summarize_conversation(conv_id, auto_save=True)

        # Search in summary
        results = cm.search_conversations(query='Accessed', limit=10)

        # Should find conversation by summary
        assert len(results) > 0

    def test_search_returns_preview(self, tmp_path):
        """Should include preview in search results."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', thread_id='1', auto_detect=False)
        cm.log_decision('Important decision', 'Rationale')

        results = cm.search_conversations(query='Important', limit=10)

        assert len(results) > 0
        assert 'preview' in results[0]
        assert 'relevance' in results[0]
        assert 'conversation' in results[0]

    def test_context_includes_entities(self, tmp_path):
        """Should include created entities in context."""
        kg_path = tmp_path / "test.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(tool='test', auto_detect=False)

        # Create an actual entity first
        entity_id = cm.kg.insert_entity({
            'type': 'project',
            'name': 'test-project'
        })

        # Log that it was created
        cm.log_entity_created(entity_id, 'project')

        # Get context
        context = cm.get_context_for_resume(conv_id)

        # Should include entities_created
        assert 'entities_created' in context
        assert len(context['entities_created']) == 1
        assert context['entities_created'][0]['id'] == entity_id
