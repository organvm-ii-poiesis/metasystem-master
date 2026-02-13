#!/usr/bin/env python3
"""
Shared pytest fixtures for metasystem-core testing.

This module provides reusable fixtures for all tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import uuid

# Make parent directory available for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_graph import KnowledgeGraph


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def tmp_kg(tmp_path):
    """Create temporary KnowledgeGraph for testing.

    Yields:
        KnowledgeGraph: Fresh, empty knowledge graph in temporary location
    """
    db_path = tmp_path / "test.db"
    kg = KnowledgeGraph(str(db_path))
    yield kg
    # Cleanup handled automatically by tmp_path


@pytest.fixture
def populated_kg(tmp_kg):
    """KnowledgeGraph pre-populated with test data.

    Yields:
        KnowledgeGraph: Knowledge graph with sample projects, tools, decisions
    """
    # Add sample projects
    projects = [
        {
            'type': 'project',
            'name': 'metasystem-core',
            'path': '/Users/test/Workspace/metasystem-core',
            'metadata': {
                'language': 'python',
                'description': 'Meta-system orchestrator',
                'tags': ['system', 'infrastructure']
            }
        },
        {
            'type': 'project',
            'name': 'typescript-app',
            'path': '/Users/test/Projects/typescript-app',
            'metadata': {
                'language': 'typescript',
                'description': 'Web application',
                'tags': ['web', 'frontend']
            }
        },
        {
            'type': 'project',
            'name': 'python-lib',
            'path': '/Users/test/Projects/python-lib',
            'metadata': {
                'language': 'python',
                'description': 'Utility library',
                'tags': ['library', 'utilities']
            }
        },
    ]

    project_ids = []
    for proj in projects:
        entity_id = tmp_kg.insert_entity(proj)
        project_ids.append(entity_id)

    # Add sample tools
    tools = [
        {
            'type': 'tool',
            'name': 'pytest',
            'metadata': {
                'category': 'testing',
                'description': 'Python testing framework'
            }
        },
        {
            'type': 'tool',
            'name': 'docker',
            'metadata': {
                'category': 'infrastructure',
                'description': 'Container platform'
            }
        },
    ]

    for tool in tools:
        tmp_kg.insert_entity(tool)

    # Add sample decisions
    decisions = [
        {
            'type': 'decision',
            'name': 'Use pytest for testing',
            'metadata': {
                'decision': 'Use pytest as the testing framework',
                'rationale': 'Industry standard, excellent plugin ecosystem',
                'tags': ['testing', 'tooling']
            }
        },
    ]

    for decision in decisions:
        tmp_kg.insert_entity(decision)

    # Add sample conversation
    conv_data = {
        'id': str(uuid.uuid4()),
        'tool': 'claude-code',
        'started_at': datetime.now().isoformat(),
        'context': {
            'files_accessed': [
                '/Users/test/Workspace/metasystem-core/knowledge_graph.py',
                '/Users/test/Workspace/metasystem-core/tests/test_kg.py',
            ],
            'description': 'Testing knowledge graph',
            'decisions_made': ['Use pytest']
        }
    }
    tmp_kg.insert_conversation(conv_data)

    yield tmp_kg


@pytest.fixture
def kg_with_relationships(populated_kg):
    """KnowledgeGraph with relationships between entities.

    Yields:
        KnowledgeGraph: Knowledge graph with entities and relationships
    """
    # Get entity IDs
    projects = populated_kg.query_entities(type='project', limit=10)
    tools = populated_kg.query_entities(type='tool', limit=10)

    if projects and tools:
        # Create relationships: projects use tools
        for proj in projects:
            for tool in tools:
                if 'python' in proj.get('metadata', {}).get('language', ''):
                    populated_kg.add_relationship(
                        source_id=proj['id'],
                        target_id=tool['id'],
                        rel_type='uses',
                        metadata={'context': 'development'}
                    )

    yield populated_kg


# ============================================================================
# File System Fixtures
# ============================================================================

@pytest.fixture
def tmp_workspace(tmp_path):
    """Create temporary workspace directory structure.

    Yields:
        Path: Temporary workspace directory with subdirectories
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create subdirectories
    (workspace / "projects").mkdir()
    (workspace / "downloads").mkdir()
    (workspace / "documents").mkdir()

    yield workspace


