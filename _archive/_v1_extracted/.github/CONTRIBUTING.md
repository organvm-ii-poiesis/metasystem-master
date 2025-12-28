# Contributing to Omni-Dromenon Engine

Thank you for your interest in contributing. This guide covers technical contributions, documentation, and artistic collaborations.

---

## Ways to Contribute

| Type | Description | Entry Point |
|------|-------------|-------------|
| **Code** | Features, bug fixes, optimizations | Pull requests |
| **Documentation** | Guides, API docs, tutorials | `documentation` repo |
| **Research** | Academic papers, studies, analysis | Issue with `research` label |
| **Art** | Performance designs, genre modules | Issue with `artistic` label |
| **Testing** | Bug reports, performance testing | Issues |

---

## Development Setup

### Prerequisites

```bash
# Required
node --version  # >= 20.0.0
npm --version   # >= 10.0.0
git --version   # >= 2.40.0

# Optional (for audio testing)
# SuperCollider 3.13+ or Max/MSP 8+
```

### Local Development

```bash
# Clone the repository you're contributing to
git clone https://github.com/omni-dromenon-engine/<repo-name>.git
cd <repo-name>

# Install dependencies
npm install

# Run tests
npm test

# Start development server (if applicable)
npm run dev
```

---

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make changes** with clear, atomic commits
4. **Run tests** and linting:
   ```bash
   npm test
   npm run lint
   ```
5. **Push** and open a PR against `main`
6. **Fill out** the PR template completely
7. **Address** reviewer feedback

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example:**
```
feat(consensus): add temporal decay weighting

Implements exponential decay for audience inputs based on timestamp.
Decay constant configurable via CAL_DECAY_RATE env variable.

Closes #42
```

---

## Code Standards

- **Style:** ESLint + Prettier (configs in each repo)
- **Testing:** Jest for unit tests, Playwright for E2E
- **Documentation:** JSDoc for public APIs
- **Coverage:** Maintain >80% on new code

---

## Issue Guidelines

### Bug Reports

Include:
- Environment (OS, Node version, browser)
- Steps to reproduce
- Expected vs. actual behavior
- Logs/screenshots if applicable

### Feature Requests

Include:
- Use case description
- Proposed solution (if any)
- Alternatives considered

---

## Questions?

- Open a [Discussion](https://github.com/orgs/omni-dromenon-engine/discussions)
- Check existing issues and docs first

---

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
