# Phase 9: Testing & Quality Assurance - Implementation Plan

**Status**: In Progress
**Started**: 2025-12-31
**Goal**: Comprehensive test coverage, performance benchmarks, and quality assurance for production readiness

---

## Overview

Phase 9 adds professional-grade testing to ensure the metasystem is reliable, performant, and maintainable. After 8 phases of development (~5,400 LOC), we need:

1. **Unit tests** - Test individual components in isolation
2. **Integration tests** - Test component interactions
3. **End-to-end tests** - Test complete workflows
4. **Performance benchmarks** - Measure and track performance
5. **Coverage reporting** - Ensure comprehensive test coverage
6. **Continuous quality** - Make testing part of development workflow

---

## Current Codebase Analysis

### Components to Test (14 modules)

#### Core Infrastructure (Priority 1 - Critical)
- **knowledge_graph.py** (~650 LOC) - 20+ methods
  - Database initialization and schema
  - Entity CRUD operations
  - Full-text search
  - Relationships and conversations
  - Facts and snapshots

- **context_manager.py** (~420 LOC)
  - Conversation lifecycle
  - Context persistence and resume
  - File access tracking
  - Decision logging

- **sorting_daemon.py** (~580 LOC)
  - File scanning and categorization
  - Rule matching engine
  - ML-based classification
  - Auto-organization logic

#### Synchronization (Priority 2 - Important)
- **sync_engine.py** (~450 LOC)
  - Multi-machine synchronization
  - Conflict resolution
  - iCloud Drive integration
  - External drive backup

- **sync_chezmoi.py** (~200 LOC)
  - Dotfile synchronization
  - Git history preservation
  - Backup and restore

#### Agents (Priority 3 - Important)
- **agents/maintainer.py** (~380 LOC)
  - Health checks
  - Auto-repair logic
  - System validation

- **agents/cataloger.py** (~420 LOC)
  - Discovery engine
  - Workspace scanning
  - Project indexing

- **agents/synthesizer.py** (~310 LOC)
  - Documentation generation
  - Template rendering
  - Auto-update logic

- **agents/dotfile_watcher.py** (~332 LOC)
  - Chezmoi integration
  - Change tracking
  - Decision logging

#### Supporting Modules (Priority 4 - Nice to Have)
- **discovery_engine.py**
- **documentation_generator.py**
- **mcp_bridge.py**
- **maintenance_daemon.py**

---

## Testing Strategy

### 1. Unit Tests

Test individual methods in isolation using mocks where needed.

**Frameworks**:
- `pytest` - Test runner
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking support
- `freezegun` - Time mocking

**Coverage Goals**:
- Critical components: >90%
- Important components: >80%
- Supporting modules: >70%
- Overall: >80%

**Example test structure**:
```
tests/
├── unit/
│   ├── test_knowledge_graph.py
│   ├── test_context_manager.py
│   ├── test_sorting_daemon.py
│   ├── test_sync_engine.py
│   └── test_agents/
│       ├── test_maintainer.py
│       ├── test_cataloger.py
│       ├── test_synthesizer.py
│       └── test_dotfile_watcher.py
├── integration/
│   ├── test_agent_coordination.py
│   ├── test_kg_context_integration.py
│   └── test_sync_workflows.py
├── e2e/
│   ├── test_conversation_lifecycle.py
│   ├── test_file_organization.py
│   └── test_multi_machine_sync.py
├── performance/
│   ├── benchmark_kg_queries.py
│   ├── benchmark_file_scanning.py
│   └── benchmark_fts_search.py
├── conftest.py         # Shared fixtures
└── test_helpers.py     # Test utilities
```

### 2. Test Fixtures

**Database fixtures**:
- `tmp_kg` - Temporary KnowledgeGraph for each test
- `populated_kg` - KG with sample data (projects, conversations, etc.)
- `kg_with_relationships` - KG with complex relationship graph

**File system fixtures**:
- `tmp_workspace` - Temporary workspace directory
- `mock_downloads` - Mock downloads folder with test files
- `mock_chezmoi` - Mock chezmoi source directory

**Time fixtures**:
- `frozen_time` - Fixed timestamp for reproducible tests
- `time_series` - Sequence of timestamps for history tests

