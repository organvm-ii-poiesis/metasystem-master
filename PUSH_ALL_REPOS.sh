#!/bin/bash

# PUSH_ALL_REPOS.sh
# Push all local repositories to GitHub org: omni-dromenon-machina
# Run from: /Users/4jp/Desktop/omni-dromenon-machina/

set -e  # Exit on error

ORG="omni-dromenon-machina"
BASE_DIR="/Users/4jp/Desktop/omni-dromenon-machina"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Pushing All Repos to GitHub${NC}"
echo -e "${BLUE}  Org: ${ORG}${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo -e "${RED}ERROR: GitHub CLI not authenticated${NC}"
    echo "Run: gh auth login"
    exit 1
fi

# List of repositories
REPOS=(
    "core-engine"
    "performance-sdk"
    "client-sdk"
    "audio-synthesis-bridge"
    "docs"
    "academic-publication"
    "example-generative-music"
    "example-generative-visual"
    "example-choreographic-interface"
    "example-theatre-dialogue"
    "artist-toolkit-and-templates"
    ".github"
)

# Function to process each repo
process_repo() {
    local repo_name=$1
    local repo_path="$BASE_DIR/$repo_name"

    echo -e "\n${BLUE}[${repo_name}]${NC}"

    # Navigate to repo
    cd "$repo_path" || { echo -e "${RED}Failed to cd into $repo_path${NC}"; return 1; }

    # Initialize git if not already a repo
    if [ ! -d ".git" ]; then
        echo "  Initializing git..."
        git init
        git branch -M main
    fi

    # Create .gitignore if missing (for TypeScript/Node repos)
    if [ ! -f ".gitignore" ] && [ -f "package.json" ]; then
        echo "  Creating .gitignore..."
        cat > .gitignore << 'EOF'
node_modules/
dist/
build/
.env
.env.local
*.log
.DS_Store
coverage/
.vscode/
.idea/
EOF
    fi

    # Add all files
    echo "  Adding files..."
    git add .

    # Create initial commit if needed
    if ! git rev-parse HEAD >/dev/null 2>&1; then
        echo "  Creating initial commit..."
        git commit -m "Initial commit: ${repo_name}

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
    else
        # Check if there are changes to commit
        if ! git diff-index --quiet HEAD --; then
            echo "  Committing changes..."
            git commit -m "Update ${repo_name} structure

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
        else
            echo "  No changes to commit"
        fi
    fi

    # Check if remote repo exists
    if gh repo view "${ORG}/${repo_name}" >/dev/null 2>&1; then
        echo "  Remote repo exists: ${ORG}/${repo_name}"
    else
        echo "  Creating GitHub repo: ${ORG}/${repo_name}..."
        if [ "$repo_name" = ".github" ]; then
            # Special handling for .github org repo
            gh repo create "${ORG}/.github" --public --description "Organization-level GitHub configuration"
        else
            gh repo create "${ORG}/${repo_name}" --public --description "Omni-Dromenon-Engine: ${repo_name}"
        fi
    fi

    # Set remote (if not already set)
    if ! git remote get-url origin >/dev/null 2>&1; then
        echo "  Setting remote..."
        git remote add origin "https://github.com/${ORG}/${repo_name}.git"
    fi

    # Push to GitHub
    echo "  Pushing to GitHub..."
    git push -u origin main

    echo -e "${GREEN}  ✓ ${repo_name} pushed successfully${NC}"
}

# Process each repository
for repo in "${REPOS[@]}"; do
    process_repo "$repo"
done

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  All repositories pushed successfully!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo "View your org at: https://github.com/orgs/${ORG}/repositories"
