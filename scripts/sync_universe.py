#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORGS = ["4444JPP", "ivviiviivvi", "omni-dromenon-machina"]

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def get_remote_repos():
    print("🔭 Fetching Remote Repository List...")
    remote_repos = {}
    for org in ORGS:
        # Correct field is 'nameWithOwner' not 'full_name'
        cmd = f"gh repo list {org} --limit 200 --json name,nameWithOwner,url,sshUrl,defaultBranchRef"
        output = run_command(cmd)
        if output:
            repos = json.loads(output)
            for r in repos:
                # defaultBranchRef is an object { "name": "main" }
                branch = r.get('defaultBranchRef', {}).get('name', 'main') if r.get('defaultBranchRef') else 'main'
                r['defaultBranch'] = branch
                r['full_name'] = r['nameWithOwner'] # Polyfill for compatibility
                remote_repos[r['name']] = r
    return remote_repos

def sync_repo(name, path, remote_data):
    print(f"\n🔄 Syncing {name} ({path})...")
    
    # 1. Check for Uncommitted Changes
    status = run_command("git status --porcelain", cwd=path)
    if status:
        print(f"   ⚠️  DIRTY: Uncommitted changes detected.")
        print(f"   ❌ SKIPPING pull to protect local work. Please commit or stash manually.")
        return "dirty"

    # 2. Fetch
    print(f"   ⬇️  Fetching origin...")
    run_command("git fetch origin", cwd=path)

    # 3. Check Divergence
    default_branch = remote_data.get('defaultBranch', 'main')
    # Try to detect if local uses 'master' instead
    local_branches = run_command("git branch", cwd=path)
    if 'master' in local_branches and 'main' not in local_branches:
        target_branch = 'master'
    else:
        target_branch = default_branch

    # Count commits
    rev_list = run_command(f"git rev-list --left-right --count HEAD...origin/{target_branch}", cwd=path)
    
    if not rev_list:
        print("   ⚠️  Could not compare branches. Maybe new repo?")
        return "error"

    ahead, behind = map(int, rev_list.split())

    if ahead == 0 and behind == 0:
        print("   ✅ Synced.")
        return "synced"
    
    if behind > 0:
        print(f"   ⬇️  Behind by {behind} commits. Pulling...")
        res = run_command(f"git pull --rebase origin {target_branch}", cwd=path)
        if res is not None:
            print("   ✅ Pulled successfully.")
        else:
            print("   ❌ Pull failed (conflict?).")
            return "conflict"
            
    if ahead > 0:
        print(f"   ⬆️  Ahead by {ahead} commits. Pushing...")
        # Since GH is master, we assume we want to push our work to it
        res = run_command(f"git push origin {target_branch}", cwd=path)
        if res is not None:
            print("   ✅ Pushed successfully.")
        else:
            print("   ❌ Push failed.")
            return "push_failed"

    return "updated"

def clone_missing(remote_repos, local_repos):
    print("\n☁️  Checking for Missing Repositories...")
    # Create org folders if they don't exist
    for org in ORGS:
        (WORKSPACE_ROOT / org).mkdir(exist_ok=True)

    for name, data in remote_repos.items():
        if name not in local_repos:
            org = data['full_name'].split('/')[0]
            target_path = WORKSPACE_ROOT / org / name
            print(f"   📥 Cloning {data['full_name']} to {target_path}...")
            res = run_command(f"gh repo clone {data['full_name']} {target_path}")
            if res is not None:
                print("   ✅ Cloned.")
            else:
                print("   ❌ Clone failed.")

def main():
    remote_repos = get_remote_repos()
    
    # Scan Local
    print("🌍 Scanning Local Workspace...")
    local_repos = {}
    
    # 1. Scan Root (for legacy/unmoved)
    for item in os.listdir(WORKSPACE_ROOT):
        path = WORKSPACE_ROOT / item
        if path.is_dir() and (path / ".git").exists():
            local_repos[item] = str(path)

    # 2. Scan Org Directories
    for org in ORGS:
        org_path = WORKSPACE_ROOT / org
        if org_path.exists():
            for item in os.listdir(org_path):
                path = org_path / item
                if path.is_dir() and (path / ".git").exists():
                    local_repos[item] = str(path)

    # Sync Existing
    for name, path in local_repos.items():
        if name in remote_repos:
            sync_repo(name, path, remote_repos[name])
        else:
            print(f"\n👻 Orphan: {name} (No matching remote in targeted orgs)")

    # Clone Missing
    # Uncomment to enable auto-cloning of all 115 repos (WARNING: High Bandwidth)
    # clone_missing(remote_repos, local_repos)

if __name__ == "__main__":
    main()
