# 🏗️ PLAN-002: Guild Infrastructure

**Spec:** `specs/REQ-002-the-guild.md`
**Context:** `labores-profani-crux`
**Goal:** Prepare the commercial assets for deployment.

## 1. Pipeline Architecture
We need a reusable workflow file that enforces "Profane Standards."

### `profane-standards.yml`
*   **Triggers:** Push to `main`, PR.
*   **Jobs:**
    *   `quality`: Lint + Test.
    *   `security`: Dependency Audit.
    *   `build`: Production Build.

## 2. Execution Steps

1.  [ ] **Create Workflow:** `templates/profane-standards.yml`.
2.  [ ] **Distribute:** Copy workflow to `.github/workflows/` in:
    *   `trade-perpetual-future`
    *   `gamified-coach-interface`
    *   `enterprise-plugin`
3.  [ ] **Script:** Create `scripts/init_guild_remote.sh` to automate the remote switch once Org exists.

## 3. Dependencies
*   None.
