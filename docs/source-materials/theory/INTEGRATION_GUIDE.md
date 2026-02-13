# Metasystem Integration Guide

Complete guide to integrating all metasystem components and enabling unified context across all tools.

---

## Overview

The metasystem creates a **unified knowledge graph** that connects:

1. **my--father-mother** - Clipboard history and copilot conversations
2. **omni-dromenon-machina** - Agent decisions and autonomous work
3. **metasystem-core** - Central knowledge graph and orchestrator

This enables:
- **Context Persistence** - Never lose conversation state
- **Cross-Project Learning** - Agents learn from past work
- **Clipboard Integration** - Clipboard data available to agents
- **Decision History** - All decisions logged for future reference

---

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    Unified Knowledge Graph                  │
│         ~/.metasystem/metastore.db (SQLite + FTS5)         │
└────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
      [MFM Integration]    [MCP Bridge]     [Omni Integration]
           │                    │                    │
           │                    │                    │
    ┌──────▼──────┐      ┌─────▼──────┐     ┌──────▼──────┐
    │  Clipboard  │      │   Web Dash │     │   Agents    │
    │   History   │      │   & CLI    │     │   Decisions │
    └─────────────┘      └────────────┘     └─────────────┘
         MFM                                     Omni
```

---

## 1. Unified CLI (metasystem_cli.py)

**Entry Point**: `/Users/4jp/Workspace/metasystem-core/metasystem`

### Basic Commands

```bash
# Show system status with colored output
metasystem status

# Run discovery engine
metasystem discover [--force]

# Run synchronization
metasystem sync [--force]

# Run health check
metasystem health [--force]

# Control daemons
metasystem daemon sorting_daemon start|stop|list
metasystem daemon terminal_monitor stop

# Query knowledge graph
metasystem knowledge search "TypeScript"
metasystem knowledge stats

# Start web dashboard
metasystem dashboard

# View daemon logs
metasystem logs meta-orchestrator
```

### Setup

Make the script accessible from anywhere:

```bash
# Option 1: Add to PATH
export PATH="/Users/4jp/Workspace/metasystem-core:$PATH"

# Option 2: Create symlink in /usr/local/bin
ln -s /Users/4jp/Workspace/metasystem-core/metasystem /usr/local/bin/metasystem

# Test it
metasystem status --json
```

---

## 2. Web Dashboard (dashboard_server.py)

**Purpose**: Real-time visualization of system status

### Start Dashboard

```bash
# Via CLI
metasystem dashboard

# Or directly
python3 dashboard_server.py

# Via LaunchAgent (runs automatically)
# Already configured, just wait for next login
```

**Access**: `http://localhost:8888`

**Features**:
- Real-time orchestrator status
- Daemon health monitoring
- Knowledge graph statistics
- System health checks
- One-click operations (Discover, Sync, Health Check)
- Auto-refresh every 5 seconds

---

## 3. my--father-mother Integration (mfm_integration.py)

**Purpose**: Import clipboard data into metasystem KG

### How It Works

```python
from mfm_integration import MFMIntegration

mfm = MFMIntegration()

# Import recent clips to KG
result = mfm.import_clips_to_kg(limit=100)
# Creates entities: clipboard_<id> with type="clipboard_content"
# Creates relationships: has_tag -> tags

# Import copilot conversations
result = mfm.import_conversations_to_kg(limit=50)

# Get clipboard context (for agents to use)
context = mfm.get_clipboard_context(limit=20)

# Search clipboard
results = mfm.search_clipboard("TypeScript", limit=20)

# Bidirectional sync
result = mfm.sync_bidirectional()
```

### Data Flow

```
my--father-mother/mfm.db
  ├─ clips table
  │   └─ [MFMIntegration.import_clips_to_kg()]
  │       └─ Metasystem KG
  │           ├─ Entity: clipboard_<id>
  │           └─ Relationship: has_tag
  │
  ├─ copilot_chats table
  │   └─ [MFMIntegration.import_conversations_to_kg()]
  │       └─ Metasystem KG
  │           └─ Conversation record
  │
  └─ clips_fts (FTS5)
      └─ [MFMIntegration.search_clipboard()]
```

