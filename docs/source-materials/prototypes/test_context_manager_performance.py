#!/usr/bin/env python3
"""
Performance benchmarks for ConversationManager operations.

Establishes baseline performance metrics for:
- Conversation lifecycle
- File access logging
- Decision logging
- Command logging
- Search operations
- Context retrieval
"""

import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from context_manager import ConversationManager


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def benchmark_cm(tmp_path):
    """Create a ConversationManager for benchmarking."""
    kg_path = tmp_path / "benchmark.db"
    cm = ConversationManager(str(kg_path))
    return cm


@pytest.fixture
def active_conversation_cm(tmp_path):
    """Create ConversationManager with active conversation."""
    kg_path = tmp_path / "benchmark.db"
    cm = ConversationManager(str(kg_path))
    cm.start_conversation(tool='claude-code', thread_id='bench-thread', auto_detect=False)
    return cm


@pytest.fixture
def populated_cm(tmp_path):
    """Create ConversationManager with multiple conversations."""
    kg_path = tmp_path / "benchmark.db"
    cm = ConversationManager(str(kg_path))

    # Create 50 conversations with activity
    for i in range(50):
        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id=f'bench-thread-{i}',
            auto_detect=False
        )

        # Log activity for each conversation
        for j in range(10):
            cm.log_file_access(f'/file_{i}_{j}.py', operation='read')

        cm.log_decision(f'Decision for conversation {i}')
        cm.log_command(f'command_{i}', output=f'output_{i}')

    return cm


# ============================================================================
# Conversation Lifecycle Benchmarks
# ============================================================================

