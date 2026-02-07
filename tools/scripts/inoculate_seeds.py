#!/usr/bin/env python3
import os
import yaml
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
ORGS = ["4444JPP", "ivviiviivvi", "omni-dromenon-machina", "labores-profani-crux"]

# Heuristic Maps
ORG_ROLES = {
    "4444JPP": "archive/origin",
    "ivviiviivvi": "mythos/research",
    "omni-dromenon-machina": "architect/core",
    "labores-profani-crux": "commercial/product"
}

def detect_tech_stack(path):
    stack = []
    if (path / "package.json").exists():
        stack.append("node")
        stack.append("typescript") # Assume TS for modern sanity
    if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
        stack.append("python")
    if (path / "Cargo.toml").exists():
        stack.append("rust")
    if (path / "Dockerfile").exists():
        stack.append("docker")
    return stack

def generate_seed(repo_name, org, path):
    print(f"🌱 Inoculating {org}/{repo_name}...")
    
    stack = detect_tech_stack(path)
    role = ORG_ROLES.get(org, "unknown")
    
    seed_content = {
        "version": 1,
        "project": {
            "name": repo_name,
            "description": "Auto-generated seed. Waiting for human intent.",
            "owners": [{"handle": org, "role": "steward"}],
            "repo": {
                "org": org,
                "type": stack[0] if stack else "generic",
                "role": role
            }
        },
        "architecture": {
            "tech_stack": stack
        },
        "automation_contract": {
            "ai_access": {
                "read_paths": ["**/*"],
                "write_paths": ["src/**", "docs/**", "tests/**"],
                "disallowed_writes": [".github/workflows/**", "seed.yaml"]
            }
        }
    }
    
    with open(path / "seed.yaml", "w") as f:
        yaml.dump(seed_content, f, sort_keys=False)

def inoculate_universe():
    print("💉 Beginning Mass Inoculation...")
    
    count = 0
    for org in ORGS:
        org_path = WORKSPACE_ROOT / org
        print(f"Scanning Org: {org} at {org_path}")
        if not org_path.exists(): 
            print("  -> Does not exist.")
            continue
        
        # Special handling for nested structure in omni-dromenon-machina
        if org == "omni-dromenon-machina":
            nested_path = org_path / "omni-dromenon-machina"
            if nested_path.exists() and nested_path.is_dir():
                print(f"  -> Entering nested directory: {nested_path}")
                # Recursively check this folder too
                for item in os.listdir(nested_path):
                    repo_path = nested_path / item
                    if repo_path.is_dir() and (repo_path / ".git").exists():
                        if not (repo_path / "seed.yaml").exists():
                            try:
                                generate_seed(item, org, repo_path)
                                count += 1
                            except Exception as e:
                                print(f"❌ Failed to seed {item}: {e}")
                        else:
                            print(f"  -> Seed already exists for {item}")

        for item in os.listdir(org_path):
            repo_path = org_path / item
            # print(f"  Checking {item}...") 
            
            # Check if valid repo
            if repo_path.is_dir() and (repo_path / ".git").exists():
                should_seed = False
                
                if not (repo_path / "seed.yaml").exists():
                    should_seed = True
                else:
                    # Check if seed matches current org
                    try:
                        with open(repo_path / "seed.yaml", "r") as f:
                            data = yaml.safe_load(f)
                            current_org = data.get("project", {}).get("repo", {}).get("org", "")
                            if current_org != org:
                                print(f"  ⚠️  Seed Org Mismatch ({current_org} != {org}). Updating...")
                                should_seed = True
                    except Exception:
                        should_seed = True

                if should_seed:
                    try:
                        generate_seed(item, org, repo_path)
                        count += 1
                    except Exception as e:
                        print(f"❌ Failed to seed {item}: {e}")
                else:
                    print(f"  -> Seed valid for {item}")
            else:
                print(f"  -> Not a git repo: {item}")

if __name__ == "__main__":
    inoculate_universe()
