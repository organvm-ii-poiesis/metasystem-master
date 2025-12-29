# 📝 REQ-002: The Guild (Profane Infrastructure)

**Status:** DRAFT
**Owner:** Labores Profani Crux
**Target:** Phase 3 of Master Plan

## 1. Executive Summary
The "Guild" (`labores-profani-crux`) is the commercial arm of the Metasystem. It requires a distinct infrastructure optimized for **Reliability**, **Security**, and **Profit**. Unlike the Alchemist (Experimental), the Guild enforces strict CI/CD gates.

## 2. Core Requirements

### 2.1. The Sovereign Entity
*   **Organization:** A dedicated GitHub Organization `labores-profani-crux`.
*   **Mandate:** All repositories here must be private by default (until release).

### 2.2. The Assets (Migration)
*   `trade-perpetual-future`: DeFi Trading Bot.
*   `gamified-coach-interface`: 3D Fitness App.
*   `enterprise-plugin`: Proprietary MCP Server.

### 2.3. The Gatekeeper (CI/CD)
*   **Standard:** `profane-standards.yml` workflow.
*   **Gates:**
    1.  **Lint:** No warnings.
    2.  **Test:** 100% Pass.
    3.  **Audit:** `npm audit` (Security).
    4.  **Build:** Must compile production build.

## 3. Implementation Plan

### Step 1: GitHub Infrastructure
*   Create Org (Manual Step for User).
*   Create Repositories.

### Step 2: Migration
*   Update Git Remotes for local folders.
*   Push history.

### Step 3: Pipeline Definition
*   Create `.github/workflows/profane-standards.yml`.
*   Distribute to all 3 Guild repos.

## 4. Acceptance Criteria
1.  [ ] `git remote -v` for `trade-perpetual` points to `labores-profani-crux`.
2.  [ ] A push to `main` triggers the `profane-standards` workflow.
