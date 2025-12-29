#!/usr/bin/env python3
import os
import json
from pathlib import Path

WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORGS = ["4444JPP", "ivviiviivvi", "omni-dromenon-machina", "labores-profani-crux"]
INDEX_FILE = WORKSPACE_ROOT / "omni-dromenon-machina/data/universe_index.json"

def index_universe():
    print("🧠 The Architect: Indexing the Universe...")
    index = []

    for org in ORGS:
        org_path = WORKSPACE_ROOT / org
        if not org_path.exists(): continue
        
        print(f"   🔭 Scanning {org}...")
        for item in os.listdir(org_path):
            repo_path = org_path / item
            if not repo_path.is_dir(): continue
            
            # Simple metadata indexing
            meta = {
                "repo": f"{org}/{item}",
                "org": org,
                "name": item,
                "files": []
            }
            
            # Extract content from README and seed
            for target in ["README.md", "seed.yaml"]:
                tp = repo_path / target
                if tp.exists():
                    try:
                        with open(tp, 'r') as f:
                            meta["files"].append({
                                "name": target,
                                "content": f.read()[:2000] # Cap for now
                            })
                    except: pass
            
            index.append(meta)

    # Ensure data dir exists
    INDEX_FILE.parent.mkdir(exist_ok=True)
    
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Index Complete. {len(index)} repositories mapped to Deep Memory.")

if __name__ == "__main__":
    index_universe()
