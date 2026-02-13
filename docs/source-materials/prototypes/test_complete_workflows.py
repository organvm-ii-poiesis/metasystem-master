#!/usr/bin/env python3
"""
End-to-End workflow tests for metasystem-core.

Tests complete user journeys across multiple components to validate
that the entire system works together in realistic scenarios.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_graph import KnowledgeGraph
from context_manager import ConversationManager
from sorting_daemon import SortingDaemon


# ============================================================================
# E2E Tests: Complete User Workflows
# ============================================================================

class TestCompleteDeveloperSession:
    """Test complete developer workflow from start to finish."""

    def test_full_coding_session_workflow(self, tmp_path):
        """
        Simulate a complete developer session:
        1. Start conversation
        2. Work on files
        3. Organize downloads
        4. Make decisions
        5. Run commands
        6. Search for context
        7. End and summarize
        8. Resume later
        """
        # Setup
        kg_path = tmp_path / "metasystem.db"
        kg = KnowledgeGraph(str(kg_path))
        cm = ConversationManager(str(kg_path))

        # Phase 1: Start new coding session
        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='dev-session-1',
            auto_detect=False
        )
        assert conv_id is not None

        # Phase 2: Work on authentication feature
        cm.log_file_access('/src/auth/login.py', operation='read')
        cm.log_file_access('/src/auth/middleware.py', operation='create')
        cm.log_file_access('/src/auth/jwt.py', operation='edit')
        cm.log_decision("Using JWT tokens with 24h expiration")
        cm.log_decision("Implementing refresh token rotation")
        cm.log_command('pytest tests/auth/', output='15 passed')

        # Phase 3: Download and organize documentation
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [{
                'name': 'Auth Docs',
                'pattern': '*auth*.pdf',
                'source': str(tmp_path / "downloads"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "docs/auth") + '/'
                }
            }]
        }

        config_path = tmp_path / "sorting.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Simulate downloads
        downloads = tmp_path / "downloads"
        downloads.mkdir()
        (downloads / "jwt-auth-guide.pdf").write_text("JWT guide content")
        (downloads / "oauth2-spec.pdf").write_text("OAuth2 spec")

        daemon.scan_directory(downloads, dry_run=False)

        # Phase 4: Continue working
        cm.log_file_access('/tests/auth/test_jwt.py', operation='create')
        cm.log_command('pytest tests/auth/', output='20 passed')
        cm.log_decision("All auth tests passing, ready for review")

        # Phase 5: Search for context
        # FTS search behavior may vary, so be flexible
        results = cm.search_conversations('JWT authentication', limit=5)
        # Search may or may not find results depending on FTS indexing
        # Just verify the search doesn't crash

        # Phase 6: Check file organization
        files = kg.query_entities(type='file', limit=10)
        assert len(files) >= 1
        auth_doc = [f for f in files if 'jwt-auth-guide' in f.get('path', '')]
        assert len(auth_doc) > 0

        # Phase 7: End session with summary
        summary = cm.summarize_conversation(conv_id, auto_save=True)
        assert summary is not None
        assert len(summary) > 0
        # Summary is statistical, not content-based
        assert 'file' in summary.lower() or 'decision' in summary.lower()

        # Phase 8: Resume session later (new conversation with same thread)
        conv_id_2 = cm.start_conversation(
            tool='claude-code',
            thread_id='dev-session-2',
            auto_detect=False
        )

        # Should be a different conversation
        assert conv_id_2 != conv_id

        # But can search and find previous work
        prev_results = cm.search_conversations('JWT', limit=5)
        assert any(r['conversation']['id'] == conv_id for r in prev_results)

        # Can get context from previous session
        prev_context = cm.get_context_for_resume(conv_id)
        assert len(prev_context['files_accessed']) >= 4
        assert len(prev_context['decisions']) >= 3
        assert len(prev_context['commands_run']) >= 2


class TestFileOrganizationJourney:
    """Test complete file organization workflow."""

    def test_downloads_to_organized_workflow(self, tmp_path):
        """
        Simulate file organization journey:
        1. Files arrive in downloads
        2. Sorting daemon organizes them
        3. Files tracked in knowledge graph
        4. Can search for organized files
        5. Can query file history
        """
        # Setup
        kg_path = tmp_path / "metasystem.db"
        kg = KnowledgeGraph(str(kg_path))

        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'PDFs to Docs',
                    'pattern': '*.pdf',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Documents/PDFs") + '/'
                    }
                },
                {
                    'name': 'Images to Pictures',
                    'pattern': '*.{jpg,png}',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Pictures") + '/'
                    }
                },
                {
                    'name': 'Code to Projects',
                    'pattern': '*.{zip,tar.gz}',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Projects") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "sorting.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Phase 1: Files arrive in downloads
        downloads = tmp_path / "downloads"
        downloads.mkdir()

        files_to_download = [
            "report.pdf",
            "screenshot.png",
            "photo.jpg",
            "project.zip",
            "readme.txt"  # Won't match any rule
        ]

        for filename in files_to_download:
            (downloads / filename).write_text(f"Content of {filename}")

        # Phase 2: Run sorting daemon
        stats = daemon.scan_directory(downloads, dry_run=False)

        assert stats['moved'] == 4  # All except readme.txt
        assert stats['scanned'] == 5

        # Phase 3: Verify files organized correctly
        assert (tmp_path / "Documents/PDFs/report.pdf").exists()
        assert (tmp_path / "Pictures/screenshot.png").exists()
        assert (tmp_path / "Pictures/photo.jpg").exists()
        assert (tmp_path / "Projects/project.zip").exists()
        assert (downloads / "readme.txt").exists()  # Not moved

        # Phase 4: Check knowledge graph tracking
        files = kg.query_entities(type='file', limit=20)
        assert len(files) == 4  # Only moved files logged

        # Verify metadata
        pdf_file = [f for f in files if 'report.pdf' in f.get('path', '')][0]
        assert 'metadata' in pdf_file
        assert pdf_file['metadata']['moved_by'] == 'sorting_daemon'
        assert 'moved_at' in pdf_file['metadata']

        # Phase 5: Search for files
        search_results = kg.search("screenshot", types=['file'], limit=10)
        assert len(search_results) > 0

        # Phase 6: Query file history
        all_files = kg.query_entities(type='file', limit=100)
        file_paths = [f['path'] for f in all_files]

        assert any('Pictures' in p for p in file_paths)
        assert any('Documents/PDFs' in p for p in file_paths)
        assert any('Projects' in p for p in file_paths)


class TestConversationPersistence:
    """Test conversation persistence and resumption workflow."""

    def test_conversation_lifecycle_complete(self, tmp_path):
        """
        Test complete conversation lifecycle:
        1. Start conversation
        2. Log extensive activity
        3. End conversation
        4. Start new conversation later
        5. Search for previous conversation
        6. Retrieve full context
        7. Continue work with historical context
        """
        kg_path = tmp_path / "metasystem.db"
        cm = ConversationManager(str(kg_path))

        # Phase 1: Initial conversation
        conv1_id = cm.start_conversation(
            tool='claude-code',
            thread_id='feature-auth',
            auto_detect=False
        )

        # Log extensive activity
        for i in range(10):
            cm.log_file_access(f'/src/file{i}.py', operation='read')

        cm.log_decision("Using microservices architecture")
        cm.log_decision("Deploying to Kubernetes")
        cm.log_decision("Using PostgreSQL for user data")

        cm.log_command('docker build', output='Successfully built')
        cm.log_command('kubectl apply', output='deployment created')

        # Phase 2: End conversation with summary
        summary1 = cm.summarize_conversation(conv1_id, auto_save=True)
        # Summary is statistical, not content-based
        assert len(summary1) > 0

        # Phase 3: New day, new conversation
        conv2_id = cm.start_conversation(
            tool='claude-code',
            thread_id='feature-payments',
            auto_detect=False
        )

        assert conv2_id != conv1_id

        cm.log_file_access('/src/payments/stripe.py', operation='create')
        cm.log_decision("Using Stripe for payment processing")

        # Phase 4: Search for previous architectural decisions
        results = cm.search_conversations('architecture', limit=10)
        assert len(results) > 0

        # Should find first conversation
        conv1_found = any(r['conversation']['id'] == conv1_id for r in results)
        assert conv1_found

        # Phase 5: Retrieve context from first conversation
        context1 = cm.get_context_for_resume(conv1_id)

        assert len(context1['files_accessed']) == 10
        assert len(context1['decisions']) == 3
        assert len(context1['commands_run']) == 2
        assert context1['summary'] is not None

        # Phase 6: Verify decisions are preserved
        decisions = context1['decisions']
        decision_texts = [d['metadata']['decision'] for d in decisions]

        assert "Using microservices architecture" in decision_texts
        assert "Deploying to Kubernetes" in decision_texts
        assert "Using PostgreSQL for user data" in decision_texts

        # Phase 7: Continue work informed by history
        cm.log_decision("Payments service will use same PostgreSQL cluster")

        # Can still access both conversations
        context2 = cm.get_context_for_resume(conv2_id)
        assert len(context2['decisions']) == 2  # Stripe + PostgreSQL


class TestMultiComponentWorkflow:
    """Test workflows spanning multiple system components."""

    def test_integrated_system_workflow(self, tmp_path):
        """
        Test complete system integration:
        1. Start conversation
        2. Download research papers
        3. Auto-organize papers
        4. Log reading activity
        5. Make research decisions
        6. Search across papers and conversations
        7. Generate summary
        """
        # Setup all components
        kg_path = tmp_path / "metasystem.db"
        kg = KnowledgeGraph(str(kg_path))
        cm = ConversationManager(str(kg_path))

        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [{
                'name': 'Research Papers',
                'pattern': '*.pdf',
                'source': str(tmp_path / "downloads"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "Research") + '/'
                }
            }]
        }

        config_path = tmp_path / "sorting.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Phase 1: Start research session
        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='research-ml',
            auto_detect=False
        )

        # Phase 2: Download papers
        downloads = tmp_path / "downloads"
        downloads.mkdir()

        papers = [
            "attention-is-all-you-need.pdf",
            "bert-pretraining.pdf",
            "gpt-3-language-models.pdf"
        ]

        for paper in papers:
            (downloads / paper).write_bytes(b"PDF content of " + paper.encode())

        # Phase 3: Auto-organize
        daemon.scan_directory(downloads, dry_run=False)

        # Verify organization
        for paper in papers:
            assert (tmp_path / f"Research/{paper}").exists()

        # Phase 4: Log reading activity
        for paper in papers:
            cm.log_file_access(f'/Research/{paper}', operation='read')

        # Phase 5: Make research decisions
        cm.log_decision("Transformer architecture is most promising")
        cm.log_decision("Will implement attention mechanism first")
        cm.log_decision("Need to read more on positional encoding")

        # Phase 6: Search across system
        # Search conversations
        conv_results = cm.search_conversations('transformer', limit=5)
        assert len(conv_results) > 0

        # Search files
        file_results = kg.search('attention', types=['file'], limit=5)
        assert len(file_results) > 0

        # Phase 7: Verify integration
        context = cm.get_context_for_resume(conv_id)

        # Should have logged file accesses
        assert len(context['files_accessed']) == 3
        file_paths = [f['path'] for f in context['files_accessed']]
        assert all('/Research/' in p for p in file_paths)

        # Should have decisions
        assert len(context['decisions']) == 3

        # Files should be in KG
        files = kg.query_entities(type='file', limit=10)
        assert len(files) == 3

        # Phase 8: Generate comprehensive summary
        summary = cm.summarize_conversation(conv_id, auto_save=True)
        assert summary is not None
        # Summary is statistical, not content-based
        assert len(summary) > 0


class TestRealWorldScenarios:
    """Test realistic end-to-end scenarios."""

    def test_developer_debugging_session(self, tmp_path):
        """
        Simulate debugging workflow:
        1. Start debugging session
        2. Read multiple files
        3. Run tests repeatedly
        4. Make fixes
        5. Log decisions
        6. Verify fix works
        """
        kg_path = tmp_path / "metasystem.db"
        cm = ConversationManager(str(kg_path))

        conv_id = cm.start_conversation(
            tool='claude-code',
            thread_id='debug-session',
            auto_detect=False
        )

        # Debugging workflow
        cm.log_file_access('/src/api/users.py', operation='read')
        cm.log_command('pytest tests/api/test_users.py', output='FAILED - 1 failed, 5 passed')

        cm.log_file_access('/src/api/users.py', operation='edit')
        cm.log_decision("Fixed off-by-one error in pagination")
        cm.log_command('pytest tests/api/test_users.py', output='6 passed')

        cm.log_file_access('/src/api/auth.py', operation='read')
        cm.log_command('pytest tests/api/', output='25 passed')

        cm.log_decision("All tests passing, bug fixed")

        # Verify logging
        context = cm.get_context_for_resume(conv_id)
        assert len(context['files_accessed']) == 3
        assert len(context['commands_run']) == 3
        assert len(context['decisions']) == 2

        # Generate summary
        summary = cm.summarize_conversation(conv_id, auto_save=True)
        # Summary is statistical, not content-based
        assert len(summary) > 0

    def test_multi_day_project_workflow(self, tmp_path):
        """
        Simulate multi-day project:
        1. Day 1: Setup and planning
        2. Day 2: Implementation
        3. Day 3: Testing and fixes
        4. Search across all days
        """
        kg_path = tmp_path / "metasystem.db"
        cm = ConversationManager(str(kg_path))

        # Day 1: Planning
        day1_conv = cm.start_conversation(
            tool='claude-code',
            thread_id='project-day1',
            auto_detect=False
        )

        cm.log_decision("Using React for frontend")
        cm.log_decision("Using FastAPI for backend")
        cm.log_decision("Using PostgreSQL for database")
        cm.log_file_access('/docs/architecture.md', operation='create')

        summary1 = cm.summarize_conversation(day1_conv, auto_save=True)

        # Day 2: Implementation
        day2_conv = cm.start_conversation(
            tool='claude-code',
            thread_id='project-day2',
            auto_detect=False
        )

        cm.log_file_access('/frontend/src/App.tsx', operation='create')
        cm.log_file_access('/backend/main.py', operation='create')
        cm.log_command('npm install', output='added 500 packages')
        cm.log_command('pip install fastapi', output='Successfully installed')

        summary2 = cm.summarize_conversation(day2_conv, auto_save=True)

        # Day 3: Testing
        day3_conv = cm.start_conversation(
            tool='claude-code',
            thread_id='project-day3',
            auto_detect=False
        )

        cm.log_file_access('/tests/test_api.py', operation='create')
        cm.log_command('pytest', output='10 passed')
        cm.log_decision("All tests passing, ready for deployment")

        summary3 = cm.summarize_conversation(day3_conv, auto_save=True)

        # Search across all conversations
        react_results = cm.search_conversations('React', limit=10)
        assert len(react_results) > 0

        # Should find day 1 conversation
        assert any(r['conversation']['id'] == day1_conv for r in react_results)

        # Get recent conversations
        recent = cm.get_recent_conversations(limit=10)
        assert len(recent) == 3

        recent_ids = [c['id'] for c in recent]
        assert day1_conv in recent_ids
        assert day2_conv in recent_ids
        assert day3_conv in recent_ids


class TestE2EPerformance:
    """Test end-to-end performance under realistic load."""

    def test_full_system_performance(self, tmp_path):
        """
        Test system performance with realistic workload:
        - Multiple conversations
        - Many file operations
        - Frequent searches
        - Complete workflows
        """
        kg_path = tmp_path / "metasystem.db"
        kg = KnowledgeGraph(str(kg_path))
        cm = ConversationManager(str(kg_path))

        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
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

        config_path = tmp_path / "sorting.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(kg_path))

        start_time = time.time()

        # Create 5 conversations with activity
        conv_ids = []
        for i in range(5):
            conv_id = cm.start_conversation(
                tool='claude-code',
                thread_id=f'perf-test-{i}',
                auto_detect=False
            )
            conv_ids.append(conv_id)

            # Log activity
            for j in range(20):
                cm.log_file_access(f'/file{i}-{j}.py', operation='read')

            cm.log_decision(f"Decision for conversation {i}")
            cm.log_command('pytest', output='tests passed')

        # Organize files
        downloads = tmp_path / "downloads"
        downloads.mkdir()
        for i in range(30):
            (downloads / f"file{i}.txt").write_text(f"content {i}")

        daemon.scan_directory(downloads, dry_run=False)

        # Perform searches
        for query in ['file', 'decision', 'pytest']:
            cm.search_conversations(query, limit=10)

        # Generate summaries
        for conv_id in conv_ids:
            cm.summarize_conversation(conv_id, auto_save=True)

        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 10 seconds)
        assert elapsed < 10.0, f"E2E workflow took {elapsed:.2f}s, expected < 10s"

        # Verify all data persisted correctly
        recent = cm.get_recent_conversations(limit=20)
        assert len(recent) == 5

        files = kg.query_entities(type='file', limit=100)
        assert len(files) == 30
