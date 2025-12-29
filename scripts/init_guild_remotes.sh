#!/bin/bash
# Run this AFTER creating 'labores-profani-crux' organization on GitHub

ORG="labores-profani-crux"
GUILD_DIR="$HOME/Workspace/labores-profani-crux"

echo "🏛️  Initializing Guild Remotes for $ORG..."

# 1. Trade Perpetual
cd "$GUILD_DIR/trade-perpetual-future"
gh repo create "$ORG/trade-perpetual-future" --private --source=. --remote=origin --push || echo "⚠️ Failed to create trade-perpetual"

# 2. Gamified Coach
cd "$GUILD_DIR/gamified-coach-interface"
gh repo create "$ORG/gamified-coach-interface" --private --source=. --remote=origin --push || echo "⚠️ Failed to create gamified-coach"

# 3. Enterprise Plugin
cd "$GUILD_DIR/enterprise-plugin"
gh repo create "$ORG/enterprise-plugin" --private --source=. --remote=origin --push || echo "⚠️ Failed to create enterprise-plugin"

echo "✅ Guild Initialization Attempt Complete."
