#!/usr/bin/env python3
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
GUILD_DIR = WORKSPACE_ROOT / "Labores-Profanus-Crux"
MYTHOS_DIR = WORKSPACE_ROOT / "ivviiviivvi"

MOVES = [
    (MYTHOS_DIR / "trade-perpetual-future", GUILD_DIR / "trade-perpetual-future"),
    (MYTHOS_DIR / "gamified-coach-interface", GUILD_DIR / "gamified-coach-interface"),
    (WORKSPACE_ROOT / "enterprise-plugin", GUILD_DIR / "enterprise-plugin")
]

def migrate():
    print(f"🏗️  Migrating Assets to {GUILD_DIR.name}...")
    GUILD_DIR.mkdir(exist_ok=True)
    
    for src, dest in MOVES:
        if src.exists():
            print(f"   🚚 Moving {src.name}...")
            try:
                shutil.move(str(src), str(dest))
                print("      ✅ Done.")
            except Exception as e:
                print(f"      ❌ Failed: {e}")
        else:
            print(f"   ⚠️  Source not found: {src}")

if __name__ == "__main__":
    migrate()
