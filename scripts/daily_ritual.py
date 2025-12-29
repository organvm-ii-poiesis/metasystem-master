#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path
import datetime

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
METASYSTEM_ROOT = WORKSPACE_ROOT / "omni-dromenon-machina"
LOG_FILE = METASYSTEM_ROOT / "plans/RITUAL_LOG.md"

def run_script(script_name):
    script_path = METASYSTEM_ROOT / "scripts" / script_name
    print(f"\n🔮 Invoking {script_name}...")
    try:
        subprocess.run(["python3", str(script_path)], check=True)
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def daily_ritual():
    print(f"\n☀️  THE DAILY RITUAL: {datetime.date.today()}")
    print("=========================================")
    
    # 1. Self-Update (Update the Ritual itself)
    print("1️⃣  Updating Metasystem Master...")
    subprocess.run(["git", "pull"], cwd=METASYSTEM_ROOT)
    
    # 2. Sync Reality (Pull everything)
    # We need a 'sync_all.py' - for now we use 'sync_universe.py' if it exists, or robust_restore.
    # Let's assume sync_universe.py handles pulls.
    run_script("sync_universe.py") 
    
    # 3. Heal Identity (Inoculate)
    run_script("inoculate_seeds.py")
    
    # 4. Remember (Index)
    run_script("index_universe.py")
    
    # 5. Audit (Check Health)
    run_script("audit_universe.py")
    
    print("\n✅ Ritual Complete. The System is aligned.")
    
    # Log it
    with open(LOG_FILE, "a") as f:
        f.write(f"\n- **{datetime.date.today()}:** Ritual Performed. System Aligned.")

if __name__ == "__main__":
    daily_ritual()
