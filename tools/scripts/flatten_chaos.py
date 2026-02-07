#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

ROOT = Path(".")
NESTED = ROOT / "omni-dromenon-machina"

def flatten():
    if not NESTED.exists():
        print("❌ Nested folder 'omni-dromenon-machina' not found!")
        return

    print(f"🚜 Flattening {NESTED} into {ROOT}...")

    for item in os.listdir(NESTED):
        src = NESTED / item
        dest = ROOT / item
        
        if dest.exists():
            print(f"   ⚠️  Conflict: {item}")
            if item == "scripts":
                print(f"      ↳ Merging scripts...")
                for script in os.listdir(src):
                    shutil.move(str(src / script), str(dest / script))
            else:
                print(f"      ↳ Skipping {item} (already exists in root).")
        else:
            print(f"   🚚 Moving {item}...")
            shutil.move(str(src), str(dest))

    print("✅ Flattening complete. Check for empty folder.")
    try:
        NESTED.rmdir()
        print("🗑️  Removed empty nested folder.")
    except:
        print("ℹ️  Nested folder not empty (conflicts left).")

if __name__ == "__main__":
    flatten()
