#!/usr/bin/env python3
"""
Test helper utilities for metasystem-core testing.

Provides common assertions, mocks, and utilities.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta


# ============================================================================
# Assertion Helpers
# ============================================================================

def assert_entity_valid(entity: Dict[str, Any], entity_type: str = None):
    """Assert that entity has required fields and valid structure.

    Args:
        entity: Entity dict to validate
        entity_type: Expected entity type (optional)
    """
    # Required fields
    assert 'id' in entity, "Entity must have 'id'"
    assert 'type' in entity, "Entity must have 'type'"
    assert 'created_at' in entity, "Entity must have 'created_at'"
    assert 'updated_at' in entity, "Entity must have 'updated_at'"
    assert 'last_seen' in entity, "Entity must have 'last_seen'"

    # Type check
    if entity_type:
        assert entity['type'] == entity_type, \
            f"Expected type '{entity_type}', got '{entity['type']}'"

    # Timestamps should be ISO format
    for ts_field in ['created_at', 'updated_at', 'last_seen']:
        try:
            datetime.fromisoformat(entity[ts_field])
        except ValueError:
            raise AssertionError(f"Invalid timestamp format in '{ts_field}': {entity[ts_field]}")

    # Metadata should be dict or None
    if 'metadata' in entity and entity['metadata'] is not None:
        assert isinstance(entity['metadata'], dict), \
            f"Metadata should be dict, got {type(entity['metadata'])}"


def assert_conversation_valid(conv: Dict[str, Any]):
    """Assert that conversation has required fields.

    Args:
        conv: Conversation dict to validate
    """
    # Required fields from schema
    assert 'id' in conv, "Conversation must have 'id'"
    assert 'tool' in conv, "Conversation must have 'tool'"
    assert 'started_at' in conv, "Conversation must have 'started_at'"
    assert 'last_message_at' in conv, "Conversation must have 'last_message_at'"

    # Optional JSON fields should be dict if present
    if 'context' in conv and conv['context'] is not None:
        assert isinstance(conv['context'], dict), \
            f"context should be dict, got {type(conv['context'])}"

    if 'state' in conv and conv['state'] is not None:
        assert isinstance(conv['state'], dict), \
            f"state should be dict, got {type(conv['state'])}"


def assert_relationship_valid(rel: Dict[str, Any]):
    """Assert that relationship has required fields.

    Args:
        rel: Relationship dict to validate
    """
    assert 'id' in rel, "Relationship must have 'id'"
    assert 'source_id' in rel, "Relationship must have 'source_id'"
    assert 'target_id' in rel, "Relationship must have 'target_id'"
    assert 'rel_type' in rel, "Relationship must have 'rel_type'"
    assert 'created_at' in rel, "Relationship must have 'created_at'"


def assert_file_exists(path: Path, message: str = None):
    """Assert that file exists.

    Args:
        path: Path to check
        message: Custom error message
    """
    assert path.exists(), message or f"File not found: {path}"
    assert path.is_file(), f"Path exists but is not a file: {path}"


def assert_dir_exists(path: Path, message: str = None):
    """Assert that directory exists.

    Args:
        path: Path to check
        message: Custom error message
    """
    assert path.exists(), message or f"Directory not found: {path}"
    assert path.is_dir(), f"Path exists but is not a directory: {path}"


# ============================================================================
# Data Generators
# ============================================================================

def make_entities(count: int, entity_type: str = 'project') -> List[Dict[str, Any]]:
    """Generate multiple test entities.

    Args:
        count: Number of entities to generate
        entity_type: Type of entities

    Returns:
        List of entity dicts
    """
    import uuid

    entities = []
    for i in range(count):
        entity = {
            'type': entity_type,
            'name': f'test-{entity_type}-{i}',
            'path': f'/test/{entity_type}s/item-{i}',
            'metadata': {
                'index': i,
                'generated': True,
            }
        }
        entities.append(entity)

    return entities


def make_file_tree(root: Path, structure: Dict[str, Any]):
    """Create file tree from nested dict structure.

    Args:
        root: Root directory
        structure: Nested dict describing file tree
            - Keys are filenames/dirnames
            - String values are file contents
            - Dict values are subdirectories

    Example:
        make_file_tree(tmp_path, {
            'file.txt': 'content',
            'subdir': {
                'nested.txt': 'nested content'
            }
        })
    """
    for name, content in structure.items():
        path = root / name

        if isinstance(content, dict):
            # It's a directory
            path.mkdir(parents=True, exist_ok=True)
            make_file_tree(path, content)
        else:
            # It's a file
            if isinstance(content, bytes):
                path.write_bytes(content)
            else:
                path.write_text(str(content))


# ============================================================================
# Time Utilities
# ============================================================================

def days_ago(days: int) -> datetime:
    """Get datetime N days ago.

    Args:
        days: Number of days in the past

    Returns:
        datetime object
    """
    return datetime.now() - timedelta(days=days)


def hours_ago(hours: int) -> datetime:
    """Get datetime N hours ago.

    Args:
        hours: Number of hours in the past

    Returns:
        datetime object
    """
    return datetime.now() - timedelta(hours=hours)


def iso_now() -> str:
    """Get current time as ISO string.

    Returns:
        ISO 8601 formatted timestamp
    """
    return datetime.now().isoformat()


# ============================================================================
# Database Utilities
# ============================================================================

def count_entities(kg, entity_type: str = None) -> int:
    """Count entities in knowledge graph.

    Args:
        kg: KnowledgeGraph instance
        entity_type: Optional type filter

    Returns:
        Count of entities
    """
    entities = kg.query_entities(type=entity_type, limit=1000000)
    return len(entities)


def clear_kg(kg):
    """Clear all data from knowledge graph.

    Args:
        kg: KnowledgeGraph instance
    """
    # Get all entities
    entities = kg.query_entities(limit=1000000)

    # Delete them all
    for entity in entities:
        kg.delete_entity(entity['id'])


# ============================================================================
# Mock Helpers
# ============================================================================

class MockProcess:
    """Mock subprocess result for testing."""

    def __init__(self, returncode: int = 0, stdout: str = '', stderr: str = ''):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def mock_subprocess_run(returncode: int = 0, stdout: str = '', stderr: str = ''):
    """Create mock subprocess.run result.

    Args:
        returncode: Exit code
        stdout: Standard output
        stderr: Standard error

    Returns:
        MockProcess instance
    """
    return MockProcess(returncode=returncode, stdout=stdout, stderr=stderr)


# ============================================================================
# JSON Utilities
# ============================================================================

def pretty_json(data: Any) -> str:
    """Pretty-print JSON for debugging.

    Args:
        data: Data to serialize

    Returns:
        Pretty-printed JSON string
    """
    return json.dumps(data, indent=2, default=str)


def assert_json_equal(actual: Any, expected: Any, message: str = None):
    """Assert that two JSON-serializable structures are equal.

    Args:
        actual: Actual value
        expected: Expected value
        message: Custom error message
    """
    actual_json = json.dumps(actual, sort_keys=True, default=str)
    expected_json = json.dumps(expected, sort_keys=True, default=str)

    assert actual_json == expected_json, \
        message or f"JSON not equal:\nActual:\n{pretty_json(actual)}\nExpected:\n{pretty_json(expected)}"


__all__ = [
    'assert_entity_valid',
    'assert_conversation_valid',
    'assert_relationship_valid',
    'assert_file_exists',
    'assert_dir_exists',
    'make_entities',
    'make_file_tree',
    'days_ago',
    'hours_ago',
    'iso_now',
    'count_entities',
    'clear_kg',
    'MockProcess',
    'mock_subprocess_run',
    'pretty_json',
    'assert_json_equal',
]
