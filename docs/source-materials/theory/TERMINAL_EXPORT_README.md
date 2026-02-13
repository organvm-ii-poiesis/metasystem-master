# Terminal Session Export Feature

**Status**: ✅ **Working** (Terminal.app support)
**Created**: 2026-01-02
**Phase**: 10 - Deployment & Production Features

---

## Overview

Automatically capture and save terminal window contents to text files, enabling:
- Session replay and review
- Command history with full context
- Searchable terminal history
- Knowledge graph integration (optional)

---

## Quick Start

### 1. Initialize Configuration

```bash
source .venv/bin/activate
python terminal_export_manager.py --init-config
```

This creates `~/.metasystem/terminal-export.yaml` with default settings.

### 2. Manual Export

Export your current terminal window:

```bash
./export_terminal.sh
```

Or use the Python interface:

```bash
source .venv/bin/activate
python terminal_app_extractor.py --frontmost --export
```

### 3. View Exports

Exports are saved to `~/Documents/TerminalExports/` organized by date:

```
~/Documents/TerminalExports/
├── 2026-01-02/
│   ├── session-171540-terminal_app-3e85e102.txt
│   ├── session-172335-terminal_app-a9f3c7d1.txt
│   └── ...
└── 2026-01-03/
    └── ...
```

---

## Features

### Currently Supported

✅ **Terminal.app** (macOS default)
- Capture window content via AppleScript
- Extract window title and metadata
- Support for multiple windows
- Configurable filters

### Planned

⏳ **iTerm2** (via Python API)
⏳ **Kitty** (via remote control)
⏳ **Auto-export on window close**
⏳ **Knowledge graph integration**

---

## Configuration

Edit `~/.metasystem/terminal-export.yaml`:

```yaml
settings:
  enabled: true
  export_directory: ~/Documents/TerminalExports
  max_file_size_mb: 10
  log_to_kg: false  # Enable to log to knowledge graph
  organize_by_date: true  # Group by date folders

terminals:
  terminal_app:
    enabled: true
    capture_scrollback: true

filters:
  exclude_patterns:
    - password
    - secret
    - token
    - API_KEY
  min_lines: 10  # Don't save tiny sessions
  max_lines: 100000
```

---

## Usage

### List Recent Exports

```bash
python terminal_export_manager.py --list
```

### View Statistics

```bash
python terminal_export_manager.py --stats
```

Output:
```
📊 Export Statistics:
  Total exports: 12
  Total size: 2.45 MB
  Export directory: /Users/4jp/Documents/TerminalExports
```

### Capture Specific Window

```bash
python terminal_app_extractor.py --capture 1 --export  # Capture window 1
python terminal_app_extractor.py --capture 2 --export  # Capture window 2
```

### Capture All Windows

```bash
python terminal_app_extractor.py --capture-all --export
```

---

## Export Format

Each exported session includes:

```
# Terminal Session Export
# Exported: 2026-01-02T17:15:40.180338
# terminal_type: terminal_app
# window_title: Terminal — metasystem-core
# columns: 80
# rows: 24
#
================================================================================

[Terminal content here...]
```

---

## Permissions

**Important**: Terminal.app may need accessibility permissions for AppleScript to capture window content.

If capture fails:
1. Go to **System Settings** → **Privacy & Security** → **Accessibility**
2. Grant permission to **Terminal.app**
3. Try exporting again

---

## Integration with Knowledge Graph

To enable KG integration:

1. Edit config: `log_to_kg: true`
2. Exports will be logged as entities:

```python
{
    'type': 'terminal_session',
    'name': 'session-171540-terminal_app-3e85e102.txt',
    'path': '/Users/4jp/Documents/TerminalExports/...',
    'metadata': {
        'exported_at': '2026-01-02T17:15:40',
        'file_size': 2048,
        'terminal_type': 'terminal_app',
        'window_title': 'Terminal — metasystem-core'
    }
}
```

3. Query exports:

```python
from knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph('~/.metasystem/metastore.db')
sessions = kg.query_entities(type='terminal_session', limit=10)
```

---

## Automatic Export on Window Close

**Status**: Planned

Will be implemented via:
- Background LaunchAgent daemon
- Monitors terminal windows
- Exports on close event
- See `PHASE_10_PLAN.md` for details

---

## Architecture

```
User closes terminal window
    ↓
Terminal Monitor Daemon (detects event)
    ↓
Terminal Extractor (AppleScript/API)
    ↓
Export Manager (saves file)
    ↓
Knowledge Graph (optional logging)
    ↓
~/Documents/TerminalExports/YYYY-MM-DD/session-*.txt
```

### Components

| File | Purpose | Status |
|------|---------|--------|
| `terminal_export_manager.py` | Manages exports and file organization | ✅ Working |
| `terminal_app_extractor.py` | Extracts from Terminal.app | ✅ Working |
| `export_terminal.sh` | Quick manual export script | ✅ Working |
| `iterm2_extractor.py` | Extracts from iTerm2 | ⏳ Planned |
| `kitty_extractor.py` | Extracts from Kitty | ⏳ Planned |
| `terminal_monitor.py` | Background daemon | ⏳ Planned |

---

## Testing

### Run Test Export

```bash
python terminal_export_manager.py --test
```

This creates a test export with sample content.

### Verify Export

```bash
ls -lh ~/Documents/TerminalExports/$(date +%Y-%m-%d)/
cat ~/Documents/TerminalExports/$(date +%Y-%m-%d)/session-*.txt
```

---

## Troubleshooting

### "Could not capture frontmost window"

**Cause**: Accessibility permissions not granted

**Solution**:
1. System Settings → Privacy & Security → Accessibility
2. Add Terminal.app
3. Restart Terminal.app

### "No Terminal windows found"

**Cause**: Terminal.app not running or no windows open

**Solution**: Open a Terminal window and try again

### Exports are too large

**Cause**: Long-running sessions with lots of output

**Solution**: Adjust `max_file_size_mb` in config, or filter content

---

## Privacy & Security

### Sensitive Data Filtering

The export manager includes basic filtering for sensitive patterns:
- `password`
- `secret`
- `token`
- `API_KEY`
- `aws_access_key`

Sessions containing these patterns are still exported but marked for review.

### Custom Filters

Add your own patterns in `~/.metasystem/terminal-export.yaml`:

```yaml
filters:
  exclude_patterns:
    - my_secret_pattern
    - confidential
```

---

## Roadmap

### v1.0 (Current) - Terminal.app Support
- ✅ Manual export
- ✅ Configuration system
- ✅ File organization
- ✅ Basic filtering

### v1.1 (Next) - Multi-Terminal Support
- ⏳ iTerm2 integration
- ⏳ Kitty integration
- ⏳ Auto-detection of terminal type

### v1.2 - Automation
- ⏳ Auto-export on window close
- ⏳ Background daemon
- ⏳ LaunchAgent setup

### v2.0 - Advanced Features
- ⏳ Session replay viewer
- ⏳ Command extraction
- ⏳ Smart filtering (ML-based)
- ⏳ Cross-machine sync

---

## License

Part of the metasystem-core project.

---

*Created: 2026-01-02*
*Status: Working MVP*
*Next: iTerm2 + auto-export*