### 3. Integration Tests

Test interactions between components:

**Critical integrations**:
- KnowledgeGraph ↔ ContextManager
- KnowledgeGraph ↔ All Agents
- SortingDaemon ↔ KnowledgeGraph
- SyncEngine ↔ KnowledgeGraph
- MaintenanceDaemon ↔ All Agents

**Test scenarios**:
- Start conversation → Log files → Resume conversation
- Scan files → Categorize → Move → Update KG
- Discover projects → Index → Generate docs
- Health check → Detect issue → Auto-repair
- Make change → Sync to iCloud → Restore on another "machine"

### 4. End-to-End Tests

Test complete user workflows:

**E2E Scenarios**:
1. **New work session**:
   - Start conversation
   - Access files
   - Make decisions
   - End conversation
   - Verify all logged to KG

2. **Resume previous work**:
   - Query recent conversations
   - Resume specific conversation
   - Verify context restored
   - Continue work

3. **File organization**:
   - Drop files in Downloads
   - Wait for scan (or trigger manually)
   - Verify files categorized correctly
   - Verify KG updated

4. **Multi-machine sync**:
   - Make changes on "machine 1"
   - Sync to iCloud
   - Restore on "machine 2"
   - Verify state identical

5. **System maintenance**:
   - Run health checks
   - Detect simulated issues
   - Verify auto-repair
   - Generate documentation

### 5. Performance Benchmarks

Measure and track performance over time:

**Key metrics**:
- KG query performance (target: <100ms for simple queries)
- FTS search performance (target: <200ms for most searches)
- File scanning speed (target: >1000 files/second)
- Discovery engine speed (target: <10s for 500 projects)
- Database size growth (monitor over time)

**Benchmark framework**:
- `pytest-benchmark` for automated benchmarking
- Store results in `benchmarks/` directory
- Generate performance reports
- Track regression over time

**Benchmark scenarios**:
```python
def test_kg_insert_performance(benchmark, populated_kg):
    """Entity insertion should be <10ms."""
    result = benchmark(populated_kg.insert_entity, {
        'type': 'project',
        'name': 'test-project',
        'path': '/test/path',
        'metadata': {'lang': 'python'}
    })
    assert result  # Just ensure it completes

def test_fts_search_performance(benchmark, kg_with_1000_entities):
    """FTS search should be <200ms for 1000 entities."""
    result = benchmark(kg_with_1000_entities.search,
                      'typescript project',
                      limit=20)
    assert len(result) > 0
```

### 6. Coverage Reporting

**Tools**:
- `pytest-cov` for coverage measurement
- `coverage.py` for HTML reports
- Pre-commit hooks for coverage checks

**Configuration** (.coveragerc):
```ini
[run]
source = .
omit =
    */tests/*
    */.venv/*
    */site-packages/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

**Commands**:
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Coverage badge (for README)
coverage-badge -o coverage.svg
```

---

## Implementation Tasks

### Task 1: Testing Infrastructure Setup ✅
- [x] Create testing plan
- [ ] Install testing dependencies
- [ ] Create test directory structure
- [ ] Configure pytest
- [ ] Create shared fixtures (conftest.py)
- [ ] Set up coverage reporting
- [ ] Create test helpers

### Task 2: Unit Tests - Knowledge Graph (Critical)
- [ ] Test `__init__` and schema initialization
- [ ] Test `insert_entity` with various entity types
- [ ] Test `get_entity` / `update_entity` / `delete_entity`
- [ ] Test `query_entities` with filters
- [ ] Test FTS `search` functionality
- [ ] Test `add_relationship` / `get_relationships`
- [ ] Test conversation methods
- [ ] Test facts and snapshots
- [ ] Edge cases: invalid IDs, concurrent access, corrupted JSON

### Task 3: Unit Tests - Context Manager
- [ ] Test conversation start/end lifecycle
- [ ] Test file access logging
- [ ] Test decision logging
- [ ] Test conversation resume
- [ ] Test context serialization
- [ ] Test search across conversations
- [ ] Edge cases: missing conversations, corrupted state

