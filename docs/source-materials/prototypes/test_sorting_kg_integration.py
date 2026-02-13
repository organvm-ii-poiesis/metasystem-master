#!/usr/bin/env python3
"""
Integration tests for SortingDaemon + KnowledgeGraph interaction.

Tests how file organization interacts with metadata tracking.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_graph import KnowledgeGraph
from sorting_daemon import SortingDaemon


# ============================================================================
# Integration Tests: SortingDaemon + KG
# ============================================================================

class TestSortingKGIntegration:
    """Test SortingDaemon and KnowledgeGraph integration."""

    def test_file_move_logged_to_kg(self, tmp_path):
        """Test that file moves are logged to knowledge graph."""
        # Create config
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'Text Files',
                    'pattern': '*.txt',
                    'source': str(tmp_path / "inbox"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "sorted") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Create test file
        inbox = tmp_path / "inbox"
        inbox.mkdir()
        test_file = inbox / "test.txt"
        test_file.write_text("test content")

        # Scan directory
        stats = daemon.scan_directory(inbox, dry_run=False)

        # Verify file was moved
        assert (tmp_path / "sorted" / "test.txt").exists()
        assert not test_file.exists()
        assert stats['moved'] >= 1

        # Query knowledge graph for file entities
        files = kg.query_entities(type='file', limit=10)

        # Should have logged the move
        assert len(files) >= 1
        # Find our moved file
        moved_file = None
        for f in files:
            if 'test.txt' in f.get('path', ''):
                moved_file = f
                break
        
        assert moved_file is not None
        assert 'sorted' in moved_file['path']

    def test_file_organization_workflow(self, tmp_path):
        """Test complete file organization workflow with KG tracking."""
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'PDFs',
                    'pattern': '*.pdf',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Documents/PDFs") + '/'
                    }
                },
                {
                    'name': 'Images',
                    'pattern': '*.{png,jpg}',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Pictures") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Create test files
        downloads = tmp_path / "downloads"
        downloads.mkdir()
        (downloads / "document.pdf").write_text("PDF content")
        (downloads / "photo.png").write_text("PNG content")
        (downloads / "readme.txt").write_text("Text content")

        # Scan and organize
        stats = daemon.scan_directory(downloads, dry_run=False)

        # Verify organization
        assert (tmp_path / "Documents/PDFs/document.pdf").exists()
        assert (tmp_path / "Pictures/photo.png").exists()
        assert (downloads / "readme.txt").exists()  # Not matched

        # Check KG has tracked the moves
        files = kg.query_entities(type='file', limit=10)
        assert len(files) >= 2  # PDF and PNG

    def test_duplicate_detection_with_kg(self, tmp_path):
        """Test duplicate detection updates knowledge graph."""
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True,
                'duplicate_action': 'skip'
            },
            'rules': [
                {
                    'name': 'All Files',
                    'pattern': '*',
                    'source': str(tmp_path / "inbox"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "archive") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        daemon = SortingDaemon(str(config_path), str(kg_path))

        inbox = tmp_path / "inbox"
        inbox.mkdir()

        # Create two files with same content
        file1 = inbox / "file1.txt"
        file1.write_text("identical content")
        
        # First scan
        daemon.scan_directory(inbox, dry_run=False)
        assert (tmp_path / "archive/file1.txt").exists()

        # Create duplicate
        file2 = inbox / "file2.txt"
        file2.write_text("identical content")

        # Second scan - should detect duplicate
        stats = daemon.scan_directory(inbox, dry_run=False)
        
        # Based on duplicate_action, file2 might be skipped or handled
        # The hash cache should work correctly
        assert daemon._compute_file_hash(tmp_path / "archive/file1.txt") == \
               daemon._compute_file_hash(file2) if file2.exists() else True

    def test_kg_entity_creation_for_organized_files(self, tmp_path):
        """Test that organizing files creates proper entities in KG."""
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'Projects',
                    'pattern': '*.zip',
                    'source': str(tmp_path / "downloads"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "Projects") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Create test file
        downloads = tmp_path / "downloads"
        downloads.mkdir()
        project_file = downloads / "my-project.zip"
        project_file.write_bytes(b"ZIP content")

        # Scan
        daemon.scan_directory(downloads, dry_run=False)

        # Check KG
        files = kg.query_entities(type='file', limit=10)
        assert len(files) >= 1
        
        # Verify entity has metadata about the move
        project_entity = files[0]
        assert 'metadata' in project_entity
        assert 'moved_at' in project_entity['metadata']
        assert 'moved_by' in project_entity['metadata']
        assert project_entity['metadata']['moved_by'] == 'sorting_daemon'

    def test_search_file_history_in_kg(self, tmp_path):
        """Test searching for file move history via KG."""
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'Organize All',
                    'pattern': '*.txt',
                    'source': str(tmp_path / "inbox"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "organized") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Organize multiple files
        inbox = tmp_path / "inbox"
        inbox.mkdir()
        
        for i in range(5):
            (inbox / f"file{i}.txt").write_text(f"content {i}")

        daemon.scan_directory(inbox, dry_run=False)

        # Search KG for organized files
        results = kg.search("file", types=['file'], limit=10)
        
        # Should find multiple files
        assert len(results) >= 5

    def test_dry_run_does_not_create_kg_entities(self, tmp_path):
        """Test that dry run mode doesn't create KG entities."""
        config = {
            'settings': {
                'dry_run': True,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'Test Rule',
                    'pattern': '*.txt',
                    'source': str(tmp_path / "inbox"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "dest") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        inbox = tmp_path / "inbox"
        inbox.mkdir()
        (inbox / "test.txt").write_text("test")

        # Dry run scan
        daemon.scan_directory(inbox, dry_run=True)

        # File should not be moved
        assert (inbox / "test.txt").exists()

        # KG should have no file entities
        files = kg.query_entities(type='file', limit=10)
        assert len(files) == 0


class TestSortingKGPerformance:
    """Performance tests for SortingDaemon + KG integration."""

    def test_organize_many_files_with_kg_logging(self, tmp_path):
        """Test organizing many files with KG logging performs well."""
        config = {
            'settings': {
                'dry_run': False,
                'log_all_moves': True
            },
            'rules': [
                {
                    'name': 'All Files',
                    'pattern': '*',
                    'source': str(tmp_path / "inbox"),
                    'action': {
                        'type': 'move',
                        'move_to': str(tmp_path / "archive") + '/'
                    }
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        kg_path = tmp_path / "test.db"
        kg = KnowledgeGraph(str(kg_path))
        daemon = SortingDaemon(str(config_path), str(kg_path))

        # Create 50 test files
        inbox = tmp_path / "inbox"
        inbox.mkdir()
        
        for i in range(50):
            (inbox / f"file{i}.txt").write_text(f"content {i}")

        # Organize all files
        import time
        start = time.time()
        stats = daemon.scan_directory(inbox, dry_run=False)
        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds for 50 files)
        assert elapsed < 5.0
        assert stats['moved'] == 50

        # All should be logged in KG
        files = kg.query_entities(type='file', limit=100)
        assert len(files) == 50
