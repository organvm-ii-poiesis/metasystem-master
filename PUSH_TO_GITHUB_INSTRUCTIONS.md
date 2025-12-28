# Push to GitHub Instructions

## Prerequisites

1. **GitHub CLI installed** ✓ (Already installed at `/opt/homebrew/bin/gh`)
2. **GitHub authentication** (Need to complete)
3. **Organization access** (Ensure you have admin access to `omni-dromenon-machina` org)

## Step 1: Authenticate with GitHub CLI

```bash
gh auth login
```

Follow the prompts:
- **What account do you want to log into?** GitHub.com
- **What is your preferred protocol?** HTTPS
- **Authenticate Git with your GitHub credentials?** Yes
- **How would you like to authenticate?** Login with a web browser (recommended)

Copy the one-time code and paste it in your browser.

## Step 2: Verify Authentication

```bash
gh auth status
```

You should see: "✓ Logged in to github.com as [your-username]"

## Step 3: Run the Push Script

```bash
cd /Users/4jp/Desktop/omni-dromenon-machina
./PUSH_ALL_REPOS.sh
```

This script will:
1. Initialize git in each repository directory
2. Create `.gitignore` files where needed
3. Add and commit all files
4. Create GitHub repositories in the `omni-dromenon-machina` org
5. Push all content to GitHub

## What Gets Pushed

The following 12 repositories will be created/updated:

**Core System:**
- `core-engine` - WebSocket server, consensus algorithm
- `performance-sdk` - React UI components
- `client-sdk` - WebSocket client library
- `audio-synthesis-bridge` - OSC gateway

**Documentation & Theory:**
- `docs` - Technical specifications, guides
- `academic-publication` - Papers, conference submissions

**Reference Implementations:**
- `example-generative-music` - Music POC
- `example-generative-visual` - Visual art reference
- `example-choreographic-interface` - Choreography reference
- `example-theatre-dialogue` - Theatre/dialogue reference

**Community:**
- `artist-toolkit-and-templates` - Grant templates, guides
- `.github` - Org-level configuration

## Verification

After the script completes, verify at:
```
https://github.com/orgs/omni-dromenon-machina/repositories
```

You should see all 12 repositories listed.

## Troubleshooting

### "You are not logged into any GitHub hosts"
Run: `gh auth login` and follow the authentication steps.

### "Permission denied"
Ensure you have admin access to the `omni-dromenon-machina` organization.

### "Repository already exists"
The script will detect existing repos and push to them instead of creating new ones.

### Individual repository push failed
You can manually navigate to the repo and run:
```bash
cd /Users/4jp/Desktop/omni-dromenon-machina/[repo-name]
git init
git add .
git commit -m "Initial commit"
gh repo create omni-dromenon-machina/[repo-name] --public
git remote add origin https://github.com/omni-dromenon-machina/[repo-name].git
git push -u origin main
```

## Next Steps (After Push)

Once all repositories are on GitHub, the coordination docs in `_COORDINATION_DOCS/` outline the next phases:

1. **Phase A (Dec 7-8):** AI services work autonomously on:
   - Consensus algorithm (Jules)
   - Grant narrative (Gemini)
   - CI/CD workflows (Copilot)

2. **Phase B (Dec 11):** Human review and validation

3. **Phase C (Dec 13-27):** Demo deployment

4. **Phase D (Dec 27+):** Grant submissions

See `START_HERE.md` for detailed timeline.
