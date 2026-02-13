# Phase 10: Deployment Guide

**Status**: ✅ **READY FOR DEPLOYMENT**
**Date**: 2026-01-02
**Components**: Terminal export, auto-monitoring, health checks

---

## Quick Start (5 minutes)

### 1. Initialize Configuration

```bash
cd ~/Workspace/metasystem-core
source .venv/bin/activate
python terminal_export_manager.py --init-config
```

### 2. Install LaunchAgents

```bash
./install_launchagents.sh
```

This installs:
- ✅ **Terminal Monitor** - Auto-exports terminal sessions (ENABLED)
- ⏸️ **Sorting Daemon** - File organization (disabled)
- ⏸️ **Health Monitor** - System health checks (disabled)

### 3. Verify Installation

```bash
# Check running agents
launchctl list | grep com.metasystem

# View logs
tail -f ~/.metasystem/logs/terminal-monitor.log
```

**Done!** Terminal monitor is running in background.

---

## Features

### ✅ Terminal Session Export

**Manually export current terminal:**
```bash
./export_terminal.sh
```

**Export from any terminal emulator:**
```bash
source .venv/bin/activate

# Terminal.app
python terminal_app_extractor.py --frontmost --export

# iTerm2
python iterm2_extractor.py --frontmost --export

# All windows
python terminal_app_extractor.py --capture-all --export
```

**View exports:**
```bash
ls ~/Documents/TerminalExports/$(date +%Y-%m-%d)/
```

### ✅ Auto-Monitoring

Terminal Monitor daemon runs in background and:
- Detects when terminal windows close
- Logs window close events
- Exports session metadata
- Stores in organized directory

### ✅ Health Monitoring

Check system health:
```bash
python health_monitor.py --check
```

Shows:
- Knowledge graph status
- Disk space available
- Export directory size
- LaunchAgent status

---

## File Organization

Exports are organized by date:

```
~/Documents/TerminalExports/
├── 2026-01-02/
│   ├── session-171540-terminal_app-3e85e102.txt
│   ├── session-172335-iterm2-a9f3c7d1.txt
│   └── session-173421-terminal_app-f2d8e9c4.txt
├── 2026-01-03/
│   └── ...
└── 2026-01-04/
    └── ...
```

Each export includes:
- Timestamp
- Terminal type
- Window title
- Session content

---

## Configuration

Edit `~/.metasystem/terminal-export.yaml`:

```yaml
settings:
  enabled: true
  export_directory: ~/Documents/TerminalExports
  max_file_size_mb: 10
  log_to_kg: false  # Set to true to log to knowledge graph
  organize_by_date: true

terminals:
  terminal_app:
    enabled: true
    capture_scrollback: true
  iterm2:
    enabled: true
    capture_scrollback: true

filters:
  exclude_patterns:
    - password
    - secret
    - token
  min_lines: 10
  max_lines: 100000
```

---

## LaunchAgent Management

### Load Agent (Auto-start)

```bash
launchctl load ~/Library/LaunchAgents/com.metasystem.terminal-monitor.plist
```

### Unload Agent (Stop auto-start)

```bash
launchctl unload ~/Library/LaunchAgents/com.metasystem.terminal-monitor.plist
```

### Check Status

```bash
launchctl list | grep com.metasystem
```

### View Logs

```bash
tail -f ~/.metasystem/logs/terminal-monitor.log
tail -f ~/.metasystem/logs/terminal-monitor-error.log
```

---

## Daemon Commands

### Terminal Monitor

```bash
# Check status
python terminal_monitor.py --status

# Start manually
python terminal_monitor.py --start --verbose

# Stop
Ctrl+C
```

### Health Monitor

```bash
# Quick health check
python health_monitor.py --check

# Run as daemon (hourly checks)
python health_monitor.py --daemon --interval 3600
```

### Sorting Daemon (When enabled)

```bash
# Check status
python sorting_daemon.py --status

# Enable auto-start
launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist

# Run manually
python sorting_daemon.py --daemon
```

---

## Troubleshooting

### "Terminal.app export not capturing content"

**Cause**: Accessibility permissions not granted

**Fix**:
1. System Settings → Privacy & Security → Accessibility
2. Click the `+` button
3. Select Terminal.app
4. Restart Terminal.app

### LaunchAgent not auto-starting

**Check if loaded:**
```bash
launchctl list | grep com.metasystem.terminal-monitor
```

**Reload if needed:**
```bash
launchctl unload ~/Library/LaunchAgents/com.metasystem.terminal-monitor.plist
launchctl load ~/Library/LaunchAgents/com.metasystem.terminal-monitor.plist
```

### Disk space warnings

```bash
# Check export directory size
du -sh ~/Documents/TerminalExports/

# Clean old exports (older than 30 days)
find ~/Documents/TerminalExports -name "*.txt" -mtime +30 -delete
```

---

## Integration with Knowledge Graph

To log exports to knowledge graph:

