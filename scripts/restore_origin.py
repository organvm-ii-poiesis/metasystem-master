#!/usr/bin/env python3
import os
import subprocess
import json
import yaml
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORIGIN_ORG = "4444JPP"
ORIGIN_DIR = WORKSPACE_ROOT / ORIGIN_ORG

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}\n{e.stderr}")
        return None

def detect_tech_stack(path):
    stack = []
    if (path / "package.json").exists(): stack.append("node")
    if (path / "requirements.txt").exists(): stack.append("python")
    return stack

def inoculate(repo_name, path):
    if (path / "seed.yaml").exists(): return
    
    print(f"   🌱 Seeding {repo_name}...")
    stack = detect_tech_stack(path)
    
    seed = {
        "version": 1,
        "project": {
            "name": repo_name,
            "description": "Restored from The Origin.",
            "owners": [{"handle": ORIGIN_ORG, "role": "archivist"}],
            "repo": {
                "org": ORIGIN_ORG,
                "role": "archive/origin",
                "type": stack[0] if stack else "generic"
            }
        },
        "status": "archived" 
    }
    
    with open(path / "seed.yaml", "w") as f:
        yaml.dump(seed, f, sort_keys=False)

def restore_origin():
    print(f"🏛️  Restoring The Origin ({ORIGIN_ORG})...")
    ORIGIN_DIR.mkdir(exist_ok=True)

    # 1. Fetch List
    print("   🔭 Scanning GitHub...")
    cmd = f"gh repo list {ORIGIN_ORG} --limit 200 --json name,sshUrl,nameWithOwner"
    output = run_command(cmd)
    
    if not output:
        print("   ❌ Failed to fetch repo list.")
        return

    repos = json.loads(output)
    print(f"   ✅ Found {len(repos)} artifacts.")

    # 2. Clone & Seed
    success_count = 0
    for r in repos:
        name = r['name']
        clone_url = r['sshUrl'] 
        full_name = r['nameWithOwner']
        
        target_path = ORIGIN_DIR / name
        
        if target_path.exists():
            print(f"   ⚠️  Skipping {name} (Exists).")
            # Inoculate even if exists
            inoculate(name, target_path)
            continue
            
        print(f"   📥 Cloning {name}...")
        res = run_command(f"gh repo clone {full_name} {target_path}")
        
        if res is not None:
            inoculate(name, target_path)
            success_count += 1
        else:
            print(f"   ❌ Failed to clone {name}")

    print(f"\n✅ Restoration Complete. {success_count} new artifacts secured in The Origin.")

if __name__ == "__main__":
    restore_origin()