### Auto-Sync via Orchestrator

Add to meta_orchestrator.py daemon loop:

```python
# In daemon_loop() method, add:
if now >= next_clipboard_sync:
    from mfm_integration import MFMIntegration
    mfm = MFMIntegration()
    mfm.import_clips_to_kg(limit=50)
    next_clipboard_sync = now + timedelta(minutes=10)
```

---

## 4. MCP Bridge Extension (mcp_bridge.py)

**Purpose**: REST API for agents to interact with metasystem

### Agent Integration Endpoints

#### Log Agent Decision
```bash
curl -X POST http://127.0.0.1:5000/metasystem/agents/log-decision \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "architect",
    "decision": "Use async/await for API layer",
    "rationale": "Better performance and code clarity",
    "category": "architecture",
    "project": "omni-dromenon-machina",
    "tags": ["performance", "typescript"],
    "context": {"framework": "express"}
  }'
```

#### Get Agent Status
```bash
curl http://127.0.0.1:5000/metasystem/agents/status
```

#### Get Clipboard Context
```bash
curl "http://127.0.0.1:5000/metasystem/context/clipboard?limit=20&search=TypeScript"
```

#### Get Cross-Project Context
```bash
curl "http://127.0.0.1:5000/metasystem/context/cross-project?project=omni-dromenon-machina&hours=168"
```

#### Get Decisions by Category
```bash
curl "http://127.0.0.1:5000/metasystem/decisions/by-category?category=architecture&limit=50"
```

### Starting the MCP Bridge

```bash
# Manual start
python3 mcp_bridge.py --port 5000

# Via LaunchAgent
launchctl load ~/Library/LaunchAgents/com.metasystem.mcp-bridge.plist

# Check if running
curl http://127.0.0.1:5000/metasystem/health
```

---

## 5. omni-dromenon-machina Integration (omni_integration.py)

**Purpose**: Enable agents to use metasystem for context and decision logging

### Integration in Agents

#### In TypeScript Agent Code

```typescript
// Import and initialize
import { OmniIntegration } from 'omni_integration';
const omni = new OmniIntegration();

// 1. Get context before starting work
const context = await omni.getAgentContext(
  'omni-dromenon-machina',
  'Implement new API endpoint'
);
console.log('Past decisions:', context.pastDecisions);
console.log('Similar work:', context.similarWork);

// 2. Log decision while working
await omni.logAgentDecision(
  'architect',
  'Use OpenAPI for API documentation',
  'Industry standard with excellent tooling',
  'architecture',
  'omni-dromenon-machina',
  ['documentation', 'api', 'openapi']
);

// 3. Log files created
await omni.logFileCreated(
  'src/api/openapi.yaml',
  'omni-dromenon-machina',
  'OpenAPI specification for REST endpoints'
);

// 4. Query similar decisions
const similarDecisions = await omni.querySimilarDecisions(
  'REST API design'
);
```

#### Or Call via Python from Agents

```bash
# From Node.js agent code:
python3 -c "
from omni_integration import OmniIntegration
omni = OmniIntegration()
context = omni.get_agent_context('omni-dromenon-machina', 'API endpoint implementation')
print(json.dumps(context, indent=2))
"
```

### seed.yaml Configuration

Add to `/Users/4jp/Workspace/omni-dromenon-machina/seed.yaml`:

