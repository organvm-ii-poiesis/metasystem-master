# Project Definition: Orchestrator Awareness (Phase D-1)

**Objective:**
Formalize the "Universal Orchestrator" capabilities of Omni-Dromenon Machina by implementing the first cross-project automation cycle. The goal is to prove that the Orchestrator can *read* the state of a managed project (`life-my--midst--in`), *analyze* its needs based on its `seed.yaml`, and *generate* a valid, actionable task list without human intervention.

**Scope:**
- **Source:** `omni-dromenon-machina` (The Orchestrator)
- **Target:** `life-my--midst--in` (The Managed Project)
- **Boundaries:** Read-only analysis of the target. No code modification in the target yet. Generation of "Meta-Tasks" in the Orchestrator's queue.

**Inputs:**
1.  **Metasystem Manifest:** `4jp-metasystem.yaml` (root configuration).
2.  **Target Genome:** `../life-my--midst--in/seed.yaml` (constraints & roadmap).
3.  **Target State:** Current file structure and content of `life-my--midst--in`.

**Outputs:**
1.  **Analysis Report:** A markdown document (`ORCHESTRATOR_REPORT_001.md`) summarizing the target's health, alignment with `seed.yaml`, and next logical steps.
2.  **Task Queue:** A JSON or YAML file (`task_queue.json`) listing specific, atomic tasks for Agents to execute in the next phase (e.g., "Generate Schema Tests", "Refactor API module").

**Success Metrics (KPIs):**
- **Accuracy:** The Analysis Report correctly identifies the project's current phase (Implementation) and tech stack (Next.js/Neo4j).
- **Alignment:** The generated Tasks map 1:1 to the "Growth Objectives" defined in the target's `seed.yaml`.
- **Autonomy:** The entire process (Scan -> Analyze -> Report) runs via a single script execution.

**Constraints:**
- **Safety:** The Orchestrator must NOT modify files in `life-my--midst--in` during this phase.
- **Context:** The analysis must respect the `automation_contract` defined in the target's seed (e.g., allowed read paths).
- **Performance:** The scan and analysis must complete in under 30 seconds.

**Methodology:**
1.  **Develop `scout.ts`:** A script in `omni-dromenon-machina/core-engine/src/orchestrator/` to read and parse the target's `seed.yaml`.
2.  **Implement `analyst.ts`:** A logic module that compares the *actual* file structure against the *expected* structure defined in the seed.
3.  **Execute & Verify:** Run the scout, generate the report, and manually verify against the known state of `life-my--midst--in`.
