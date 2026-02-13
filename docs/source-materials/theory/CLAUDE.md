# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**Metasystem Core** is a self-maintaining knowledge graph system that prevents context loss across AI conversations and machines. It's a personal automation platform combining:
- SQLite-based knowledge graph with FTS5 for full-text search
- Autonomous agents for discovery, maintenance, and documentation
- Multi-machine sync (iCloud + external drive)
- Context persistence for resuming AI conversations
- Dotfile management via chezmoi

**Key Insight**: This system solves the problem of rebuilding the same systems repeatedly by maintaining a perpetual store of all decisions, code organization, and project state.

## Development Commands

### Environment Setup

```bash
cd /Users/4jp/Workspace/metasystem-core

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov

# Run specific test file
pytest tests/test_knowledge_graph.py -v

# Run specific test
pytest tests/test_knowledge_graph.py::TestKnowledgeGraph::test_insert_entity -v

# Run with markers
pytest -m "unit" -v          # Only unit tests
pytest -m "integration" -v   # Only integration tests
pytest -m "not slow" -v      # Skip slow tests

# Run tests in parallel
pytest -n auto

# Run benchmarks
pytest --benchmark-only

# Watch mode (requires pytest-watch)
ptw -- -v
```

### Linting and Code Quality

```bash
# Check with built-in tools (no external linters required, use Python's built-ins)
python3 -m py_compile *.py agents/*.py  # Syntax check

# Check imports and dependencies
python3 -c "import py_compile; import sys; sys.exit(sum(1 for f in __import__('glob').glob('**/*.py', recursive=True) if not py_compile.compile(f, doraise=True)))"
```

### Building and Running

```bash
# Initialize knowledge graph (one-time)
python3 knowledge_graph.py init

# Run discovery to populate initial data
python3 discovery_engine.py discover

# Start specific daemon manually (for development)
python3 sorting_daemon.py scan
python3 context_manager.py start
python3 agents/maintainer.py

# Load daemons as LaunchAgents (production)
launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.sync-daemon.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.maintenance-daemon.plist

# Verify daemons running
launchctl list | grep metasystem
```

### Common Development Tasks

```bash
# Query knowledge graph
python3 knowledge_graph.py search --query="python" --type=project

# Check system health
python3 agents/maintainer.py

# View recent conversations
python3 context_manager.py recent

# Sync to iCloud/external drive
python3 sync_engine.py sync

# Check sync status
python3 sync_engine.py status

# View system statistics
python3 knowledge_graph.py stats

# Test context persistence
python3 context_manager.py start
python3 context_manager.py log-decision --decision="Test" --rationale="Testing"
python3 context_manager.py recent
```

## Architecture

### Core Components

#### 1. Knowledge Graph (`knowledge_graph.py`)
- **Purpose**: Central SQLite database with FTS5 full-text search
- **Key Class**: `KnowledgeGraph`
- **Main Methods**: 
  - `insert_entity()` / `get_entity()` / `update_entity()` - CRUD for entities
  - `search()` - Full-text search across all entities
  - `add_relationship()` / `get_relationships()` - Entity relationships
  - `insert_conversation()` - Log conversation metadata
  - `check_integrity()` / `vacuum()` - Maintenance operations
- **Data Stored**: Projects, files, conversations, decisions, tools, dotfiles
- **Database Path**: `~/.metasystem/metastore.db`

#### 2. Context Manager (`context_manager.py`)
- **Purpose**: Persist AI conversation context to prevent loss across sessions
- **Key Class**: `ConversationManager`
- **Main Methods**:
  - `start_conversation()` - Begin new conversation tracking
  - `log_file_access()` / `log_decision()` - Record work context
  - `get_context_for_resume()` - Retrieve full conversation state
  - `search_conversations()` - Find previous conversations
- **Workflow**: Logs conversation ID → records all file access/decisions → enables resume

#### 3. Autonomous Agents (`agents/`)

**Maintainer** (`agents/maintainer.py`)
- Daily health checks, database integrity, orphaned entity cleanup
- Auto-repair capabilities
- Called by maintenance daemon at 2 AM daily

**Cataloger** (`agents/cataloger.py`)
- Continuous discovery of new projects with `seed.yaml`
- Detects installed tools (Homebrew, npm)
- Incremental updates via SHA256 hashing

