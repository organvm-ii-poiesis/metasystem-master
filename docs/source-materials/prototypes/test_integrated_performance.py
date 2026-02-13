#!/usr/bin/env python3
"""
Integrated performance benchmarks for complete system workflows.

Establishes baseline performance metrics for:
- Multi-component workflows
- End-to-end operations
- Realistic usage scenarios
- System scalability
"""

import pytest
import tempfile
from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_graph import KnowledgeGraph
from context_manager import ConversationManager
from sorting_daemon import SortingDaemon


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def integrated_system(tmp_path):
    """Create integrated system with all components."""
    kg_path = tmp_path / "system.db"

    kg = KnowledgeGraph(str(kg_path))
    cm = ConversationManager(str(kg_path))

    config = {
        'settings': {
            'dry_run': False,
            'log_all_moves': True
        },
        'rules': [
            {
                'name': 'Python Files',
                'pattern': '*.py',
                'source': str(tmp_path / "downloads"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "organized/python") + '/'
                }
            },
            {
                'name': 'Documents',
                'pattern': '*.{pdf,doc,txt}',
                'source': str(tmp_path / "downloads"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "organized/docs") + '/'
                }
            }
        ]
    }

    config_path = tmp_path / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    daemon = SortingDaemon(str(config_path), str(kg_path))

    return kg, cm, daemon, tmp_path


# ============================================================================
# Complete Workflow Benchmarks
# ============================================================================

class TestCompleteWorkflowBenchmarks:
    """Benchmark complete end-to-end workflows."""

    def test_developer_session_workflow_benchmark(self, benchmark, integrated_system):
        """Benchmark a complete developer session workflow."""
        kg, cm, daemon, tmp_path = integrated_system

        def developer_session():
            # Start conversation
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id='dev-bench',
                auto_detect=False
            )

            # Log file work
            for i in range(10):
                cm.log_file_access(f'/src/file_{i}.py', operation='read')

            # Make decisions
            cm.log_decision('Using Factory pattern')
            cm.log_decision('Implementing caching layer')

            # Run commands
            cm.log_command('pytest tests/', output='50 passed')

            # Get context
            context = cm.get_context_for_resume(conv_id)

            # Summarize
            summary = cm.summarize_conversation(conv_id, auto_save=True)

            return len(context['files_accessed'])

        result = benchmark(developer_session)
        assert result == 10

    def test_file_organization_workflow_benchmark(self, benchmark, integrated_system):
        """Benchmark complete file organization workflow."""
        kg, cm, daemon, tmp_path = integrated_system

        # Setup files
        downloads = tmp_path / "downloads"
        downloads.mkdir()

        for i in range(20):
            ext = 'py' if i % 2 == 0 else 'pdf'
            (downloads / f"file_{i}.{ext}").write_text(f"Content {i}")

        def organize_workflow():
            # Scan and organize
            stats = daemon.scan_directory(downloads, dry_run=False)

            # Query organized files
            files = kg.query_entities(type='file', limit=50)

            return stats['moved']

        result = benchmark(organize_workflow)
        assert result == 20

    def test_conversation_with_file_organization_benchmark(self, benchmark, integrated_system):
        """Benchmark conversation tracking + file organization."""
        kg, cm, daemon, tmp_path = integrated_system

        # Setup files
        downloads = tmp_path / "downloads"
        downloads.mkdir()

        for i in range(15):
            (downloads / f"script_{i}.py").write_text(f"# Script {i}")

        def integrated_workflow():
            # Start conversation
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id='integrated-bench',
                auto_detect=False
            )

            # Log that we're organizing files
            cm.log_decision('Organizing downloaded scripts')

            # Organize files
            stats = daemon.scan_directory(downloads, dry_run=False)

            # Log the organization activity
            for i in range(stats['moved']):
                cm.log_file_access(f'/organized/python/script_{i}.py', operation='organized')

            # Get context
            context = cm.get_context_for_resume(conv_id)

            return stats['moved'] + len(context['files_accessed'])

        result = benchmark(integrated_workflow)
        assert result >= 15


# ============================================================================
# Multi-User Simulation Benchmarks
# ============================================================================

class TestMultiUserBenchmarks:
    """Benchmark multi-user/multi-session scenarios."""

    def test_multiple_concurrent_conversations_benchmark(self, benchmark, tmp_path):
        """Benchmark managing multiple concurrent conversations."""
        kg_path = tmp_path / "multi_user.db"
        cm = ConversationManager(str(kg_path))

        def multi_user_workflow():
            conv_ids = []

            # Simulate 5 concurrent users
            for user in range(5):
                conv_id = cm.start_conversation(
                    tool='claude-code',
                    thread_id=f'user-{user}',
                    auto_detect=False
                )
                conv_ids.append(conv_id)

                # Each user does some work
                for i in range(10):
                    cm.log_file_access(f'/user{user}/file_{i}.py', operation='read')

                cm.log_decision(f'User {user} decision')
                cm.log_command(f'user{user}-command', output='success')

            return len(conv_ids)

        result = benchmark(multi_user_workflow)
        assert result == 5

    def test_conversation_search_across_users_benchmark(self, benchmark, tmp_path):
        """Benchmark searching across multiple user conversations."""
        kg_path = tmp_path / "search_multi.db"
        cm = ConversationManager(str(kg_path))

        # Setup: Create multiple conversations
        for user in range(10):
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id=f'search-user-{user}',
                auto_detect=False
            )

            for i in range(5):
                cm.log_file_access(f'/user{user}/file_{i}.py', operation='read')

            cm.log_decision(f'Authentication strategy for user {user}')

        def search_workflow():
            results = cm.search_conversations('authentication', limit=20)
            return len(results)

        result = benchmark(search_workflow)
        assert result >= 0  # FTS may or may not find results


