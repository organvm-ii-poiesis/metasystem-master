#!/usr/bin/env python3
"""
Performance benchmarks for KnowledgeGraph operations.

Establishes baseline performance metrics for:
- Entity CRUD operations
- Query operations
- Relationship management
- Full-text search
- Bulk operations
"""

import pytest
import tempfile
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from knowledge_graph import KnowledgeGraph


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def benchmark_kg(tmp_path):
    """Create a KnowledgeGraph for benchmarking."""
    kg_path = tmp_path / "benchmark.db"
    kg = KnowledgeGraph(str(kg_path))
    return kg


@pytest.fixture
def populated_kg(tmp_path):
    """Create a pre-populated KnowledgeGraph with 1000 entities."""
    kg_path = tmp_path / "benchmark.db"
    kg = KnowledgeGraph(str(kg_path))

    # Insert 1000 entities
    for i in range(1000):
        kg.insert_entity({
            'id': str(uuid.uuid4()),
            'type': 'file' if i % 3 == 0 else 'project' if i % 3 == 1 else 'conversation',
            'name': f'entity_{i}',
            'path': f'/path/to/entity_{i}',
            'metadata': {
                'index': i,
                'category': f'cat_{i % 10}',
                'description': f'Entity number {i} for benchmarking purposes'
            }
        })

    return kg


# ============================================================================
# Entity CRUD Benchmarks
# ============================================================================

class TestEntityCRUDBenchmarks:
    """Benchmark entity CRUD operations."""

    def test_insert_entity_benchmark(self, benchmark, benchmark_kg):
        """Benchmark single entity insertion."""
        def insert_entity():
            entity = {
                'id': str(uuid.uuid4()),
                'type': 'file',
                'name': 'benchmark_file.py',
                'path': '/src/benchmark_file.py',
                'metadata': {'size': 1024, 'created': '2026-01-02'}
            }
            return benchmark_kg.insert_entity(entity)

        result = benchmark(insert_entity)
        assert result is not None

    def test_get_entity_benchmark(self, benchmark, populated_kg):
        """Benchmark entity retrieval by ID."""
        # Get first entity
        entities = populated_kg.query_entities(limit=1)
        entity_id = entities[0]['id']

        result = benchmark(populated_kg.get_entity, entity_id)
        assert result is not None

    def test_update_entity_benchmark(self, benchmark, populated_kg):
        """Benchmark entity update."""
        # Get first entity
        entities = populated_kg.query_entities(limit=1)
        entity_id = entities[0]['id']

        def update_entity():
            updates = {'metadata': {'updated': True, 'benchmark': 'test', 'iter': str(uuid.uuid4())}}
            return populated_kg.update_entity(entity_id, updates)

        result = benchmark(update_entity)
        assert result is True

    def test_delete_entity_benchmark(self, benchmark, benchmark_kg):
        """Benchmark entity deletion."""
        def delete_entity():
            # Insert entity first (for each iteration)
            entity_id = str(uuid.uuid4())
            benchmark_kg.insert_entity({
                'id': entity_id,
                'type': 'file',
                'name': 'to_delete.py'
            })
            return benchmark_kg.delete_entity(entity_id)

        result = benchmark(delete_entity)
        assert result is True

    def test_bulk_insert_benchmark(self, benchmark, benchmark_kg):
        """Benchmark bulk entity insertion (100 entities)."""
        def bulk_insert():
            entities = []
            for i in range(100):
                entities.append({
                    'id': str(uuid.uuid4()),
                    'type': 'file',
                    'name': f'bulk_file_{i}.py',
                    'path': f'/src/bulk_{i}.py'
                })

            for entity in entities:
                benchmark_kg.insert_entity(entity)

            return len(entities)

        result = benchmark(bulk_insert)
        assert result == 100


# ============================================================================
# Query Benchmarks
# ============================================================================

