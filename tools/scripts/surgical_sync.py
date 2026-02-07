#!/usr/bin/env python3
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/4jp/Workspace")

TARGETS = [
    "ivviiviivvi/trade-perpetual-future",
    "ivviiviivvi/gamified-coach-interface"
]

def run_command(cmd, cwd):
    print(f"   > {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        print("     ❌ Command failed.")
        return False

def surgical_sync(rel_path):
    path = WORKSPACE_ROOT / rel_path
    print(f"\n🚑 Surgical Sync for {path.name}...")
    
    # 1. Pull Rebase
    if run_command("git pull --rebase origin main", path):
        print("   ✅ Rebase successful.")
        # 2. Push
        if run_command("git push origin main", path):
            print("   ✅ Pushed successfully.")
        else:
            print("   ❌ Push failed after rebase.")
    else:
        print("   ❌ Rebase failed (Merge Conflict?).")

if __name__ == "__main__":
    for target in TARGETS:
        surgical_sync(target)
