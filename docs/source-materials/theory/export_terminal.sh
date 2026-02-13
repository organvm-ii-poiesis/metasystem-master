#!/bin/bash
# Quick script to export current terminal window content
# Usage: ./export_terminal.sh

cd "$(dirname "$0")"
source .venv/bin/activate

echo "📸 Exporting current terminal window..."
python terminal_app_extractor.py --frontmost --export

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Terminal session exported successfully!"
    echo "📁 Check: ~/Documents/TerminalExports/"
else
    echo ""
    echo "ℹ️  Note: If capture failed, Terminal.app may need accessibility permissions"
    echo "   Go to: System Settings → Privacy & Security → Accessibility"
    echo "   Grant permission to Terminal.app"
fi
