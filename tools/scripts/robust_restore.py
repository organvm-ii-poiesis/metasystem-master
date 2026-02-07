#!/usr/bin/env python3
import subprocess
import json
import yaml
import time
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORIGIN_ORG = "4444JPP"
ORIGIN_DIR = WORKSPACE_ROOT / ORIGIN_ORG
LOG_FILE = WORKSPACE_ROOT / "omni-dromenon-machina/plans/ORIGIN_RESTORATION_LOG.md"

# Repos to try LAST (Heavyweights)
DEFERRED_REPOS = ["docs", "adaptiveDEVlearningHub", "cookbook", "OpenMetadata", "pokerogue"]

def run_command(cmd, cwd=None, timeout=300):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"   ⏳ TIMEOUT: Command took longer than {timeout}s")
        return None
    except subprocess.CalledProcessError as e:
        print(f"   ❌ ERROR: {e.stderr.strip()}")
        return None

def detect_tech_stack(path):
    stack = []
    if (path / "package.json").exists(): stack.append("node")
    if (path / "requirements.txt").exists(): stack.append("python")
    return stack

def inoculate(repo_name, path):
    seed_path = path / "seed.yaml"
    if seed_path.exists(): 
        return True
    
    # print(f"   🌱 Seeding {repo_name}...")
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
    
    try:
        with open(seed_path, "w") as f:
            yaml.dump(seed, f, sort_keys=False)
        return True
    except Exception as e:
        print(f"   ❌ Seed Failed: {e}")
        return False

def robust_restore():
    print(f"🏛️  Robust Restoration: {ORIGIN_ORG}")
    ORIGIN_DIR.mkdir(exist_ok=True)

    # 1. Fetch List
    print("   🔭 Fetching Inventory...")
    # Corrected JSON fields: name, sshUrl, nameWithOwner
    cmd = f"gh repo list {ORIGIN_ORG} --limit 200 --json name,sshUrl,nameWithOwner"
    output = run_command(cmd)
    
    if not output:
        return

    repos = json.loads(output)
    total = len(repos)
    print(f"   ✅ Inventory: {total} artifacts found.")

    # 2. Sort execution order
    standard_ops = [r for r in repos if r['name'] not in DEFERRED_REPOS]
    deferred_ops = [r for r in repos if r['name'] in DEFERRED_REPOS]
    
    final_list = standard_ops + deferred_ops
    
    # 3. Execute
    success_count = 0
    fail_count = 0
    skipped_count = 0

    log_entries = []

    for i, r in enumerate(final_list):
        name = r['name']
        full_name = r['nameWithOwner']
        target_path = ORIGIN_DIR / name
        
        print(f"[{i+1}/{total}] {name}...", end=" ", flush=True)

        status = "UNKNOWN"
        note = ""

        if target_path.exists():
            print("✅ (Exists)")
            status = "RESTORED"
            note = "Previously cloned"
            skipped_count += 1
            inoculate(name, target_path)
        else:
            # Clone
            res = run_command(f"gh repo clone {full_name} {target_path}", timeout=300) # 5 min limit
            if res is not None:
                print("✅ Cloned")
                status = "RESTORED"
                inoculate(name, target_path)
                success_count += 1
            else:
                print("❌ Failed")
                status = "FAILED"
                note = "Clone Error or Timeout"
                fail_count += 1

        log_entries.append(f"| `{name}` | {status} | {note} |")
        time.sleep(1) # Breath

    # 4. Write Log
    print(f"\n📝 Updating Log: {LOG_FILE}")
    header = "# 📜 Origin Restoration Log\n\n| Repository | Status | Notes |\n| :--- | :--- | :--- |\n"
    content = header + "\n".join(log_entries)
    
    with open(LOG_FILE, "w") as f:
        f.write(content)

    print(f"\n🏁 Mission Report:")
    print(f"   - Total: {total}")
    print(f"   - Restored: {success_count}")
    print(f"   - Skipped (Existing): {skipped_count}")
    print(f"   - Failed: {fail_count}")

if __name__ == "__main__":
    robust_restore()