1. Edit `~/.metasystem/terminal-export.yaml`:
   ```yaml
   settings:
     log_to_kg: true
   ```

2. Exports will be logged as entities:
   ```
   type: terminal_session
   name: session-171540-terminal_app-3e85e102.txt
   metadata: {
     terminal_type: terminal_app,
     window_title: Terminal — metasystem-core,
     file_size: 2048
   }
   ```

3. Query in Python:
   ```python
   from knowledge_graph import KnowledgeGraph

   kg = KnowledgeGraph()
   sessions = kg.query_entities(type='terminal_session', limit=10)
   ```

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   macOS System                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  LaunchAgent (com.metasystem.terminal-monitor)     │
│              ↓                                      │
│  Terminal Monitor Daemon (terminal_monitor.py)     │
│         Runs in background                         │
│         Checks every 1 second                       │
│              ↓                                      │
│  Terminal Extractors                               │
│  ├── Terminal.app (AppleScript)                    │
│  └── iTerm2 (AppleScript)                          │
│              ↓                                      │
│  Export Manager (terminal_export_manager.py)       │
│  ├── Save to ~/Documents/TerminalExports/          │
│  ├── Organize by date                              │
│  └── Log to KG (optional)                          │
│              ↓                                      │
│  Knowledge Graph (optional)                        │
│  └── Entity: terminal_session                      │
│                                                     │
│  Other Daemons:                                    │
│  ├── Health Monitor (hourly)                       │
│  └── Sorting Daemon (on demand)                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Security & Privacy

### Exported Data

Terminal exports contain:
- Command history
- Code and configuration
- File paths and names
- Potentially sensitive information

### Recommendations

1. **Store securely**: Use encrypted external drive or iCloud
2. **Filter sensitive data**: Add patterns to `exclude_patterns`
3. **Review regularly**: Check exports for sensitive content
4. **Set file permissions**: `chmod 600` on export files

### Manual Filtering

To redact sensitive content before storing:

```bash
# Find exports containing keyword
grep -r "password\|secret" ~/Documents/TerminalExports/

# Remove sensitive exports
rm ~/Documents/TerminalExports/2026-01-02/session-*.txt
```

---

## Performance Considerations

### Resource Usage

- **CPU**: Minimal (1% when checking)
- **Memory**: ~50MB per daemon
- **Disk**: ~1-10MB per export
- **Check interval**: 1 second (configurable)

### Optimization

To reduce resource usage:

```bash
# Increase check interval (slower detection)
python terminal_monitor.py --start --check-interval 5

# Disable less-used terminals
# Edit ~/.metasystem/terminal-export.yaml
```

---

## Monitoring

### View Real-Time Logs

```bash
# Terminal monitor
tail -f ~/.metasystem/logs/terminal-monitor.log

# All metasystem logs
ls ~/.metasystem/logs/
```

### Check System Status

```bash
# One-line status check
python health_monitor.py --check | grep "Overall Status"

# Full health report
python health_monitor.py --check
```

### Dashboard (Optional Future)

Could add web dashboard to view:
- Recent exports
- System health
- LaunchAgent status
- Statistics and trends

---

## Next Steps (Future Phases)

### Phase 11: Multi-Machine Sync
- Sync exports to iCloud Drive
- Sync to external drives
- Sync knowledge graph

### Phase 12: Advanced Features
- Session replay viewer
- Command extraction and tagging
- Smart filtering with ML
- Session search and discovery

### Phase 13: Insights & Analytics
- Productivity metrics
- Most-used commands
- Session patterns
- Context preservation

---

## Uninstall

To completely remove metasystem:

```bash
# Unload LaunchAgents
launchctl unload ~/Library/LaunchAgents/com.metasystem*.plist

# Remove LaunchAgent files
rm ~/Library/LaunchAgents/com.metasystem*.plist

# Optional: Archive exports
tar -czf ~/Documents/terminal-exports-backup.tar.gz ~/Documents/TerminalExports/

# Remove export directory
rm -rf ~/Documents/TerminalExports/

# Remove logs
rm -rf ~/.metasystem/logs/
```

---

## Support & Issues

### Get Help

```bash
# Show help for each component
./export_terminal.sh --help
python terminal_monitor.py --help
python health_monitor.py --help
python terminal_export_manager.py --help
```

### Report Issues

1. Check logs: `tail ~/.metasystem/logs/*.log`
2. Run health check: `python health_monitor.py --check`
3. Test manually: `python terminal_app_extractor.py --frontmost`

---

## Summary

✅ **Terminal export** - Manual and automatic
✅ **Multi-terminal support** - Terminal.app & iTerm2
✅ **Auto-monitoring** - Runs in background via LaunchAgent
✅ **Health checks** - System health monitoring
✅ **Knowledge graph integration** - Optional logging
✅ **Production ready** - Tested and working

**Status**: Ready for production deployment!

---

*Phase 10 Deployment Guide*
*Created: 2026-01-02*
*Last Updated: 2026-01-02*
