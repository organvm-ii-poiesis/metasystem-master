#!/bin/bash
# Fallback: Create under personal account 4444JPP
ORG="4444JPP"
GUILD_DIR="$HOME/Workspace/labores-profani-crux"

echo "🏛️  Initializing Guild Repositories for $ORG..."

# 1. Trade Perpetual
cd "$GUILD_DIR/trade-perpetual-future"
# Check if repo exists first to avoid error
gh repo view "$ORG/trade-perpetual-future" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  gh repo create "$ORG/trade-perpetual-future" --private --source=. --remote=origin --push
else
  echo "⚠️  Repo trade-perpetual-future already exists"
  git push -u origin main
fi

# 2. Gamified Coach
cd "$GUILD_DIR/gamified-coach-interface"
gh repo view "$ORG/gamified-coach-interface" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  gh repo create "$ORG/gamified-coach-interface" --private --source=. --remote=origin --push
else
  echo "⚠️  Repo gamified-coach-interface already exists"
  git push -u origin main
fi

# 3. Enterprise Plugin
cd "$GUILD_DIR/enterprise-plugin"
gh repo view "$ORG/enterprise-plugin" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  gh repo create "$ORG/enterprise-plugin" --private --source=. --remote=origin --push
else
  echo "⚠️  Repo enterprise-plugin already exists"
  git push -u origin main
fi

echo "✅ Guild Assets Deployed to $ORG."
