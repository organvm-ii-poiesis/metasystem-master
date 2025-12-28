# .github

Organization-level GitHub configuration for the **Omni-Dromenon Engine** project.

## Purpose

This repository contains default community health files and templates that are automatically inherited by all repositories in the `omni-dromenon-engine` organization that don't have their own versions.

## Contents

| Path | Purpose |
|------|---------|
| `profile/README.md` | Organization profile displayed on [github.com/omni-dromenon-engine](https://github.com/omni-dromenon-engine) |
| `CODE_OF_CONDUCT.md` | Community standards and expected behavior |
| `CONTRIBUTING.md` | Guidelines for contributing code, docs, research, and art |
| `SECURITY.md` | Security policy and vulnerability reporting |
| `SUPPORT.md` | How to get help and community resources |
| `FUNDING.yml` | Sponsorship and funding links |
| `ISSUE_TEMPLATE/` | Standardized issue templates (bug, feature, research) |
| `PULL_REQUEST_TEMPLATE/` | Pull request template with checklist |
| `workflow-templates/` | Reusable GitHub Actions workflows |

## How It Works

GitHub automatically uses these files for any repository in the organization that doesn't have its own version:

1. **Community health files** (`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, etc.) — appear in the "Community" section of each repo
2. **Issue templates** — available when creating new issues in any org repo
3. **PR templates** — auto-populate when opening pull requests
4. **Workflow templates** — appear under Actions → "Workflows created by omni-dromenon-engine"

## Customization

To override any file for a specific repository:
1. Create the same file in that repository's `.github/` directory
2. The repo-specific file takes precedence

## Workflow Templates

Available workflow templates:

| Template | Description |
|----------|-------------|
| `ci.yml` | Standard CI: lint, test (Node 20.x/22.x), build, security audit |

To use in a repository:
1. Go to Actions tab
2. Click "New workflow"
3. Select from "Workflows created by omni-dromenon-engine"

## Local Development

```bash
# Clone this repository
git clone https://github.com/omni-dromenon-engine/.github.git
cd .github

# Make changes
# ...

# Commit and push
git add .
git commit -m "chore: update community files"
git push origin main
```

## Links

- [Organization Profile](https://github.com/omni-dromenon-engine)
- [Discussions](https://github.com/orgs/omni-dromenon-engine/discussions)
- [Project Documentation](https://github.com/omni-dromenon-engine/documentation)

## License

MIT License — see individual repositories for their specific licenses.