**Synthesizer** (`agents/synthesizer.py`)
- Generates 7 markdown docs from knowledge graph
- Creates mermaid architecture diagrams
- Only regenerates on content changes

**Dotfile Watcher** (`agents/dotfile_watcher.py`)
- Tracks all chezmoi-managed dotfiles
- Queries changes via git log
- Enables "what changed this week?" functionality

#### 4. Background Daemons

**Sorting Daemon** (`sorting_daemon.py`)
- Every 5 minutes: Organizes Downloads folder
- Categorizes files by type, moves to appropriate locations
- Logs all movements to knowledge graph

**Sync Daemon** (`sync_daemon.py`)
- Every 5 minutes: Syncs KG to iCloud + external drive
- SHA256-based change detection, conflict resolution
- Automatic backups before overwrites

**Maintenance Daemon** (`maintenance_daemon.py`)
- Daily at 2 AM: Master orchestrator
- Runs all agent tasks: health checks, discovery, doc generation
- Syncs chezmoi state, regenerates documentation

#### 5. Discovery Engine (`discovery_engine.py`)
- Scans workspace for `seed.yaml` files
- Extracts tech stack, dependencies
- Creates knowledge graph entities for projects/tools

#### 6. Multi-Machine Sync (`sync_engine.py`)
- Bidirectional sync: local ↔ iCloud ↔ external drive
- Conflict resolution (newest wins)
- Automatic backups and integrity verification

### Data Model

**Core Tables** (in `metastore.db`):
- `entities` - All objects (projects, files, tools, decisions, dotfiles)
- `relationships` - Connections between entities
- `conversations` - AI conversation metadata
- `facts` - Timestamped decisions/facts
- `snapshots` - Point-in-time database snapshots
- `sync_log` - Multi-machine sync history
- `entities_fts` - Full-text search index

**Key Entity Types**:
- `project` - Workspace projects with tech stack
- `file` - Organized files from sorting daemon
- `conversation` - AI conversation sessions
- `decision` - Architectural choices
- `tool` - Installed software/configs
- `dotfile` - chezmoi-managed configs

### Execution Flow

**On Application Start**:
1. `context_manager.py start` - Create conversation record
2. User performs work, accessing files
3. Daemons run in background (every 5 min)

**Every 5 Minutes**:
- Sorting daemon organizes files
- Sync daemon pushes to iCloud/external
- These run via LaunchAgents

**Daily at 2 AM**:
- Maintenance daemon runs all agents
- Health checks and auto-repair
- Discovery of new projects/tools
- Documentation regeneration
- Dotfile change tracking

**On Conversation Resume**:
1. `context_manager.py recent` - Find previous conversation
2. `context_manager.py resume --conv-id=<ID>` - Retrieve full context
3. KG provides all decisions, files, conversations from that session

### Code Patterns

**Singleton Database Connection**:
```python
# KnowledgeGraph uses thread-safe connection pooling
kg = KnowledgeGraph()
conn = kg._get_conn()  # Gets connection with timeout
```

**Entity CRUD Pattern**:
```python
# Standard insert/get/update/delete
kg.insert_entity(type='project', data={'name': 'my-project', ...})
entity = kg.get_entity(entity_id)
kg.update_entity(entity_id, {'tech_stack': 'python'})
kg.delete_entity(entity_id)
```

**Relationship Management**:
```python
# Link entities together
kg.add_relationship(source_id, 'depends_on', target_id)
relationships = kg.get_relationships(source_id, 'depends_on')
```

**Full-Text Search**:
```python
# FTS5 search across all entity content
results = kg.search('react typescript', type='project')
```

**Error Handling**:
- Database locking: exponential backoff with timeout
- Missing chezmoi items: graceful fallback in templates
- Sync conflicts: timestamp-based resolution (newest wins)

## Testing Strategy

**Test Categories** (from `pytest.ini`):
- `unit` - Fast, isolated tests of individual functions
- `integration` - Component interactions
- `e2e` - Complete workflows
- `performance` - Benchmarks with pytest-benchmark
- `slow` - Long-running tests (can skip)

**Test Organization**:
- Tests in `tests/` directory
- Coverage target: 80% minimum
- Run with: `pytest --cov` (generates HTML report in `htmlcov/`)