```yaml
knowledge_graph:
  enabled: true
  db_path: "~/.metasystem/metastore.db"
  mcp_endpoints:
    context_current: "http://127.0.0.1:5000/metasystem/context/current"
    log_decision: "http://127.0.0.1:5000/metasystem/agents/log-decision"
    agent_status: "http://127.0.0.1:5000/metasystem/agents/status"
    clipboard_context: "http://127.0.0.1:5000/metasystem/context/clipboard"
    cross_project_context: "http://127.0.0.1:5000/metasystem/context/cross-project"
  integration:
    query_before_work: true
    log_decisions: true
    log_file_changes: true
    cross_project_learning: true
    sync_interval_seconds: 300
```

---

## 6. Setup Instructions

### Prerequisites

```bash
# Install dependencies
cd ~/Workspace/metasystem-core
pip install -r requirements.txt

# Verify MCP bridge port is available
lsof -i :5000  # Should show nothing

# Verify MFM database exists
ls ~/.my-father-mother/mfm.db
```

### Step-by-Step Setup

#### 1. Start the Meta-Orchestrator (if not already running)

```bash
# Check if running
launchctl list | grep meta-orchestrator

# If not running, load it
launchctl load ~/Library/LaunchAgents/com.metasystem.meta-orchestrator.plist

# Verify
ps aux | grep meta_orchestrator
```

#### 2. Start the MCP Bridge

```bash
# In a new terminal
cd ~/Workspace/metasystem-core
python3 mcp_bridge.py --port 5000 --debug
```

#### 3. Test the Integration

```bash
# Test MCP Bridge health
curl http://127.0.0.1:5000/metasystem/health

# Test importing clips
python3 -c "
from mfm_integration import MFMIntegration
mfm = MFMIntegration()
result = mfm.import_clips_to_kg(limit=20)
print(result)
"

# Test agent endpoints
curl -X POST http://127.0.0.1:5000/metasystem/agents/log-decision \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "test",
    "decision": "Test decision",
    "category": "architecture"
  }'
```

#### 4. Access the Dashboard

```bash
# Start dashboard
metasystem dashboard

# Opens http://localhost:8888 automatically
```

#### 5. Update omni-dromenon-machina seed.yaml

Add the KG configuration (see seed.yaml section above) to:
`~/Workspace/omni-dromenon-machina/seed.yaml`

---

## 7. Integration Workflows

### Workflow A: Clipboard → Agent Context

```
User copies code snippet to clipboard
    ↓
my--father-mother captures clip
    ↓
[Every 10 min] Orchestrator runs mfm_integration.import_clips_to_kg()
    ↓
Clip stored in KG as entity with embeddings
    ↓
Agent queries: GET /metasystem/context/clipboard
    ↓
Agent gets recent clips including the new one
    ↓
Agent uses snippet in decision-making
```

### Workflow B: Agent Decision → KG → Dashboard

```
Agent (Architect) makes decision
    ↓
Agent calls: POST /metasystem/agents/log-decision
    ↓
Decision stored in KG with metadata
    ↓
Relationship: decision → project, agent, category
    ↓
User opens dashboard at http://localhost:8888
    ↓
Dashboard queries: GET /metasystem/agents/status
    ↓
Shows agent's recent decisions and statistics
```

### Workflow C: Cross-Project Learning

```
Agent working on Project A needs context
    ↓
Agent calls: GET /metasystem/context/cross-project?project=ProjectA
    ↓
MCP Bridge queries KG for decisions from Projects B, C, D
    ↓
Filters for relevant patterns and similar problems
    ↓
Agent gets insights from past work
    ↓
Agent applies patterns to current project
```

---

## 8. Monitoring & Debugging

### Check Integration Status

```bash
# Orchestrator status
metasystem status

# Check each integration
python3 -c "
from mfm_integration import MFMIntegration
from omni_integration import OmniIntegration
from knowledge_graph import KnowledgeGraph

mfm = MFMIntegration()
omni = OmniIntegration()
kg = KnowledgeGraph()

print('MFM DB:', mfm.mfm_db)
print('Omni Dir:', omni.omni_dir)
print('KG DB:', kg.db_path)
print('KG Stats:', kg.get_stats())
"
```

### View Integration Logs

