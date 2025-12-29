#!/usr/bin/env python3
import subprocess
from pathlib import Path

GUILD_DIR = Path("/Users/4jp/Workspace/labores-profani-crux")
TARGETS = ["trade-perpetual-future", "gamified-coach-interface", "enterprise-plugin"]

def run_git(cmd, cwd):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Git Error in {cwd.name}: {e.stderr.strip()}")
        return False

def enable_actions():
    print("🎬 Enabling GitHub Actions (Committing Workflows)...")
    
    for target in TARGETS:
        repo_path = GUILD_DIR / target
        if not repo_path.exists():
            continue
            
        print(f"   🔧 Processing {target}...")
        
        # 1. Add the workflow file
        if run_git("git add .github/workflows/profane-standards.yml", repo_path):
            # 2. Check if there are changes to commit
            # We also commit seed.yaml if modified (inoculation)
            run_git("git add seed.yaml", repo_path)
            
            # 3. Commit
            if run_git('git commit -m "ci(guild): enable profane standards workflow"', repo_path):
                print(f"      ✅ Committed workflow.")
            else:
                print(f"      ℹ️  Nothing to commit (or commit failed).")
        
        # Note: We cannot push yet because the remote 'labores-profani-crux' doesn't exist.
        # But the code is now "Enabled" locally.

if __name__ == "__main__":
    enable_actions()