@pytest.fixture
def mock_downloads(tmp_workspace):
    """Create mock downloads folder with test files.

    Yields:
        Path: Downloads directory with various test files
    """
    downloads = tmp_workspace / "downloads"

    # Create test files
    test_files = {
        'screenshot.png': b'fake-png-data',
        'document.pdf': b'fake-pdf-data',
        'code.py': b'print("hello world")',
        'data.json': json.dumps({'key': 'value'}).encode(),
        'archive.zip': b'fake-zip-data',
    }

    for filename, content in test_files.items():
        (downloads / filename).write_bytes(content)

    yield downloads


@pytest.fixture
def mock_chezmoi(tmp_path):
    """Create mock chezmoi source directory.

    Yields:
        Path: Mock chezmoi source directory with git repo
    """
    chezmoi_source = tmp_path / "chezmoi"
    chezmoi_source.mkdir()

    # Initialize git repo
    import subprocess
    subprocess.run(['git', 'init'], cwd=chezmoi_source, check=True,
                   capture_output=True)
    subprocess.run(['git', 'config', 'user.email', 'test@example.com'],
                   cwd=chezmoi_source, check=True, capture_output=True)
    subprocess.run(['git', 'config', 'user.name', 'Test User'],
                   cwd=chezmoi_source, check=True, capture_output=True)

    # Create some dotfiles
    dotfiles = {
        'dot_bashrc': '# bashrc\nalias ll="ls -la"',
        'dot_gitconfig': '[user]\nname = Test',
        'private_dot_aws/credentials.tmpl': '# AWS credentials',
    }

    for filepath, content in dotfiles.items():
        full_path = chezmoi_source / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)

    # Initial commit
    subprocess.run(['git', 'add', '.'], cwd=chezmoi_source, check=True,
                   capture_output=True)
    subprocess.run(['git', 'commit', '-m', 'Initial commit'],
                   cwd=chezmoi_source, check=True, capture_output=True)

    yield chezmoi_source


# ============================================================================
# Time Fixtures
# ============================================================================

@pytest.fixture
def frozen_time():
    """Fixed timestamp for reproducible tests.

    Yields:
        datetime: Fixed datetime (2025-01-01 00:00:00)
    """
    from freezegun import freeze_time

    with freeze_time("2025-01-01 00:00:00"):
        yield datetime(2025, 1, 1, 0, 0, 0)


@pytest.fixture
def time_series():
    """Generate sequence of timestamps for testing time-based features.

    Yields:
        List[datetime]: List of datetimes spaced 1 hour apart
    """
    from datetime import timedelta

    base = datetime(2025, 1, 1, 0, 0, 0)
    times = [base + timedelta(hours=i) for i in range(24)]

    yield times


# ============================================================================
# Test Data Generators
# ============================================================================

@pytest.fixture
def fake_data():
    """Faker instance for generating test data.

    Yields:
        Faker: Faker instance with fixed seed for reproducibility
    """
    from faker import Faker

    fake = Faker()
    Faker.seed(42)  # Fixed seed for reproducibility

    yield fake


def make_test_entity(entity_type: str = 'project', **kwargs) -> Dict[str, Any]:
    """Helper to create test entity data.

    Args:
        entity_type: Type of entity (project, tool, file, etc.)
        **kwargs: Additional entity fields

    Returns:
        Dict with entity data ready for insert_entity()
    """
    entity = {
        'type': entity_type,
        'name': kwargs.get('name', f'test-{entity_type}-{uuid.uuid4().hex[:8]}'),
        'metadata': kwargs.get('metadata', {}),
    }

    # Add optional fields
    if 'path' in kwargs:
        entity['path'] = kwargs['path']

    return entity


def make_test_conversation(**kwargs) -> Dict[str, Any]:
    """Helper to create test conversation data.

    Args:
        **kwargs: Conversation fields

    Returns:
        Dict with conversation data ready for insert_conversation()
    """
    conv = {
        'id': kwargs.get('id', str(uuid.uuid4())),
        'tool': kwargs.get('tool', 'test-tool'),
        'started_at': kwargs.get('started_at', datetime.now().isoformat()),
        'context': kwargs.get('context', {}),
        'state': kwargs.get('state', {}),
    }

    return conv


# Export helper functions
__all__ = [
    'tmp_kg',
    'populated_kg',
    'kg_with_relationships',
    'tmp_workspace',
    'mock_downloads',
    'mock_chezmoi',
    'frozen_time',
    'time_series',
    'fake_data',
    'make_test_entity',
    'make_test_conversation',
]
