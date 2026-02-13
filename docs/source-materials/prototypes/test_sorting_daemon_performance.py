#!/usr/bin/env python3
"""
Performance benchmarks for SortingDaemon operations.

Establishes baseline performance metrics for:
- File scanning
- Pattern matching
- File classification
- Directory organization
- Duplicate detection
- Bulk operations
"""

import pytest
import tempfile
from pathlib import Path
import sys
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sorting_daemon import SortingDaemon


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def benchmark_daemon(tmp_path):
    """Create a SortingDaemon for benchmarking."""
    config = {
        'settings': {
            'dry_run': True,
            'log_all_moves': False
        },
        'rules': [
            {
                'name': 'Text Files',
                'pattern': '*.txt',
                'source': str(tmp_path / "source"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "dest/text") + '/'
                }
            },
            {
                'name': 'Python Files',
                'pattern': '*.py',
                'source': str(tmp_path / "source"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "dest/python") + '/'
                }
            },
            {
                'name': 'Images',
                'pattern': '*.{jpg,png,gif}',
                'source': str(tmp_path / "source"),
                'action': {
                    'type': 'move',
                    'move_to': str(tmp_path / "dest/images") + '/'
                }
            }
        ]
    }

    config_path = tmp_path / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)

    kg_path = tmp_path / "benchmark.db"
    daemon = SortingDaemon(str(config_path), str(kg_path))

    return daemon, tmp_path