**Key Areas to Test**:
1. Knowledge graph CRUD operations
2. Sync conflict resolution
3. Entity relationship integrity
4. Full-text search accuracy
5. Daemon scheduling and execution
6. Context persistence across conversations

## Key Files and Their Responsibilities

| File | Purpose | Key Methods |
|------|---------|-------------|
| `knowledge_graph.py` | Core data store with SQLite + FTS5 | search, insert_entity, add_relationship |
| `context_manager.py` | AI conversation persistence | start_conversation, log_decision, resume |
| `discovery_engine.py` | Project/tool discovery | discover, scan_tools |
| `sync_engine.py` | Multi-machine sync | sync, status, verify |
| `sorting_daemon.py` | File organization (every 5 min) | scan |
| `maintenance_daemon.py` | Master orchestrator (daily 2 AM) | run_daily_maintenance |
| `agents/maintainer.py` | Health checks & auto-repair | (run directly) |
| `agents/cataloger.py` | Continuous discovery | scan |
| `agents/synthesizer.py` | Auto-doc generation | generate_docs |
| `agents/dotfile_watcher.py` | Config tracking | query, sync |
| `metasystem_cli.py` | User-facing CLI interface | (various commands) |

## Configuration and State

**Configuration Files**:
- `seed.yaml` - Project metadata (tech stack, dependencies)
- `sorting-rules.yaml` - File organization rules (in `~/.metasystem/`)
- `pytest.ini` - Test configuration

**State Directories**:
- `~/.metasystem/metastore.db` - Knowledge graph database
- `~/.metasystem/logs/` - All daemon logs
- `~/.metasystem/cataloger-state.json` - Discovery state tracking
- `~/Library/LaunchAgents/` - Daemon plists (production)

**Important Notes**:
- Database changes should always go through `KnowledgeGraph` class for consistency
- Daemons use LaunchAgents for scheduling (not cron)
- Sync backups are created automatically (`.backup-YYYYMMDD-HHMMSS` files)
- All logging goes to `~/.metasystem/logs/` for observability

## Debugging

**Enable Debug Output**:
- Add `--debug` flag to daemon plist arguments
- Logs go to `~/.metasystem/logs/<daemon>.log`
- View with `tail -f ~/.metasystem/logs/*.log`

**Database Inspection**:
```bash
# Check integrity
sqlite3 ~/.metasystem/metastore.db "PRAGMA integrity_check"

# Query directly
sqlite3 ~/.metasystem/metastore.db "SELECT * FROM entities WHERE type='project'"

# Check FTS index
sqlite3 ~/.metasystem/metastore.db "SELECT * FROM entities_fts WHERE entities_fts MATCH 'react'"
```

**Common Issues and Solutions** - See `TROUBLESHOOTING.md` for comprehensive guide

## Performance Considerations

- **Knowledge Graph Queries**: O(1) entity lookups, O(n) for searches (FTS5 optimized)
- **Sync Operations**: SHA256 change detection prevents unnecessary transfers
- **Daemon Frequency**: 5-min daemons are throttled; critical paths only
- **Database Maintenance**: Weekly VACUUM recommended for large databases
- **Memory**: Minimal footprint; suitable for background processes

## Security

**Secrets Management**:
- No secrets in git (checked via pre-commit)
- 1Password CLI for dynamic secrets
- GitHub auth via `gh` CLI (not plaintext tokens)
- AWS credentials from 1Password (not in dotfiles)

**Data Protection**:
- Automatic backups before sync overwrites
- Database integrity checks daily
- Git history for all chezmoi changes
- No credentials stored in knowledge graph

## Important Architectural Decisions

1. **SQLite + FTS5 over PostgreSQL**: Simplicity and portability for a personal system
2. **Python for agents**: Easy to modify, sufficient performance for automation
3. **LaunchAgents over cron**: macOS-native, better error handling
4. **Timestamp-based sync conflict resolution**: Simple and deterministic
5. **YAML for configuration**: Human-readable, no special parsing needed
6. **chezmoi for dotfiles**: Proven tool with git history and secret support

## Future Development

The system is modular, allowing additions without breaking existing functionality:
- New agent types can be added to `agents/` directory
- New entity types automatically supported by knowledge graph schema
- Daemon scheduling can be extended via LaunchAgent plists
- Sync destinations can be added to `sync_engine.py`

See `README.md` for completed phases and potential enhancements.