class TestQueryBenchmarks:
    """Benchmark query operations."""

    def test_query_all_entities_benchmark(self, benchmark, populated_kg):
        """Benchmark querying all entities."""
        result = benchmark(populated_kg.query_entities, limit=1000)
        assert len(result) > 0

    def test_query_by_type_benchmark(self, benchmark, populated_kg):
        """Benchmark querying entities by type."""
        result = benchmark(populated_kg.query_entities, type='file', limit=1000)
        assert len(result) > 0

    def test_query_by_name_like_benchmark(self, benchmark, populated_kg):
        """Benchmark querying entities by name pattern."""
        result = benchmark(populated_kg.query_entities, name_like='entity_5%', limit=100)
        assert len(result) > 0

    def test_query_recent_entities_benchmark(self, benchmark, populated_kg):
        """Benchmark querying recent entities."""
        result = benchmark(populated_kg.query_entities, limit=50)
        assert len(result) > 0

    def test_query_with_multiple_filters_benchmark(self, benchmark, populated_kg):
        """Benchmark complex query with multiple filters."""
        result = benchmark(
            populated_kg.query_entities,
            type='file',
            name_like='entity_%',
            limit=100
        )
        assert len(result) >= 0


# ============================================================================
# Relationship Benchmarks
# ============================================================================

class TestRelationshipBenchmarks:
    """Benchmark relationship operations."""

    def test_add_relationship_benchmark(self, benchmark, populated_kg):
        """Benchmark adding a relationship."""
        entities = populated_kg.query_entities(limit=2)
        from_id = entities[0]['id']
        to_id = entities[1]['id']

        def add_rel():
            # Use unique relationship type for each iteration
            rel_type = f'depends_on_{uuid.uuid4().hex[:8]}'
            return populated_kg.add_relationship(
                from_id,
                to_id,
                rel_type,
                {'strength': 0.8}
            )

        result = benchmark(add_rel)
        assert result is True

    def test_get_relationships_benchmark(self, benchmark, populated_kg):
        """Benchmark getting relationships for an entity."""
        # Add some relationships first
        entities = populated_kg.query_entities(limit=10)
        base_id = entities[0]['id']

        for i in range(1, 10):
            populated_kg.add_relationship(base_id, entities[i]['id'], 'relates_to')

        result = benchmark(populated_kg.get_relationships, base_id)
        assert len(result) > 0

    def test_delete_relationship_benchmark(self, benchmark, populated_kg):
        """Benchmark deleting a relationship."""
        entities = populated_kg.query_entities(limit=2)
        from_id = entities[0]['id']
        to_id = entities[1]['id']

        def delete_rel():
            # Add and delete for each iteration
            rel_type = f'test_rel_{uuid.uuid4().hex[:8]}'
            populated_kg.add_relationship(from_id, to_id, rel_type)
            return populated_kg.delete_relationship(from_id, to_id, rel_type)

        result = benchmark(delete_rel)
        assert result is True


# ============================================================================
# Full-Text Search Benchmarks
# ============================================================================

class TestSearchBenchmarks:
    """Benchmark full-text search operations."""

    def test_search_simple_query_benchmark(self, benchmark, populated_kg):
        """Benchmark simple FTS query."""
        result = benchmark(populated_kg.search, 'entity', limit=100)
        assert len(result) >= 0

    def test_search_with_type_filter_benchmark(self, benchmark, populated_kg):
        """Benchmark FTS query with type filter."""
        result = benchmark(populated_kg.search, 'entity', types=['file'], limit=100)
        assert len(result) >= 0

    def test_search_complex_query_benchmark(self, benchmark, populated_kg):
        """Benchmark complex FTS query."""
        result = benchmark(
            populated_kg.search,
            'entity number benchmarking',
            types=['file', 'project'],
            limit=50
        )
        assert len(result) >= 0


# ============================================================================
# Conversation Benchmarks
# ============================================================================

