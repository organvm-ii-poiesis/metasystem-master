#!/usr/bin/env python3
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/4jp/Workspace")

# Explicit list of repos to sync
TARGETS = [
    "ivviiviivvi/trade-perpetual-future",
    "ivviiviivvi/gamified-coach-interface",
    "ivviiviivvi/input-keys-log",
    "omni-dromenon-machina/omni-dromenon-machina/core-engine",
    "omni-dromenon-machina/omni-dromenon-machina/docs",
    "omni-dromenon-machina/omni-dromenon-machina/academic-publication",
    "omni-dromenon-machina/omni-dromenon-machina/client-sdk",
    "omni-dromenon-machina/omni-dromenon-machina/performance-sdk",
    "omni-dromenon-machina/omni-dromenon-machina/artist-toolkit-and-templates"
]

def run_command(cmd, cwd):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False

def sync_target(rel_path):
    path = WORKSPACE_ROOT / rel_path
    if not path.exists():
        print(f"❌ Path not found: {path}")
        return

    print(f"\n🚀 Syncing {path.name}...")
    
    # 1. Add
    run_command("git add .", path)
    
    # 2. Commit
    if run_command('git commit -m "chore: metasystem sync (teleological audit)"', path):
        print("   ✅ Committed.")
    else:
        print("   ⚠️  Nothing to commit?")

    # 3. Push
    # Try main, then master
    if run_command("git push origin main", path):
        print("   ✅ Pushed to main.")
    elif run_command("git push origin master", path):
        print("   ✅ Pushed to master.")
    else:
        print("   ❌ Push failed.")

if __name__ == "__main__":
    print("⚔️  Mass Commit & Push Protocol Initiated...")
    for target in TARGETS:
        sync_target(target)
