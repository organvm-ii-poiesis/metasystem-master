# Phase 10: Deployment & Production Features

**Date**: 2026-01-02
**Status**: 🚀 Starting
**Goal**: Deploy tested system + add terminal session capture

---

## Overview

Phase 10 focuses on:
1. **Terminal Session Capture** - Automatically export terminal windows to .txt on close
2. **Production Deployment** - Make the system run automatically
3. **Multi-Machine Sync** - Enable seamless work across devices
4. **Monitoring & Observability** - Track system health

---

## Priority 1: Terminal Session Capture (NEW FEATURE)

### Goal
Automatically capture and save terminal window contents when windows close, enabling:
- Session replay and review
- Command history with context
- Knowledge graph integration
- Searchable terminal history

### Supported Terminals
- Terminal.app (macOS default)
- iTerm2 (popular alternative)
- Kitty (modern GPU-accelerated)

### Implementation Approach

**Architecture**:
```
Terminal Window Close
    ↓
Terminal Monitor Daemon (detects close event)
    ↓
Content Extractor (terminal-specific)
    ↓
Export to ~/Documents/TerminalExports/YYYY-MM-DD/session-{timestamp}.txt
    ↓
Log to Knowledge Graph (optional)
```

**Components**:

1. **Terminal Monitor Daemon** (`terminal_monitor.py`)
   - Runs in background via LaunchAgent
   - Monitors terminal windows
   - Detects close events
   - Triggers export

2. **Content Extractors** (per terminal type)
   - `terminal_app_extractor.py` - AppleScript-based
   - `iterm2_extractor.py` - iTerm2 Python API
   - `kitty_extractor.py` - Kitty remote control

3. **Export Manager** (`terminal_export_manager.py`)
   - Saves to organized directory structure
   - Handles file naming
   - Optional KG integration

4. **Configuration** (`~/.metasystem/terminal-export.yaml`)
   ```yaml
   settings:
     enabled: true
     export_directory: ~/Documents/TerminalExports
     max_file_size_mb: 10
     log_to_kg: true

   terminals:
     terminal_app:
       enabled: true
       capture_scrollback: true
     iterm2:
       enabled: true
       capture_scrollback: true
     kitty:
       enabled: true
       capture_scrollback: true

   filters:
     exclude_patterns:
       - "password"
       - "secret"
       - "token"
     min_lines: 10  # Don't save tiny sessions
   ```

### Files to Create

| File | Purpose | Lines |
|------|---------|-------|
| `terminal_monitor.py` | Main daemon | ~300 |
| `terminal_app_extractor.py` | Terminal.app support | ~150 |
| `iterm2_extractor.py` | iTerm2 support | ~150 |
| `kitty_extractor.py` | Kitty support | ~150 |
| `terminal_export_manager.py` | Export coordination | ~200 |
| `~/Library/LaunchAgents/com.metasystem.terminal-monitor.plist` | Auto-start | ~30 |
| `~/.metasystem/terminal-export.yaml` | Configuration | ~50 |

### Implementation Steps

1. **Create basic Terminal.app extractor** (AppleScript)
2. **Create export manager** (file saving logic)
3. **Create monitor daemon** (detect window close)
4. **Add iTerm2 support** (Python API)
5. **Add Kitty support** (remote control)
6. **Create LaunchAgent** (auto-start)
7. **Integrate with KG** (optional logging)
8. **Add tests** (unit + integration)

---

## Priority 2: Production Deployment

### LaunchAgents Setup

Create LaunchAgents for:
- `meta_orchestrator` - Main system coordinator
- `sorting_daemon` - File organization
- `terminal_monitor` - Terminal export

### Auto-Start Configuration

```xml
<!-- ~/Library/LaunchAgents/com.metasystem.orchestrator.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metasystem.orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/4jp/Workspace/metasystem-core/.venv/bin/python3</string>
        <string>/Users/4jp/Workspace/metasystem-core/meta_orchestrator.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

---

## Priority 3: Multi-Machine Sync

### Sync Strategy

**Locations**:
- iCloud Drive: `~/Library/Mobile Documents/com~apple~CloudDocs/.metasystem/`
- External Drive: `/Volumes/4444-iivii/.metasystem/` (when mounted)

**Sync Items**:
- Knowledge graph database
- Configuration files
- Terminal exports (optional, size-dependent)
- Conversation history

**Implementation**:
- Use `rsync` for file-level sync
- SQLite database: copy when idle
- Conflict resolution: newest wins (configurable)

---

## Priority 4: Monitoring & Observability

### Health Checks

Create `agents/health_monitor.py`:
- Database integrity checks
- File organization status
- Daemon health
- Disk space monitoring

### Logging

- Centralized logging to `~/.metasystem/logs/`
- Log rotation
- Error alerting (macOS notifications)

---

## Timeline

### Quick Win (1-2 hours)
✅ Terminal.app export (basic implementation)
✅ Export manager
✅ Basic testing

### Phase 10 Core (4-6 hours)
- iTerm2 support
- Kitty support
- LaunchAgent setup
- KG integration
- Comprehensive testing

### Extended Features (optional)
- Multi-machine sync
- Health monitoring
- Advanced filtering
- Session replay viewer

---

## Success Criteria

| Feature | Criteria | Status |
|---------|----------|--------|
| Terminal export | Captures on window close | ⏳ |
| Terminal.app | Fully supported | ⏳ |
| iTerm2 | Fully supported | ⏳ |
| Auto-start | Runs on login | ⏳ |
| KG integration | Logs to graph | ⏳ |
| Tests | >90% coverage | ⏳ |

---

## Next Actions

1. **Implement Terminal.app extractor** (quick win)
2. **Create export manager**
3. **Test basic export**
4. **Add iTerm2 support**
5. **Create LaunchAgent**
6. **Integrate with KG**

---

*Phase 10 started: 2026-01-02*
*Focus: Terminal capture + deployment*
*Expected completion: 1-2 sessions*
