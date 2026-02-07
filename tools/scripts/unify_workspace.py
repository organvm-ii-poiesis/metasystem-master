#!/usr/bin/env python3
import os
import shutil
import subprocess
import json
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORGS = ["4444JPP", "ivviiviivvi", "omni-dromenon-machina"]

# Map of specific repos that might need manual overrides if their remote is ambiguous
# (Currently relying on 'git remote get-url origin')

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_repo_org(path):
    """Determines the org of a repo based on its remote URL."""
    remote_url = run_command("git remote get-url origin", cwd=path)
    if not remote_url:
        return None
    
    # Parse https://github.com/ORG/REPO.git or git@github.com:ORG/REPO.git
    parts = remote_url.replace(":", "/").split("/")
    if "github.com" in parts:
        idx = parts.index("github.com")
        if len(parts) > idx + 1:
            return parts[idx + 1]
    return None

def organize_workspace():
    print("🏗️  Organizing Workspace Structure...")
    
    # 1. Create Org Directories
    for org in ORGS:
        org_path = WORKSPACE_ROOT / org
        org_path.mkdir(exist_ok=True)
        print(f"   - Ensured directory: {org_path}")

    # 2. Scan and Move
    for item in os.listdir(WORKSPACE_ROOT):
        item_path = WORKSPACE_ROOT / item
        
        # Skip if it's not a directory or if it IS one of the org directories
        if not item_path.is_dir() or item in ORGS:
            continue
            
        # Check if it's a git repo
        if (item_path / ".git").exists():
            org = get_repo_org(item_path)
            
            if org and org in ORGS:
                dest_path = WORKSPACE_ROOT / org / item
                
                # Safety check: Don't move if destination exists
                if dest_path.exists():
                    print(f"   ⚠️  Skipping {item}: Destination {dest_path} already exists.")
                    continue
                
                print(f"   🚚 Moving {item} -> {org}/{item}...")
                try:
                    shutil.move(str(item_path), str(dest_path))
                except Exception as e:
                    print(f"   ❌ Failed to move {item}: {e}")
            else:
                print(f"   ❓ Unknown Org for {item} (Remote: {org}). Leaving in root.")

if __name__ == "__main__":
    organize_workspace()
