# Feature Implementation Plan: workspace_quality_and_security_overhaul

## 📋 Todo Checklist
- [ ] **Standardization**: Create a shared ESLint/Prettier configuration package for the metasystem.
- [ ] **Security (Crypto)**: Audit `trade-perpetual-future` dependencies and implement a lockfile freeze.
- [ ] **Security (Automation)**: Verify `.gitignore` rules for `mail_automation` and `my--father-mother` to prevent credential leaks.
- [ ] **Performance**: Analyze `gamified-coach-interface` bundle size and Three.js asset loading strategies.
- [ ] **Documentation**: Consolidate architectural diagrams from all projects into a central Metasystem Wiki.
- [ ] **Orchestration**: Extend `omni-dromenon-machina` to support "Quality Guard" tasks that run `audit` commands across managed repos.
- [ ] Final Review and Testing

## 🔍 Analysis & Investigation

### Codebase Structure
The workspace is a "Metasystem" managed by `omni-dromenon-machina`.
- **Orchestrator**: `omni-dromenon-machina` (Node/TS) - High quality, strict types.
- **Monorepo**: `life-my--midst--in` (Turbo/Next.js) - Strict governance via `seed.yaml`.
- **Web Apps**: `gamified-coach-interface`, `trade-perpetual-future` (React/Vite).
- **Tools**: `mail_automation`, `my--father-mother` (Python).

### Current Architecture
- **Federated Governance**: Each project has local config, but `omni-dromenon` is acquiring capabilities to audit them.
- **Language Split**: Heavy TypeScript focus for apps, Python for local automation/tools.
- **Deployment**: Docker/Cloud Run for the core engine; Vercel/Netlify patterns for web apps.

### Dependencies & Integration Points
- **Shared**: `mcp-servers` provides local intelligence capabilities to multiple projects.
- **External**: Google Cloud (Firestore, Cloud Run), Solana (Drift Protocol), OpenAI/Anthropic APIs.

### Considerations & Challenges
- **Secret Management**: Python scripts (`mail_automation`) rely on local files (`credentials.json`) which pose a leak risk if not strictly git-ignored.
- **Consistency**: TypeScript configs vary slightly between `omni-dromenon` and `trade-perpetual-future`.
- **Local Data**: `my--father-mother` stores sensitive clipboard history in SQLite; encryption at rest should be considered.

## 📝 Implementation Plan

### Prerequisites
- Access to all repositories (verified).
- `omni-dromenon-machina` operational (verified).

### Step-by-Step Implementation

1. **Step 1: Unify TypeScript & Linting Standards**
   - **Context**: Reduce cognitive load by enforcing consistent rules.
   - Files to modify: Create `packages/config-eslint` in `life-my--midst--in` (as it's the monorepo) or a root-level config in `omni-dromenon`.
   - Action: Define a "Strict Metasystem" preset (AirBnb style + Prettier) and propagate to `trade-perpetual-future`.

2. **Step 2: Hardening Python Automation**
   - **Context**: Prevent credential leaks.
   - Files to modify: `mail_automation/.gitignore`.
   - Changes needed: Ensure `token.pickle`, `credentials.json`, and `*.log` are explicitly ignored. Add a pre-commit hook script to check for high-entropy strings.

3. **Step 3: Crypto-Safety Audit**
   - **Context**: `trade-perpetual-future` handles real funds via wallet connection.
   - Action: Run `npm audit`. Implement `socket.io` security headers if used.
   - Files to modify: `trade-perpetual-future/package.json` (update dependencies).

4. **Step 4: Performance Optimization (3D)**
   - **Context**: `gamified-coach-interface` loads 3D scenes.
   - Action: Implement Draco compression for models and lazy-loading for the `StrategyCore`.
   - Files to modify: `gamified-coach-interface/src/SceneManager.js`.

5. **Step 5: Metasystem Quality Guard**
   - **Context**: Automate this review process.
   - Files to modify: `omni-dromenon-machina/core-engine/src/orchestrator/tester.ts`.
   - Changes needed: Add a `runSecurityAudit` method that triggers `npm audit` or `pip-audit` in managed workspaces and reports findings to the dashboard.

### Testing Strategy
- **Linting**: Run `eslint .` across all TS projects; expect zero errors.
- **Security**: Run `trivy` or `npm audit` on all repos.
- **Performance**: Use Lighthouse CI on the landing page and dashboard.

## 🎯 Success Criteria
- **Zero Critical Vulnerabilities** across all 4 major projects.
- **Unified Style**: All TypeScript projects pass the same strict linting rules.
- **Automated Vigilance**: The Orchestrator reports security status alongside project health in the Performer Dashboard.