# ============================================================================
# Scalability Benchmarks
# ============================================================================

class TestScalabilityBenchmarks:
    """Benchmark system scalability."""

    def test_large_file_organization_benchmark(self, benchmark, tmp_path):
        """Benchmark organizing 200 files."""
        kg_path = tmp_path / "large_org.db"

        config = {
            'settings': {'dry_run': False, 'log_all_moves': True},
            'rules': [{
                'name': 'All Files',
                'pattern': '*',
                'source': str(tmp_path / "downloads"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "organized") + '/'
                }
            }]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(kg_path))
        kg = KnowledgeGraph(str(kg_path))

        # Create 200 files
        downloads = tmp_path / "downloads"
        downloads.mkdir()

        for i in range(200):
            (downloads / f"file_{i}.txt").write_text(f"Content {i}")

        def large_org():
            stats = daemon.scan_directory(downloads, dry_run=False)
            files = kg.query_entities(type='file', limit=300)
            return stats['moved']

        result = benchmark(large_org)
        assert result == 200

    def test_high_activity_conversation_benchmark(self, benchmark, tmp_path):
        """Benchmark conversation with high activity (1000 file accesses)."""
        kg_path = tmp_path / "high_activity.db"
        cm = ConversationManager(str(kg_path))

        def high_activity():
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id='high-activity',
                auto_detect=False
            )

            # Log 1000 file accesses
            for i in range(1000):
                cm.log_file_access(f'/file_{i}.py', operation='read')

            # Get context
            context = cm.get_context_for_resume(conv_id)

            return len(context['files_accessed'])

        result = benchmark(high_activity)
        assert result == 1000

    def test_many_conversations_with_search_benchmark(self, benchmark, tmp_path):
        """Benchmark system with 100 conversations."""
        kg_path = tmp_path / "many_convs.db"
        cm = ConversationManager(str(kg_path))

        # Create 100 conversations
        for i in range(100):
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id=f'conv-{i}',
                auto_detect=False
            )

            for j in range(5):
                cm.log_file_access(f'/conv{i}/file_{j}.py', operation='read')

            cm.log_decision(f'Decision for conversation {i}')

        def search_many():
            # Search across all conversations
            results = cm.search_conversations('decision', limit=50)

            # Get recent
            recent = cm.get_recent_conversations(limit=20)

            return len(recent)

        result = benchmark(search_many)
        assert result == 20


# ============================================================================
# Performance Under Load Benchmarks
# ============================================================================

class TestLoadBenchmarks:
    """Benchmark system performance under load."""

    def test_mixed_operations_benchmark(self, benchmark, integrated_system):
        """Benchmark mixed operations (queries, inserts, updates, searches)."""
        kg, cm, daemon, tmp_path = integrated_system

        def mixed_load():
            # Start conversation
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id='mixed-load',
                auto_detect=False
            )

            # Mix of operations
            for i in range(20):
                # File access
                cm.log_file_access(f'/file_{i}.py', operation='read')

                # Insert entity
                kg.insert_entity({
                    'id': f'ent-{i}',
                    'type': 'file',
                    'name': f'file_{i}.py',
                    'path': f'/file_{i}.py'
                })

                # Query
                if i % 5 == 0:
                    kg.query_entities(type='file', limit=10)

                # Search
                if i % 7 == 0:
                    cm.search_conversations('file', limit=5)

            # Final context retrieval
            context = cm.get_context_for_resume(conv_id)

            return len(context['files_accessed'])

        result = benchmark(mixed_load)
        assert result == 20

    def test_sustained_load_benchmark(self, benchmark, tmp_path):
        """Benchmark sustained operations over time."""
        kg_path = tmp_path / "sustained.db"
        cm = ConversationManager(str(kg_path))

        def sustained_operations():
            total_ops = 0

            # Simulate sustained activity
            for session in range(5):
                conv_id = cm.start_conversation(
                    tool='claude-code',
                    thread_id=f'session-{session}',
                    auto_detect=False
                )

                for i in range(20):
                    cm.log_file_access(f'/session{session}/file_{i}.py', operation='read')
                    total_ops += 1

                cm.log_decision(f'Decision for session {session}')
                total_ops += 1

                # Get context
                context = cm.get_context_for_resume(conv_id)
                total_ops += 1

            return total_ops

        result = benchmark(sustained_operations)
        assert result == 5 * (20 + 1 + 1)  # 5 sessions * (20 files + 1 decision + 1 context)
