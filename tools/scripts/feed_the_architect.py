#!/usr/bin/env python3
import json
import requests
import sys
from pathlib import Path
import time

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
INDEX_FILE = WORKSPACE_ROOT / "omni-dromenon-machina/data/universe_index.json"
API_URL = "http://localhost:3000/api/architect/memorize"

def feed_memory():
    print("🧠 Feeding the Architect (Ingesting Index into Chroma)...")
    
    if not INDEX_FILE.exists():
        print("❌ Index not found. Run 'scripts/index_universe.py' first.")
        sys.exit(1)
        
    with open(INDEX_FILE, 'r') as f:
        data = json.load(f)
        
    total_files = sum(len(repo['files']) for repo in data)
    print(f"   📚 Found {len(data)} repositories with {total_files} files.")
    
    count = 0
    errors = 0
    
    for repo in data:
        repo_name = repo['repo']
        print(f"   Processing {repo_name}...", end=" ", flush=True)
        
        for file in repo['files']:
            payload = {
                "content": file['content'],
                "source": f"{repo_name}/{file['name']}"
            }
            
            try:
                res = requests.post(API_URL, json=payload, timeout=10)
                if res.status_code == 200:
                    count += 1
                else:
                    errors += 1
            except Exception:
                errors += 1
                
        print("✅")
        # Sleep briefly to avoid rate limiting Gemini Embedding API if needed
        # time.sleep(0.5) 

    print(f"\n✨ Ingestion Complete.")
    print(f"   - Memorized: {count} documents")
    print(f"   - Errors: {errors}")

if __name__ == "__main__":
    feed_memory()