class TestConversationLifecycleBenchmarks:
    """Benchmark conversation lifecycle operations."""

    def test_start_conversation_benchmark(self, benchmark, benchmark_cm):
        """Benchmark starting a new conversation."""
        def start_conv():
            return benchmark_cm.start_conversation(
                tool='claude-code',
                thread_id=f'bench-{benchmark.stats.stats.iterations}',
                auto_detect=False
            )

        result = benchmark(start_conv)
        assert result is not None

    def test_get_context_for_resume_benchmark(self, benchmark, populated_cm):
        """Benchmark getting context for resume."""
        # Get a conversation ID
        recent = populated_cm.get_recent_conversations(limit=1)
        conv_id = recent[0]['id']

        result = benchmark(populated_cm.get_context_for_resume, conv_id)
        assert result is not None
        assert 'conversation_id' in result

    def test_summarize_conversation_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark conversation summarization."""
        # Get current conversation
        conv_id = active_conversation_cm.current_conversation_id

        # Log some activity
        for i in range(20):
            active_conversation_cm.log_file_access(f'/file_{i}.py', operation='read')

        result = benchmark(active_conversation_cm.summarize_conversation, conv_id, auto_save=False)
        assert result is not None


# ============================================================================
# Logging Benchmarks
# ============================================================================

class TestLoggingBenchmarks:
    """Benchmark logging operations."""

    def test_log_file_access_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark file access logging."""
        result = benchmark(
            active_conversation_cm.log_file_access,
            '/src/benchmark.py',
            operation='read'
        )
        # log_file_access doesn't return a value, just verify no exception

    def test_log_decision_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark decision logging."""
        result = benchmark(
            active_conversation_cm.log_decision,
            'Benchmark decision: Using optimal algorithm'
        )
        # log_decision doesn't return a value

    def test_log_command_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark command logging."""
        result = benchmark(
            active_conversation_cm.log_command,
            'pytest tests/',
            output='100 passed in 2.5s'
        )
        # log_command doesn't return a value

    def test_log_entity_created_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark entity creation logging."""
        result = benchmark(
            active_conversation_cm.log_entity_created,
            'ent-123',
            'file',
            '/src/new_file.py'
        )
        # log_entity_created doesn't return a value

    def test_bulk_file_logging_benchmark(self, benchmark, active_conversation_cm):
        """Benchmark logging 100 file accesses."""
        def bulk_log():
            for i in range(100):
                active_conversation_cm.log_file_access(f'/file_{i}.py', operation='read')

        benchmark(bulk_log)


# ============================================================================
# Search Benchmarks
# ============================================================================

class TestSearchBenchmarks:
    """Benchmark search operations."""

    def test_search_conversations_simple_benchmark(self, benchmark, populated_cm):
        """Benchmark simple conversation search."""
        result = benchmark(populated_cm.search_conversations, 'decision', limit=10)
        assert isinstance(result, list)

    def test_search_conversations_complex_benchmark(self, benchmark, populated_cm):
        """Benchmark complex conversation search."""
        result = benchmark(
            populated_cm.search_conversations,
            'decision command',
            limit=20
        )
        assert isinstance(result, list)

    def test_get_recent_conversations_benchmark(self, benchmark, populated_cm):
        """Benchmark getting recent conversations."""
        result = benchmark(populated_cm.get_recent_conversations, limit=20)
        assert isinstance(result, list)
        assert len(result) > 0


# ============================================================================
# Context Retrieval Benchmarks
# ============================================================================

class TestContextRetrievalBenchmarks:
    """Benchmark context retrieval operations."""

    def test_get_full_context_benchmark(self, benchmark, populated_cm):
        """Benchmark retrieving full context."""
        # Get a conversation with lots of data
        recent = populated_cm.get_recent_conversations(limit=1)
        conv_id = recent[0]['id']

        result = benchmark(populated_cm.get_context_for_resume, conv_id)
        assert 'files_accessed' in result
        assert 'decisions' in result
        assert 'commands_run' in result

    def test_get_context_with_large_history_benchmark(self, benchmark, tmp_path):
        """Benchmark context retrieval with large file access history."""
        kg_path = tmp_path / "large_history.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='large-history',
            auto_detect=False
        )

        # Log 500 file accesses
        for i in range(500):
            cm.log_file_access(f'/file_{i}.py', operation='read')

        result = benchmark(cm.get_context_for_resume, conv_id)
        assert len(result['files_accessed']) == 500


# ============================================================================
# Concurrent Operations Benchmarks
# ============================================================================

class TestConcurrentBenchmarks:
    """Benchmark concurrent operations."""

    def test_multiple_conversations_benchmark(self, benchmark, tmp_path):
        """Benchmark managing multiple conversations."""
        kg_path = tmp_path / "multi_conv.db"
        cm = ConversationManager(str(kg_path))

        def multi_conv():
            conv_ids = []
            for i in range(10):
                conv_id = cm.start_conversation(
                    tool='claude-code',
                    thread_id=f'multi-{i}',
                    auto_detect=False
                )
                conv_ids.append(conv_id)

                # Log some activity
                cm.log_file_access(f'/file_{i}.py', operation='read')
                cm.log_decision(f'Decision {i}')

            return len(conv_ids)

        result = benchmark(multi_conv)
        assert result == 10

    def test_search_across_many_conversations_benchmark(self, benchmark, populated_cm):
        """Benchmark searching across many conversations."""
        # populated_cm already has 50 conversations
        result = benchmark(
            populated_cm.search_conversations,
            'decision',
            limit=50
        )
        assert isinstance(result, list)


# ============================================================================
# End-to-End Workflow Benchmarks
# ============================================================================

class TestWorkflowBenchmarks:
    """Benchmark complete workflow operations."""

    def test_full_conversation_workflow_benchmark(self, benchmark, tmp_path):
        """Benchmark complete conversation workflow."""
        kg_path = tmp_path / "workflow.db"

        def full_workflow():
            cm = ConversationManager(str(kg_path))

            # Start conversation
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id='workflow-bench',
                auto_detect=False
            )

            # Log activity
            for i in range(20):
                cm.log_file_access(f'/file_{i}.py', operation='read')

            cm.log_decision('Using Factory pattern')
            cm.log_command('pytest', output='20 passed')

            # Get context
            context = cm.get_context_for_resume(conv_id)

            # Summarize
            summary = cm.summarize_conversation(conv_id, auto_save=True)

            return len(context['files_accessed'])

        result = benchmark(full_workflow)
        assert result == 20

    def test_conversation_resume_workflow_benchmark(self, benchmark, tmp_path):
        """Benchmark conversation resume workflow."""
        kg_path = tmp_path / "resume.db"
        cm = ConversationManager(str(kg_path))

        # Create initial conversation
        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='resume-bench',
            auto_detect=False
        )

        # Log extensive activity
        for i in range(50):
            cm.log_file_access(f'/file_{i}.py', operation='read')

        for i in range(10):
            cm.log_decision(f'Decision {i}')

        def resume_workflow():
            # Get full context
            context = cm.get_context_for_resume(conv_id)

            # Verify context
            files = len(context['files_accessed'])
            decisions = len(context['decisions'])

            return files + decisions

        result = benchmark(resume_workflow)
        assert result == 60  # 50 files + 10 decisions
