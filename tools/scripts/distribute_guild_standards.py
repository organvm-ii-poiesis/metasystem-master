#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
GUILD_DIR = WORKSPACE_ROOT / "labores-profani-crux"
TEMPLATE_PATH = WORKSPACE_ROOT / "omni-dromenon-machina/artist-toolkit-and-templates/templates/profane-standards.yml"

TARGETS = [
    "trade-perpetual-future",
    "gamified-coach-interface",
    "enterprise-plugin"
]

def distribute():
    print("🛡️  Distributing Profane Standards...")
    
    if not TEMPLATE_PATH.exists():
        print(f"❌ Template not found: {TEMPLATE_PATH}")
        return

    for target in TARGETS:
        repo_path = GUILD_DIR / target
        if not repo_path.exists():
            print(f"⚠️  Skipping {target} (Not found)")
            continue
            
        workflow_dir = repo_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        dest = workflow_dir / "profane-standards.yml"
        shutil.copy(TEMPLATE_PATH, dest)
        print(f"✅ Secured {target}")

if __name__ == "__main__":
    distribute()
