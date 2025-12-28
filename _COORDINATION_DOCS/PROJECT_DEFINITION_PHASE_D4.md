# Project Definition: Metasystem Production Deployment (Phase D-4)

**Objective:**
Deploy the fully integrated **4jp Metasystem** to production (Google Cloud Platform), ensuring that the "Universal Orchestrator" capabilities—including multi-project health monitoring, task dispatch, and real-time dashboard visibility—are fully functional in the live cloud environment.

**Scope:**
- **Core Engine:** `omni-dromenon-core` (Orchestrator Backend).
- **Performance SDK:** `omni-dromenon-sdk` (Performer/Orchestrator Dashboard).
- **Landing Page:** `omni-dromenon-landing` (Entry point).
- **Infrastructure:** Google Cloud Run (us-central1).
- **Boundaries:** This phase focuses on the *orchestrator's* ability to see the universe. It does *not* involve deploying the satellite projects (e.g., `trade-perpetual-future`) to their own production environments yet, only verifying the Orchestrator's *awareness* of them.

**Inputs:**
1.  **Metasystem Manifest:** `omni-dromenon-machina/4jp-metasystem.yaml` (The Source of Truth).
2.  **Source Code:** Latest revisions of Core Engine, SDK, and Landing Page.
3.  **Genomes:** `seed.yaml` files for all managed projects (verified locally).

**Outputs:**
1.  **Live Services:** 3 healthy Cloud Run services.
2.  **Verified Dashboard:** A live Performer Dashboard showing 7/7 "Green" projects.
3.  **Functional Dispatch:** A successful API test of the `/metasystem/dispatch` endpoint in production.

**Success Metrics (KPIs):**
- **Deployment Success:** `DEPLOY_ALL.sh` completes with exit code 0.
- **Health Check:** Core Engine `/metasystem/health` endpoint returns 200 OK and valid JSON data for 7 projects.
- **Visual Verification:** Performer Dashboard loads within 3 seconds and displays the "Metasystem Health" card correctly.
- **Integration:** Dispatching a task from the live dashboard logs a success message in the Core Engine logs.

**Methodology:**
1.  **Pre-Flight Check:** Verify local build and manifest paths one last time.
2.  **Execute Deployment:** Run `./DEPLOY_ALL.sh` to build containers and push to GCR/Cloud Run.
3.  **Post-Deployment Verification:**
    - Curl the health endpoint.
    - Inspect Cloud Run logs for startup errors.
    - Manually test the dashboard UI.
4.  **Documentation:** Update `CLOUD_HANDOFF_SUMMARY.md` with the new capabilities.

**Constraints:**
- **Cloud Build Limits:** Ensure Docker builds stay within timeout limits.
- **Secrets:** Ensure `4jp-metasystem.yaml` does not expose sensitive paths (it uses relative paths or mocked cloud status, which is safe).