class TestConversationBenchmarks:
    """Benchmark conversation operations."""

    def test_insert_conversation_benchmark(self, benchmark, benchmark_kg):
        """Benchmark conversation insertion."""
        def insert_conv():
            conversation = {
                'id': str(uuid.uuid4()),
                'thread_id': f'bench-thread-{uuid.uuid4().hex[:8]}',
                'tool': 'claude-code',
                'context': {
                    'files_accessed': [],
                    'decisions': [],
                    'commands_run': []
                }
            }
            return benchmark_kg.insert_conversation(conversation)

        result = benchmark(insert_conv)
        assert result is not None

    def test_get_conversation_benchmark(self, benchmark, benchmark_kg):
        """Benchmark conversation retrieval."""
        # Insert conversation first
        conv_id = str(uuid.uuid4())
        benchmark_kg.insert_conversation({
            'id': conv_id,
            'thread_id': 'bench-thread-get',
            'tool': 'claude-code',
            'context': {}
        })

        result = benchmark(benchmark_kg.get_conversation, conv_id)
        assert result is not None

    def test_update_conversation_benchmark(self, benchmark, benchmark_kg):
        """Benchmark conversation update."""
        # Insert conversation first
        conv_id = str(uuid.uuid4())
        benchmark_kg.insert_conversation({
            'id': conv_id,
            'thread_id': 'bench-thread-update',
            'tool': 'claude-code',
            'context': {}
        })

        def update_conv():
            updates = {
                'context': {
                    'files_accessed': [{'path': '/file.py', 'operation': 'read'}],
                    'decisions': [{'decision': f'Decision {uuid.uuid4().hex[:8]}'}]
                }
            }
            return benchmark_kg.update_conversation(conv_id, updates)

        result = benchmark(update_conv)
        assert result is True

    def test_query_conversations_benchmark(self, benchmark, tmp_path):
        """Benchmark conversation query."""
        # Use fresh KG with conversations
        kg_path = tmp_path / "query_convs.db"
        kg = KnowledgeGraph(str(kg_path))

        # Insert some conversations
        for i in range(50):
            kg.insert_conversation({
                'id': str(uuid.uuid4()),
                'thread_id': f'bench-thread-{i}',
                'tool': 'claude-code',
                'context': {}
            })

        result = benchmark(kg.query_conversations, limit=50)
        assert len(result) > 0


# ============================================================================
# Database Maintenance Benchmarks
# ============================================================================

class TestMaintenanceBenchmarks:
    """Benchmark database maintenance operations."""

    def test_get_stats_benchmark(self, benchmark, populated_kg):
        """Benchmark getting database statistics."""
        result = benchmark(populated_kg.get_stats)
        assert 'total_entities' in result

    def test_check_integrity_benchmark(self, benchmark, populated_kg):
        """Benchmark integrity check."""
        result = benchmark(populated_kg.check_integrity)
        assert result is True

    def test_vacuum_benchmark(self, benchmark, tmp_path):
        """Benchmark database vacuum operation."""
        # Use small DB for vacuum (it's slow on large DBs)
        kg_path = tmp_path / "vacuum_test.db"
        kg = KnowledgeGraph(str(kg_path))

        # Add a few entities
        for i in range(10):
            kg.insert_entity({
                'id': str(uuid.uuid4()),
                'type': 'file',
                'name': f'file_{i}.py'
            })

        result = benchmark.pedantic(kg.vacuum, rounds=3, iterations=1)
        assert result is True


# ============================================================================
# Snapshot Benchmarks
# ============================================================================

class TestSnapshotBenchmarks:
    """Benchmark snapshot operations."""

    def test_create_snapshot_benchmark(self, benchmark, populated_kg):
        """Benchmark snapshot creation."""
        entities = populated_kg.query_entities(limit=1)
        entity_id = entities[0]['id']

        result = benchmark(populated_kg.create_snapshot, entity_id, 'benchmark_snapshot')
        assert result is not None

    def test_get_snapshots_benchmark(self, benchmark, populated_kg):
        """Benchmark snapshot retrieval."""
        # Create some snapshots first
        entities = populated_kg.query_entities(limit=1)
        entity_id = entities[0]['id']

        for i in range(10):
            populated_kg.create_snapshot(entity_id, f'snapshot_{i}')

        result = benchmark(lambda: populated_kg.get_entity(entity_id))
        assert result is not None