### Task 4: Unit Tests - Sorting Daemon
- [ ] Test file scanning
- [ ] Test rule matching engine
- [ ] Test file categorization
- [ ] Test file moving
- [ ] Test KG integration (mock)
- [ ] Test duplicate detection
- [ ] Edge cases: permission errors, missing files

### Task 5: Unit Tests - Sync Engine
- [ ] Test iCloud sync
- [ ] Test external drive sync
- [ ] Test conflict detection
- [ ] Test conflict resolution
- [ ] Test sync status tracking
- [ ] Edge cases: offline, drive unmounted

### Task 6: Unit Tests - Agents
- [ ] Maintainer: health checks, auto-repair
- [ ] Cataloger: discovery, indexing
- [ ] Synthesizer: doc generation
- [ ] DotfileWatcher: tracking, sync
- [ ] Edge cases: missing dependencies, permission errors

### Task 7: Integration Tests
- [ ] KG + ContextManager integration
- [ ] SortingDaemon + KG integration
- [ ] MaintenanceDaemon + All Agents
- [ ] SyncEngine + KG integration
- [ ] MCP Bridge + KG queries

### Task 8: End-to-End Tests
- [ ] Complete conversation lifecycle
- [ ] File organization workflow
- [ ] Multi-machine sync simulation
- [ ] System maintenance workflow
- [ ] Documentation generation workflow

### Task 9: Performance Benchmarks
- [ ] KG entity operations benchmarks
- [ ] FTS search benchmarks
- [ ] File scanning benchmarks
- [ ] Discovery engine benchmarks
- [ ] Relationship query benchmarks
- [ ] Create performance reports

### Task 10: Documentation & Reporting
- [ ] Update README with testing instructions
- [ ] Create TESTING.md guide
- [ ] Generate coverage reports
- [ ] Create performance baseline
- [ ] Document CI/CD integration (optional)
- [ ] Create Phase 9 completion summary

---

## Success Criteria

### Minimum Viable Testing (Phase 9 Complete)
- ✅ Test infrastructure set up (pytest, coverage, fixtures)
- ✅ >80% overall code coverage
- ✅ Knowledge Graph: >90% coverage (critical component)
- ✅ All core modules have unit tests
- ✅ Key integrations have integration tests
- ✅ At least 3 E2E workflows tested
- ✅ Performance benchmarks established
- ✅ Coverage reporting automated
- ✅ Testing documentation complete

### Stretch Goals
- ⭐ >90% overall coverage
- ⭐ All E2E workflows tested
- ⭐ Performance regression tracking
- ⭐ Pre-commit hooks for testing
- ⭐ CI/CD pipeline (GitHub Actions)
- ⭐ Mutation testing for critical code

---

## Testing Dependencies

Add to `requirements.txt`:
```
# Testing
pytest>=7.4
pytest-cov>=4.1
pytest-mock>=3.12
pytest-benchmark>=4.0
freezegun>=1.2         # Time mocking
faker>=20.0            # Generate test data
coverage>=7.3
coverage-badge>=1.1

# Test utilities
pytest-xdist>=3.5      # Parallel test execution
pytest-timeout>=2.2    # Prevent hanging tests
pytest-randomly>=3.15  # Randomize test order
```

---

## Example Test Cases

### Example: Knowledge Graph Unit Test
```python
import pytest
from knowledge_graph import KnowledgeGraph
from pathlib import Path

@pytest.fixture
def tmp_kg(tmp_path):
    """Create temporary KnowledgeGraph for testing."""
    db_path = tmp_path / "test.db"
    kg = KnowledgeGraph(str(db_path))
    return kg

def test_insert_and_get_entity(tmp_kg):
    """Should insert entity and retrieve it."""
    entity = {
        'type': 'project',
        'name': 'test-project',
        'path': '/test/path',
        'metadata': {'language': 'python'}
    }

    entity_id = tmp_kg.insert_entity(entity)

    assert entity_id is not None

    retrieved = tmp_kg.get_entity(entity_id)

    assert retrieved['name'] == 'test-project'
    assert retrieved['type'] == 'project'
    assert retrieved['path'] == '/test/path'
    assert retrieved['metadata']['language'] == 'python'

def test_fts_search(tmp_kg):
    """Should find entities via full-text search."""
    # Insert test entities
    tmp_kg.insert_entity({
        'type': 'project',
        'name': 'typescript-app',
        'metadata': {'description': 'A web application'}
    })
    tmp_kg.insert_entity({
        'type': 'project',
        'name': 'python-lib',
        'metadata': {'description': 'A Python library'}
    })

    # Search for TypeScript
    results = tmp_kg.search('typescript', types=['project'])

    assert len(results) == 1
    assert results[0]['name'] == 'typescript-app'

def test_update_nonexistent_entity(tmp_kg):
    """Should raise error when updating nonexistent entity."""
    with pytest.raises(ValueError, match="Entity .* not found"):
        tmp_kg.update_entity('nonexistent-id', {'name': 'updated'})
```

