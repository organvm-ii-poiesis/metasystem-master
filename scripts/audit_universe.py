#!/usr/bin/env python3
import os
import subprocess
import json
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORGS = ["4444JPP", "ivviiviivvi", "omni-dromenon-machina"]
OUTPUT_FILE = WORKSPACE_ROOT / "UNIVERSE_STATUS.md"

def run_command(cmd):
    """Runs a shell command and returns stdout."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def get_remote_repos():
    """Fetches all repos from GitHub for the defined orgs."""
    print("🔭 Scanning the Heavens (Fetching GitHub Repos)...")
    remote_repos = {}
    
    for org in ORGS:
        print(f"   - Scanning {org}...")
        # Fetch up to 200 repos per org to be safe
        cmd = f"gh repo list {org} --limit 200 --json name,full_name,sshUrl,defaultBranch"
        output = run_command(cmd)
        if output:
            repos = json.loads(output)
            for r in repos:
                remote_repos[r['name']] = r
    
    print(f"✅ Found {len(remote_repos)} remote repositories.")
    return remote_repos

def get_local_repos():
    """Scans the local workspace for git repositories."""
    print("🌍 Scanning the Earth (Walking Workspace)...")
    local_repos = {}
    
    # Walk only 2 levels deep to avoid scanning inside node_modules
    for root, dirs, files in os.walk(WORKSPACE_ROOT):
        # Skip hidden folders (except .git)
        dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.git']
        
        if ".git" in dirs:
            path = Path(root)
            repo_name = path.name
            
            # Get remote URL to confirm identity
            remote_url = run_command(f"git -C '{path}' remote get-url origin")
            
            # Get git status
            status_short = run_command(f"git -C '{path}' status --porcelain")
            is_dirty = bool(status_short)
            
            # Check ahead/behind
            commits = run_command(f"git -C '{path}' rev-list --left-right --count HEAD...origin/main 2>/dev/null || git -C '{path}' rev-list --left-right --count HEAD...origin/master 2>/dev/null")
            ahead, behind = (0, 0)
            if commits:
                parts = commits.split()
                if len(parts) == 2:
                    ahead, behind = map(int, parts)
            
            local_repos[repo_name] = {
                "path": str(path),
                "remote_url": remote_url,
                "is_dirty": is_dirty,
                "ahead": ahead,
                "behind": behind
            }
            # Don't recurse into a repo
            dirs[:] = []
            
    print(f"✅ Found {len(local_repos)} local repositories.")
    return local_repos

def generate_report(remote, local):
    """Generates a Markdown report of the delta."""
    print("⚡ Calculating Delta (The Stride)...")
    
    with open(OUTPUT_FILE, "w") as f:
        f.write(f"# 🌌 UNIVERSE STATUS REPORT\n")
        f.write(f"**Generated:** {run_command('date')}\n\n")
        
        # 1. DRIFTED (Exist locally, but out of sync)
        f.write("## ⚠️ DRIFTED (Local needs Sync)\n")
        f.write("| Repo | Status | Path |\n")
        f.write("|---|---|---|")
        
        drift_count = 0
        for name, l_data in local.items():
            if name in remote:
                status = []
                if l_data['is_dirty']: status.append("Dirty 📝")
                if l_data['ahead'] > 0: status.append(f"Ahead {l_data['ahead']} ⬆️")
                if l_data['behind'] > 0: status.append(f"Behind {l_data['behind']} ⬇️")
                
                if status:
                    drift_count += 1
                    f.write(f"| **{name}** | {', '.join(status)} | `{l_data['path']}` |\n")
        
        if drift_count == 0: f.write("| None | All synced | - |\n")
        f.write("\n")

        # 2. MISSING (Remote exists, Local does not)
        f.write("## ☁️ MISSING LOCALLY (Need Clone)\n")
        f.write("| Repo | Org | Clone Command |\n")
        f.write("|---|---|---|")
        
        missing_count = 0
        for name, r_data in remote.items():
            if name not in local:
                missing_count += 1
                f.write(f"| {name} | {r_data['full_name'].split('/')[0]} | `gh repo clone {r_data['full_name']}` |\n")
        
        if missing_count == 0: f.write("| None | All cloned | - |\n")
        f.write("\n")

        # 3. ORPHANS (Local exists, Remote does not match known orgs)
        f.write("## 👻 ORPHANS (Local only / Unknown Remote)\n")
        f.write("| Repo | Local Path | Remote URL |\n")
        f.write("|---|---|---|")
        
        orphan_count = 0
        for name, l_data in local.items():
            if name not in remote:
                orphan_count += 1
                remote_str = l_data['remote_url'] if l_data['remote_url'] else "No Remote"
                f.write(f"| {name} | `{l_data['path']}` | {remote_str} |\n")
                
        if orphan_count == 0: f.write("| None | - | - |\n")
        f.write("\n")

    print(f"📜 Report generated at: {OUTPUT_FILE}")
    print(f"   - Drifted: {drift_count}")
    print(f"   - Missing: {missing_count}")
    print(f"   - Orphans: {orphan_count}")

if __name__ == "__main__":
    remote_data = get_remote_repos()
    local_data = get_local_repos()
    generate_report(remote_data, local_data)
