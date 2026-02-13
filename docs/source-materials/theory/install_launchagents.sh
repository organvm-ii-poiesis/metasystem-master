#!/bin/bash
# Install LaunchAgent configurations for metasystem services
# Usage: ./install_launchagents.sh

set -e

METASYSTEM_DIR="$HOME/Workspace/metasystem-core"
VENV_PYTHON="$METASYSTEM_DIR/.venv/bin/python3"
LAUNCHAGENTS_DIR="$HOME/Library/LaunchAgents"

echo "📦 Installing metasystem LaunchAgents..."
echo ""

# Ensure LaunchAgents directory exists
mkdir -p "$LAUNCHAGENTS_DIR"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 0. Meta-Orchestrator (PRIMARY COORDINATOR)
echo -e "${BLUE}Installing meta-orchestrator LaunchAgent (primary)...${NC}"

cat > "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metasystem.meta-orchestrator</string>
    <key>ProgramArguments</key>
    <array>
        <string>VENV_PYTHON_PLACEHOLDER</string>
        <string>METASYSTEM_DIR_PLACEHOLDER/meta_orchestrator.py</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/meta-orchestrator.log</string>
    <key>StandardErrorPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/meta-orchestrator-error.log</string>
</dict>
</plist>
EOF

sed -i '' "s|VENV_PYTHON_PLACEHOLDER|$VENV_PYTHON|g" "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist"
sed -i '' "s|METASYSTEM_DIR_PLACEHOLDER|$METASYSTEM_DIR|g" "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist"
sed -i '' "s|HOME_PLACEHOLDER|$HOME|g" "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist"

chmod 644 "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist"
echo -e "${GREEN}✅ Installed: com.metasystem.meta-orchestrator (PRIMARY)${NC}"

# 1. Terminal Monitor Agent
echo -e "${BLUE}Installing terminal-monitor LaunchAgent...${NC}"

cat > "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metasystem.terminal-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>VENV_PYTHON_PLACEHOLDER</string>
        <string>METASYSTEM_DIR_PLACEHOLDER/terminal_monitor.py</string>
        <string>--start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/terminal-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/terminal-monitor-error.log</string>
</dict>
</plist>
EOF

# Replace placeholders
sed -i '' "s|VENV_PYTHON_PLACEHOLDER|$VENV_PYTHON|g" "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist"
sed -i '' "s|METASYSTEM_DIR_PLACEHOLDER|$METASYSTEM_DIR|g" "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist"
sed -i '' "s|HOME_PLACEHOLDER|$HOME|g" "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist"

chmod 644 "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist"
echo -e "${GREEN}✅ Installed: com.metasystem.terminal-monitor${NC}"

# 2. File Organization Daemon (placeholder for sorting_daemon)
echo ""
echo -e "${BLUE}Installing sorting-daemon LaunchAgent...${NC}"

cat > "$LAUNCHAGENTS_DIR/com.metasystem.sorting-daemon.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metasystem.sorting-daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>VENV_PYTHON_PLACEHOLDER</string>
        <string>METASYSTEM_DIR_PLACEHOLDER/sorting_daemon.py</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/sorting-daemon.log</string>
    <key>StandardErrorPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/sorting-daemon-error.log</string>
</dict>
</plist>
EOF

sed -i '' "s|VENV_PYTHON_PLACEHOLDER|$VENV_PYTHON|g" "$LAUNCHAGENTS_DIR/com.metasystem.sorting-daemon.plist"
sed -i '' "s|METASYSTEM_DIR_PLACEHOLDER|$METASYSTEM_DIR|g" "$LAUNCHAGENTS_DIR/com.metasystem.sorting-daemon.plist"
sed -i '' "s|HOME_PLACEHOLDER|$HOME|g" "$LAUNCHAGENTS_DIR/com.metasystem.sorting-daemon.plist"

chmod 644 "$LAUNCHAGENTS_DIR/com.metasystem.sorting-daemon.plist"
echo -e "${GREEN}✅ Installed: com.metasystem.sorting-daemon${NC}"

# 3. Health Monitor (placeholder for future)
echo ""
echo -e "${BLUE}Installing health-monitor LaunchAgent...${NC}"

cat > "$LAUNCHAGENTS_DIR/com.metasystem.health-monitor.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.metasystem.health-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>VENV_PYTHON_PLACEHOLDER</string>
        <string>METASYSTEM_DIR_PLACEHOLDER/health_monitor.py</string>
        <string>--daemon</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>KeepAlive</key>
    <false/>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/health-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>HOME_PLACEHOLDER/.metasystem/logs/health-monitor-error.log</string>
</dict>
</plist>
EOF

sed -i '' "s|VENV_PYTHON_PLACEHOLDER|$VENV_PYTHON|g" "$LAUNCHAGENTS_DIR/com.metasystem.health-monitor.plist"
sed -i '' "s|METASYSTEM_DIR_PLACEHOLDER|$METASYSTEM_DIR|g" "$LAUNCHAGENTS_DIR/com.metasystem.health-monitor.plist"
sed -i '' "s|HOME_PLACEHOLDER|$HOME|g" "$LAUNCHAGENTS_DIR/com.metasystem.health-monitor.plist"

chmod 644 "$LAUNCHAGENTS_DIR/com.metasystem.health-monitor.plist"
echo -e "${GREEN}✅ Installed: com.metasystem.health-monitor${NC}"

# Load agents
echo ""
echo -e "${BLUE}Loading LaunchAgents...${NC}"

# Load meta-orchestrator first (it coordinates everything)
launchctl load "$LAUNCHAGENTS_DIR/com.metasystem.meta-orchestrator.plist" 2>/dev/null || true
echo -e "${GREEN}✅ Loaded: meta-orchestrator (PRIMARY COORDINATOR)${NC}"

# Load terminal monitor (enabled by default)
launchctl load "$LAUNCHAGENTS_DIR/com.metasystem.terminal-monitor.plist" 2>/dev/null || true
echo -e "${GREEN}✅ Loaded: terminal-monitor${NC}"

# Don't auto-load sorting-daemon and health-monitor yet
echo "⏸️  Deferred: sorting-daemon (disabled, use 'launchctl load' to enable)"
echo "⏸️  Deferred: health-monitor (disabled, use 'launchctl load' to enable)"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ LaunchAgent installation complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📋 Installed agents:"
echo "   • com.metasystem.meta-orchestrator (ENABLED - PRIMARY COORDINATOR)"
echo "   • com.metasystem.terminal-monitor (ENABLED)"
echo "   • com.metasystem.sorting-daemon (disabled)"
echo "   • com.metasystem.health-monitor (disabled)"
echo ""
echo "🔧 Commands:"
echo "   Load:    launchctl load ~/Library/LaunchAgents/com.metasystem.<agent>.plist"
echo "   Unload:  launchctl unload ~/Library/LaunchAgents/com.metasystem.<agent>.plist"
echo "   Status:  launchctl list | grep com.metasystem"
echo "   Logs:    tail -f ~/.metasystem/logs/<agent>.log"
echo ""
echo "ℹ️  Terminal monitor is now running in the background!"
echo "   It will auto-export terminal sessions when they close."
echo ""