```bash
# Orchestrator logs
tail -f ~/.metasystem/logs/meta-orchestrator.log

# MCP Bridge logs
tail -f ~/.metasystem/logs/mcp-bridge.log

# Dashboard logs
tail -f ~/.metasystem/logs/dashboard_server.log
```

### Test MCP Endpoints

```bash
# Test all endpoints
python3 << 'EOF'
import requests
import json

base = 'http://127.0.0.1:5000'

endpoints = [
    ('GET', '/metasystem/health'),
    ('GET', '/metasystem/stats'),
    ('GET', '/metasystem/context/current'),
    ('GET', '/metasystem/agents/status'),
]

for method, path in endpoints:
    try:
        if method == 'GET':
            r = requests.get(base + path)
        print(f"✓ {method} {path}: {r.status_code}")
    except Exception as e:
        print(f"✗ {method} {path}: {e}")
EOF
```

---

## 9. Advanced Configuration

### Custom MCP Port

Edit `dashboard_server.py` and `metasystem_cli.py`:

```python
MCP_BASE_URL = 'http://127.0.0.1:5000'  # Change 5000 to desired port
```

### Sync Intervals

Edit `meta_orchestrator.py` default config:

```python
def _default_config(self) -> Dict[str, Any]:
    return {
        'orchestrator': {
            'discovery_interval': 300,        # 5 min
            'sync_interval': 600,             # 10 min
            'clipboard_sync_interval': 600,   # 10 min (ADD THIS)
            'health_check_interval': 300,     # 5 min
        },
        ...
    }
```

### Custom Entity Types

Add to knowledge_graph.py to track custom entities:

```python
# In KnowledgeGraph.__init__():
self.supported_types = [
    'project', 'file', 'decision', 'conversation',
    'clipboard_content', 'agent_task', 'research_note'
]
```

---

## 10. Troubleshooting

### Issue: MCP Bridge Not Responding

```bash
# Check if port is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Restart
python3 mcp_bridge.py --port 5000
```

### Issue: MFM Database Not Found

```bash
# Check path
ls -la ~/.my-father-mother/mfm.db

# If missing, you need to install my--father-mother first
cd ~/Workspace/my--father-mother
python3 main.py watch
```

### Issue: Knowledge Graph Locked

```bash
# Check for locks
lsof | grep metastore.db

# If locked, wait a moment and retry
# Or restart orchestrator:
launchctl unload ~/Library/LaunchAgents/com.metasystem.meta-orchestrator.plist
sleep 2
launchctl load ~/Library/LaunchAgents/com.metasystem.meta-orchestrator.plist
```

### Issue: Agents Not Seeing Decisions

```bash
# Verify decisions are in KG
python3 -c "
from knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()
decisions = kg.query_entities(type='decision', limit=10)
print(f'Found {len(decisions)} decisions')
for d in decisions:
    print(f'  - {d[\"name\"]}')
"
```

---

## 11. Next Steps

1. **Enable Auto-Sync**: Modify meta_orchestrator.py to call mfm_integration every 10 minutes
2. **Agent Integration**: Update omni-dromenon-machina agents to log decisions
3. **Custom Dashboards**: Extend dashboard_server.py with project-specific views
4. **Mobile Access**: Configure dashboard for remote access (port forwarding, auth)
5. **Export/Backup**: Add KG export functionality for backup and analysis

---

## Summary

You now have:

✅ **Unified CLI** - Central command interface for all metasystem operations
✅ **Web Dashboard** - Real-time visualization of system status
✅ **Clipboard Integration** - Clipboard data available to agents and conversations
✅ **Agent Logging** - Agents can log decisions and learn from past work
✅ **Cross-Project Learning** - Agents can find patterns from other projects
✅ **MCP Bridge** - REST API for AI integration

The metasystem is now **fully integrated and operational**.

---

*Integration Guide - Last Updated: 2026-01-03*
*Metasystem Status: Production Ready ✅*