@pytest.fixture
def daemon_with_files(tmp_path):
    """Create daemon with 100 test files."""
    config = {
        'settings': {
            'dry_run': True,
            'log_all_moves': False
        },
        'rules': [
            {
                'name': 'All Files',
                'pattern': '*',
                'source': str(tmp_path / "source"),
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

    kg_path = tmp_path / "benchmark.db"
    daemon = SortingDaemon(str(config_path), str(kg_path))

    # Create 100 test files
    source = tmp_path / "source"
    source.mkdir()

    for i in range(100):
        ext = ['txt', 'py', 'jpg', 'pdf', 'md'][i % 5]
        (source / f"file_{i}.{ext}").write_text(f"Content {i}")

    return daemon, source


# ============================================================================
# Scanning Benchmarks
# ============================================================================

class TestScanningBenchmarks:
    """Benchmark file scanning operations."""

    def test_scan_empty_directory_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark scanning an empty directory."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 0

    def test_scan_small_directory_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark scanning directory with 10 files."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        # Create 10 files
        for i in range(10):
            (source / f"file_{i}.txt").write_text(f"Content {i}")

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 10

    def test_scan_medium_directory_benchmark(self, benchmark, daemon_with_files):
        """Benchmark scanning directory with 100 files."""
        daemon, source = daemon_with_files

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 100

    def test_scan_large_directory_benchmark(self, benchmark, tmp_path):
        """Benchmark scanning directory with 500 files."""
        config = {
            'settings': {
                'dry_run': True,
                'log_all_moves': False
            },
            'rules': [{
                'name': 'All',
                'pattern': '*',
                'source': str(tmp_path / "source"),
                'action': {'type': 'move', 'move_to': str(tmp_path / "dest") + '/'}
            }]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(tmp_path / "benchmark.db"))

        # Create 500 files
        source = tmp_path / "source"
        source.mkdir()

        for i in range(500):
            (source / f"file_{i}.txt").write_text(f"Content {i}")

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 500


# ============================================================================
# Pattern Matching Benchmarks
# ============================================================================

class TestPatternMatchingBenchmarks:
    """Benchmark pattern matching operations."""

    def test_simple_pattern_match_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark simple pattern matching (*.txt)."""
        daemon, tmp_path = benchmark_daemon

        def match_pattern():
            return daemon._matches_pattern("test.txt", "*.txt")

        result = benchmark(match_pattern)
        assert result is True

    def test_complex_pattern_match_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark complex pattern matching (*.{jpg,png,gif})."""
        daemon, tmp_path = benchmark_daemon

        def match_pattern():
            return daemon._matches_pattern("photo.jpg", "*.{jpg,png,gif}")

        result = benchmark(match_pattern)
        assert result is True

    def test_multiple_rules_matching_benchmark(self, benchmark, daemon_with_files):
        """Benchmark matching against multiple rules."""
        daemon, source = daemon_with_files

        # Create file to test
        test_file = source / "test.txt"

        def find_matching_rules():
            matched = []
            for rule in daemon.rules:
                if daemon._matches_pattern(test_file.name, rule.get('pattern', '*')):
                    matched.append(rule)
            return len(matched)

        result = benchmark(find_matching_rules)
        assert result >= 1


# ============================================================================
# File Classification Benchmarks
# ============================================================================

class TestClassificationBenchmarks:
    """Benchmark file classification operations."""

    def test_classify_by_extension_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark classification by file extension."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        test_file = source / "document.txt"
        test_file.write_text("Test content")

        def classify():
            for rule in daemon.rules:
                if daemon._matches_pattern(test_file.name, rule.get('pattern', '*')):
                    return rule['name']
            return None

        result = benchmark(classify)
        assert result == 'Text Files'

    def test_bulk_classification_benchmark(self, benchmark, daemon_with_files):
        """Benchmark classifying 100 files."""
        daemon, source = daemon_with_files

        def classify_all():
            classified = 0
            for file in source.iterdir():
                if file.is_file():
                    for rule in daemon.rules:
                        if daemon._matches_pattern(file.name, rule.get('pattern', '*')):
                            classified += 1
                            break
            return classified

        result = benchmark(classify_all)
        assert result == 100


# ============================================================================
# Hash Computation Benchmarks
# ============================================================================

class TestHashBenchmarks:
    """Benchmark hash computation operations."""

    def test_hash_small_file_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark hashing a small file (1KB)."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        test_file = source / "small.txt"
        test_file.write_text("x" * 1024)  # 1KB

        result = benchmark(daemon._compute_file_hash, test_file)
        assert len(result) == 64  # SHA256 hex digest

    def test_hash_medium_file_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark hashing a medium file (100KB)."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        test_file = source / "medium.txt"
        test_file.write_text("x" * (100 * 1024))  # 100KB

        result = benchmark(daemon._compute_file_hash, test_file)
        assert len(result) == 64

    def test_hash_large_file_benchmark(self, benchmark, benchmark_daemon):
        """Benchmark hashing a large file (1MB)."""
        daemon, tmp_path = benchmark_daemon
        source = tmp_path / "source"
        source.mkdir()

        test_file = source / "large.txt"
        test_file.write_text("x" * (1024 * 1024))  # 1MB

        result = benchmark(daemon._compute_file_hash, test_file)
        assert len(result) == 64

    def test_bulk_hashing_benchmark(self, benchmark, daemon_with_files):
        """Benchmark hashing 100 files."""
        daemon, source = daemon_with_files

        def hash_all():
            hashes = []
            for file in source.iterdir():
                if file.is_file():
                    hashes.append(daemon._compute_file_hash(file))
            return len(hashes)

        result = benchmark(hash_all)
        assert result == 100


# ============================================================================
# Duplicate Detection Benchmarks
# ============================================================================

class TestDuplicateDetectionBenchmarks:
    """Benchmark duplicate detection operations."""

    def test_find_duplicates_in_small_set_benchmark(self, benchmark, tmp_path):
        """Benchmark duplicate detection in 10 files."""
        config = {
            'settings': {'dry_run': True, 'log_all_moves': False},
            'rules': [{
                'name': 'All',
                'pattern': '*',
                'source': str(tmp_path / "source"),
                'action': {'type': 'move', 'move_to': str(tmp_path / "dest") + '/'}
            }]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(tmp_path / "benchmark.db"))

        # Create files with duplicates
        source = tmp_path / "source"
        source.mkdir()

        # Create 10 files, some duplicates
        for i in range(10):
            content = "duplicate" if i % 2 == 0 else f"unique_{i}"
            (source / f"file_{i}.txt").write_text(content)

        def find_duplicates():
            hashes = {}
            duplicates = 0
            for file in source.iterdir():
                if file.is_file():
                    file_hash = daemon._compute_file_hash(file)
                    if file_hash in hashes:
                        duplicates += 1
                    else:
                        hashes[file_hash] = file
            return duplicates

        result = benchmark(find_duplicates)
        assert result >= 4  # At least 4 duplicates


# ============================================================================
# Full Workflow Benchmarks
# ============================================================================

class TestWorkflowBenchmarks:
    """Benchmark complete workflow operations."""

    def test_complete_scan_workflow_benchmark(self, benchmark, daemon_with_files):
        """Benchmark complete scan workflow (scan + classify + hash)."""
        daemon, source = daemon_with_files

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 100

    def test_scan_and_organize_workflow_benchmark(self, benchmark, tmp_path):
        """Benchmark scan and organize workflow (dry-run)."""
        config = {
            'settings': {'dry_run': True, 'log_all_moves': False},
            'rules': [
                {
                    'name': 'Text',
                    'pattern': '*.txt',
                    'source': str(tmp_path / "source"),
                    'action': {'type': 'move', 'move_to': str(tmp_path / "dest/text") + '/'}
                },
                {
                    'name': 'Python',
                    'pattern': '*.py',
                    'source': str(tmp_path / "source"),
                    'action': {'type': 'move', 'move_to': str(tmp_path / "dest/python") + '/'}
                }
            ]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(tmp_path / "benchmark.db"))

        # Create mixed files
        source = tmp_path / "source"
        source.mkdir()

        for i in range(50):
            ext = 'txt' if i % 2 == 0 else 'py'
            (source / f"file_{i}.{ext}").write_text(f"Content {i}")

        result = benchmark(daemon.scan_directory, source, dry_run=True)
        assert result['scanned'] == 50


# ============================================================================
# Nested Directory Benchmarks
# ============================================================================

class TestNestedDirectoryBenchmarks:
    """Benchmark nested directory operations."""

    def test_scan_nested_directories_benchmark(self, benchmark, tmp_path):
        """Benchmark scanning nested directory structure."""
        config = {
            'settings': {'dry_run': True, 'log_all_moves': False},
            'rules': [{
                'name': 'All',
                'pattern': '*',
                'source': str(tmp_path / "source"),
                'action': {'type': 'move', 'move_to': str(tmp_path / "dest") + '/'}
            }]
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f)

        daemon = SortingDaemon(str(config_path), str(tmp_path / "benchmark.db"))

        # Create nested structure
        source = tmp_path / "source"
        source.mkdir()

        for i in range(5):
            subdir = source / f"level1_{i}"
            subdir.mkdir()
            for j in range(10):
                (subdir / f"file_{i}_{j}.txt").write_text(f"Content {i}-{j}")

        # Scan just top level (daemon typically scans single directory)
        result = benchmark(daemon.scan_directory, source, dry_run=True)
        # scan_directory only scans files in the given directory, not subdirectories
        assert result['scanned'] == 0  # No files in root, only in subdirs