### Example: Integration Test
```python
def test_context_manager_kg_integration(tmp_kg, tmp_path):
    """ContextManager should log conversations to KnowledgeGraph."""
    from context_manager import ContextManager

    cm = ContextManager(kg=tmp_kg, workspace=tmp_path)

    # Start conversation
    conv_id = cm.start_conversation(tool='claude-code')

    # Log file access
    cm.log_file_access('/test/file.py')

    # Log decision
    cm.log_decision(
        decision='Use pytest for testing',
        rationale='Industry standard, excellent plugin ecosystem'
    )

    # End conversation
    cm.end_conversation()

    # Verify in KG
    conv = tmp_kg.get_conversation(conv_id)

    assert conv is not None
    assert conv['tool'] == 'claude-code'
    assert conv['status'] == 'completed'
    assert len(conv['files_accessed']) == 1
    assert '/test/file.py' in conv['files_accessed']

    # Verify decision logged
    decisions = tmp_kg.query_entities(type='decision', limit=10)
    assert len(decisions) == 1
    assert 'pytest' in decisions[0]['metadata']['decision']
```

### Example: E2E Test
```python
def test_complete_conversation_lifecycle(tmp_kg, tmp_path):
    """Complete conversation workflow from start to resume."""
    from context_manager import ContextManager

    cm = ContextManager(kg=tmp_kg, workspace=tmp_path)

    # Step 1: Start new work session
    conv_id = cm.start_conversation(tool='claude-code')
    cm.log_file_access('/project/main.py')
    cm.log_file_access('/project/tests/test_main.py')
    cm.log_decision(
        decision='Implement feature X',
        rationale='User requirement'
    )
    cm.end_conversation()

    # Step 2: Resume previous session
    resumed_cm = ContextManager(kg=tmp_kg, workspace=tmp_path)
    context = resumed_cm.resume_conversation(conv_id)

    # Verify context restored
    assert context['conversation_id'] == conv_id
    assert context['tool'] == 'claude-code'
    assert len(context['files_accessed']) == 2
    assert '/project/main.py' in context['files_accessed']

    # Step 3: Continue work
    resumed_cm.log_file_access('/project/utils.py')
    resumed_cm.end_conversation()

    # Verify history accumulated
    final_conv = tmp_kg.get_conversation(conv_id)
    assert len(final_conv['files_accessed']) == 3
```

---

## Timeline Estimate

This is a self-paced personal project, so no strict deadlines. However, for planning purposes:

- **Task 1** (Infrastructure): ~2-3 hours
- **Tasks 2-6** (Unit tests): ~15-20 hours (largest effort)
- **Task 7** (Integration): ~5-7 hours
- **Task 8** (E2E): ~4-6 hours
- **Task 9** (Benchmarks): ~3-4 hours
- **Task 10** (Docs): ~2-3 hours

**Total**: ~30-40 hours of focused work

**Approach**: Incremental, test one module at a time, commit frequently.

---

## Next Steps

1. ✅ Review this plan for alignment with Phase 9 goals
2. Install testing dependencies
3. Set up test infrastructure
4. Start with KnowledgeGraph unit tests (most critical)
5. Progressively add tests for other modules
6. Measure coverage and fill gaps
7. Create Phase 9 completion summary

---

**This testing strategy ensures the metasystem is production-ready and maintainable for the long term.**
