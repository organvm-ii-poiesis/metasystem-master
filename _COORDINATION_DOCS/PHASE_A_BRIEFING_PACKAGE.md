# PHASE A: AI SERVICE BRIEFING PACKAGE (READY TO DEPLOY)

**Status:** ✅ Ready to send to AI services immediately
**Date Prepared:** Dec 6, 2025
**Phase A Duration:** Dec 7-8, 2025
**Review Gate:** Dec 11, 2025 (morning)

---

## BRIEFING INSTRUCTIONS

1. **Read this document** for overview
2. **Copy appropriate template** (A, B, or C below)
3. **Paste into AI service** (Jules, Gemini, or Copilot)
4. **AI executes Dec 7-8**
5. **Return outputs to:** `/Users/4jp/Desktop/omni-dromenon-machina/` (paths match your assignments)

---

## OVERVIEW: WHAT IS PHASE A?

**Goal:** Autonomous AI execution to complete three critical Phase A deliverables with zero human coordination.

**Timeline:** Dec 7 (Friday) → Dec 8 (Saturday) EOD
**Deadline:** Both services deliver final outputs by Dec 8, 11:59 PM
**Review:** Human reviews morning of Dec 11 (Wed)

**Success = ALL THREE deliverables complete + meet acceptance criteria**

---

## PHASE A OVERVIEW: CRITICAL DATES & DEPENDENCIES

| Component | Owner | Input | Output | Deadline | Success Criteria |
|-----------|-------|-------|--------|----------|------------------|
| **Consensus Algo** | Jules | Weighted consensus spec (below) | `core-engine/src/consensus/weighted-consensus.ts` + tests | Dec 8 EOD | npm test passes, <1ms benchmark, 100% coverage |
| **Grant Narrative** | Gemini | Problem/structure (below) | `GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md` | Dec 8 EOD | 1200±50w, compelling, submission-ready |
| **CI/CD Workflows** | Copilot | Workflow specs (below) | `.github/workflows/{test,deploy-docs,release}.yml` | Dec 8 EOD | Valid YAML, ready to push, follows best practices |

**ALL THREE MUST COMPLETE BY DEC 8 EOD FOR PHASE B APPROVAL**

---

## PHASE A COMMUNICATIONS

**No coordination needed between AI services.** Each works independently:
- **Jules** implements consensus in `core-engine/` (self-contained algorithm)
- **Gemini** writes narrative based on provided outline (no dependencies)
- **Copilot** creates workflows (uses standard GitHub Actions syntax)

**If one fails, others can still succeed.** Proceed with Phase B even if one needs rework.

---

---

# TEMPLATE A: JULES (BACKEND ENGINEER)

**Copy everything below this line. Paste into Jules/Claude Code session.**

---

## ASSIGNMENT: CONSENSUS ALGORITHM + TESTS + BENCHMARK

**You are:** Backend engineer implementing real-time consensus voting for audience-participatory performance.

**Your task:** Implement weighted consensus algorithm with tests + benchmarks for Omni-Dromenon-Engine.

**Timeline:** Dec 7-8, 2025 | Deadline: Dec 8, 11:59 PM
**Output location:** `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/`

---

### THE ALGORITHM (Detailed Specification)

**Purpose:** Aggregate 1000s of concurrent audience votes into coherent performance parameters in <1ms.

**Input:** Array of `Vote` objects (voter ID, parameter, value 0-100, weight 0.5-1.5, timestamp, optional location)

**Output:** `ConsensusResult` (parameter name, aggregated value 0-100, confidence 0-1, participant count, execution time)

**Processing Pipeline:**

```
1. TEMPORAL DECAY
   - Current time: T
   - Vote timestamp: t_v
   - Age: T - t_v
   - Weight multiplier:
     * 0-5s: weight *= 1.0 (full strength)
     * 5-10s: weight *= 0.8 (80% strength)
     * >10s: discard vote entirely
   
2. PROXIMITY BONUS (optional, if location provided)
   - Calculate distance between voter & performance center
   - If distance < 100m: weight += 0.2 (bonus)
   - If distance >= 100m: no bonus
   
3. OUTLIER FILTERING
   - Calculate mean μ and std dev σ of all vote values
   - Remove any vote where |value - μ| > 2σ
   - Recalculate μ, σ with filtered set
   
4. WEIGHTED AGGREGATION
   - aggregated_value = Σ(vote.value × weight) / Σ(weight)
   - confidence = 1 - (σ / max_possible_value)
   - max_possible_value = 100
   
5. RETURN RESULT
   {
     parameter: string,
     value: number (0-100, rounded to nearest int),
     confidence: number (0-1, 2 decimals),
     participantCount: number (how many votes after filtering),
     executionTimeMs: number (milliseconds to compute)
   }
```

---

### TECHNICAL REQUIREMENTS

**Language & Constraints:**
- TypeScript (strict mode enabled)
- Node.js runtime
- Zero external dependencies (no npm packages except test framework)
- Must run in <1ms for 1000 concurrent votes
- 100% unit test coverage
- Benchmark suite showing performance

**Performance Targets:**
- P95 latency: <1ms for 1000 votes
- Memory: <10MB for 10,000 votes in flight
- No GC pauses during aggregation

**Files to Create:**

1. **`core-engine/src/consensus/weighted-consensus.ts`** (main implementation)
   - Export `class WeightedConsensus`
   - Implement `aggregate(votes: Vote[]): ConsensusResult`
   
2. **`core-engine/tests/consensus.test.ts`** (unit tests)
   - Test empty vote array
   - Test single vote
   - Test temporal decay (5s boundary, 10s discard)
   - Test proximity bonus (if location provided)
   - Test outlier filtering (2σ rule)
   - Test aggregation (weighted mean)
   - Test confidence calculation
   - Test with 100, 1000, 10000 votes
   - Expected: 100% code coverage
   
3. **`core-engine/benchmarks/consensus-bench.ts`** (performance benchmark)
   - Create 1000 random votes
   - Run aggregate() 100 times
   - Measure P50, P95, P99 latency
   - Report memory usage
   - Output: "P95 latency: XXms for 1000 votes"

---

### INTERFACE DEFINITIONS

```typescript
// Input interface
interface Vote {
  voterId: string;           // Unique voter ID
  parameter: string;         // e.g., "mood", "tempo", "intensity"
  value: number;             // 0-100 (what they voted for)
  weight: number;            // 0.5-1.5 (voter influence, default 1.0)
  timestamp: number;         // Date.now() milliseconds
  location?: {
    latitude: number;
    longitude: number;
  };
}

// Output interface
interface ConsensusResult {
  parameter: string;         // Which parameter this is for
  value: number;             // 0-100 (aggregated result)
  confidence: number;        // 0-1 (how confident is this result?)
  participantCount: number;  // How many votes were used
  executionTimeMs: number;   // How long computation took
}

// Class
class WeightedConsensus {
  aggregate(votes: Vote[]): ConsensusResult { ... }
}
```

---

### SUCCESS CRITERIA (ALL MUST PASS)

```bash
# 1. Code compiles
cd /Users/4jp/Desktop/omni-dromenon-machina/core-engine
npm install
npm run build
# Expected: No TypeScript errors, .js files generated

# 2. Tests pass
npm test
# Expected: All tests pass, 100% coverage reported

# 3. Benchmark runs
npm run benchmark
# Expected: Output shows "P95 latency: <1ms for 1000 votes"

# 4. No dependencies added (check package.json)
cat package.json | grep '"dependencies"'
# Expected: Empty or only core-engine's existing deps (no consensus lib added)

# 5. Code is strict TypeScript
# Expected: No "any" types, all params typed
```

---

### EDGE CASES TO HANDLE

- Empty vote array → Return default ConsensusResult with 0 participant count
- Single vote → Return that vote's value as consensus
- All votes identical → Return value with confidence = 1.0
- All votes filtered as outliers → Return mean of remaining votes
- Timestamp in future → Treat as current time
- Weight < 0.5 or > 1.5 → Clamp to range

---

### OUTPUT FORMAT

**File:** `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/src/consensus/weighted-consensus.ts`

Submit with:
1. Full implementation (algorithm + edge cases)
2. Type definitions (Vote, ConsensusResult, WeightedConsensus)
3. Docstrings explaining algorithm
4. Test file (100% coverage)
5. Benchmark file (proves <1ms performance)

**Deadline:** Dec 8, 11:59 PM
**Verification:** Paste output of `npm test` + `npm run benchmark` when complete

---

## END TEMPLATE A

---

---

# TEMPLATE B: GEMINI (RESEARCH & NARRATIVE)

**Copy everything below this line. Paste into Gemini session.**

---

## ASSIGNMENT: GRANT NARRATIVE (1200 WORDS)

**You are:** Research advisor synthesizing technical vision into compelling grant narrative.

**Your task:** Write 1200-word grant narrative for Ars Electronica/Mozarteum XR Residency (€40,000).

**Timeline:** Dec 7-8, 2025 | Deadline: Dec 8, 11:59 PM
**Output location:** `/Users/4jp/Desktop/omni-dromenon-machina/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`

---

### GRANT CONTEXT

**Funder:** Ars Electronica Mozarteum XR Residency
**Amount:** €40,000
**Deadline:** July 13, 2025
**Duration:** Typically 6-8 weeks residency
**Focus:** XR + performance + artistic innovation

**Your narrative will be read by:**
- Program officers (art/tech background)
- Peer reviewers (artists + researchers)
- Selection committee (Ars Electronica staff)

**Tone:** Professional, ambitious but honest, academically grounded, artistic passion evident

---

### STRUCTURE (EXACT WORD COUNT TARGETS)

Write 5 sections in this order:

#### SECTION 1: PROBLEM STATEMENT (200 ± 20 words)
**Pitch:** What problem does Omni-Dromenon-Engine solve?

**Key points to include:**
- Traditional performance: audience = passive spectators
- Limitation: one-directional creative authority (artist → audience)
- Opportunity: democratize creative agency without losing artistic control
- Stakes: Why this matters culturally/artistically
- Vision: "Reciprocal creation" as paradigm shift

**Example narrative arc:**
"For millennia, performance has maintained a fundamental asymmetry: artists create, audiences consume. Even interactive art often gamifies participation rather than inviting genuine creative partnership. Omni-Dromenon-Engine inverts this dynamic..."

#### SECTION 2: TECHNICAL APPROACH (350 ± 30 words)
**Pitch:** How does it actually work? Why is the technical approach important?

**Key points to include:**
- Contextual Awareness Layer (CAL) — real-time audience input aggregation
- Weighted consensus algorithm (temporal decay + proximity + outlier filtering)
- Parameter bus — translator between audience votes and performer control
- P95 latency = 2ms (proof that real-time responsiveness is validated, not theoretical)
- Genre-agnostic substrate (music, dance, theatre, visual all use same engine)
- Performer override authority (artists maintain final say)

**Technical credibility signals:**
- Mention validated POC (working prototype exists)
- Cite specific technical metrics (2ms latency)
- Explain weighted consensus in accessible terms
- Acknowledge constraints (WiFi reliability, latency at scale)

**Example narrative arc:**
"The system operates through a Contextual Awareness Layer that processes smartphone inputs from audience members in real-time. A weighted consensus algorithm aggregates diverse votes into coherent performance parameters while preserving minority perspectives through outlier-aware aggregation..."

#### SECTION 3: ARTISTIC & CULTURAL IMPACT (300 ± 30 words)
**Pitch:** Why does this matter? What doors does it open?

**Key points to include:**
- Artist vocabulary expansion (new compositional/choreographic possibilities)
- Audience transformation (from consumers to co-creators)
- NOT gamification (this is genuine creative partnership, not point-scoring)
- Generative vs. participatory distinction (system generates possibilities audience shapes)
- Research contribution (performance studies + HCI intersection)
- Precedent lineage (Cage, Kaprow, contemporary practice like teamLab, Blast Theory)
- Publishable research (peer-reviewed potential)

**Why funders care:**
- Ars Electronica funds cultural innovation
- XR/performance intersection is strategic focus
- Academic rigor + artistic vision both present
- Scalable model (can work in diverse venues + genres)

**Example narrative arc:**
"The shift from spectator to computational agent represents a fundamental reconception of audience role. Rather than gamifying participation, we're creating conditions for genuine reciprocal creation—where audience input becomes medium rather than metadata..."

#### SECTION 4: IMPLEMENTATION TIMELINE (200 ± 20 words)
**Pitch:** Realistic 6-month roadmap for residency period (Jan-Jun 2025 if awarded early 2025)

**Likely timeline (adjust if needed):**
- Months 1-2: Expand POC to all genres (visual, choreography, theatre, music)
- Months 2-3: Deploy beta at 2-3 venues with artist collaborators
- Months 3-4: Iterate based on feedback, draft publication
- Months 4-5: Production version + comprehensive documentation
- Months 6: Academic presentation prep + open-source release planning
- Post-residency: Conference presentations (NIME, DIS, CHI, ICMC)

**Realism signals:**
- Acknowledge what's already validated (POC)
- Break work into phases with clear milestones
- Build in iteration time (not overpromising)
- Plan for dissemination (not just artifact creation)

**Example narrative arc:**
"The residency period allows us to move from working prototype to production system across multiple artistic genres. Initial months focus on expanding the core engine; middle months engage collaborators in iterative testing; final months prepare for academic publication and community release..."

#### SECTION 5: RISKS & MITIGATION (150 ± 15 words)
**Pitch:** Show you've thought about what could go wrong. Be honest.

**Key risks:**
1. Network reliability (WiFi dropout during performance)
   - Mitigation: Design offline-fallback mode, geospatial bucketing for resilience
2. Artist adoption curve (unfamiliar interface for performers)
   - Mitigation: Customizable parameter sets, extensive artist toolkit + training
3. Latency at scale (100+ concurrent voters in large venue)
   - Mitigation: Redis caching, geographic clustering, stress-tested architecture
4. Privacy/consent (collecting location data from audience)
   - Mitigation: Opt-in anonymization, GDPR compliance, transparent consent

**Funder expectation:** They want to see you've thought critically, not that you've solved everything.

**Example narrative arc:**
"While the system has demonstrated 2ms P95 latency in lab conditions, large-scale venues present distinct challenges. We've architected mitigations including Redis-backed caching, geographic clustering for load distribution, and transparent consent frameworks for location data collection..."

---

### TONE & VOICE GUIDELINES

**Do:**
- Write in active voice ("the system aggregates votes" not "votes are aggregated")
- Use vivid language (this is art + research)
- Be specific (cite metrics, precedents, technical details)
- Show passion (you care about this)
- Acknowledge constraints honestly (builds credibility)

**Don't:**
- Oversell (no "revolutionary" or "paradigm-shifting" hype)
- Use jargon without explanation (define terms)
- Make unsupported claims (everything should be grounded in POC or referenced work)
- Be defensive (if risks are mentioned, that's okay)

---

### SUCCESS CRITERIA

```
1. Word count: 1200 ± 50 words (1150-1250)
   Check: wc -w output.md should show ~1200

2. Five sections present, properly proportioned
   - Problem: 200w
   - Technical: 350w
   - Impact: 300w
   - Timeline: 200w
   - Risks: 150w
   
3. Tone: Professional but artistic
   - Read aloud test: Does it sound like an artist-researcher or a grant consultant?
   
4. Specificity: Metrics + precedents cited
   - "P95 latency: 2ms" (specific, validated)
   - "Ars Electronica, teamLab, Blast Theory" (precedent lineage)
   - "Consensus algorithm with temporal decay + proximity bonus" (technical specificity)
   
5. Honesty about limitations
   - Risks section is candid, not defensive
   - Mitigation strategies are realistic
   
6. Submission readiness
   - No grammatical errors
   - Clear sections
   - Ready to paste into application form
```

---

### OUTPUT FORMAT

**File:** `/Users/4jp/Desktop/omni-dromenon-machina/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`

**Content:**
```markdown
# Ars Electronica/Mozarteum XR Residency Narrative

## Problem Statement
[200 words]

## Technical Approach
[350 words]

## Artistic & Cultural Impact
[300 words]

## Implementation Timeline
[200 words]

## Risks & Mitigation
[150 words]
```

**Submission:** Paste final output when complete

**Deadline:** Dec 8, 11:59 PM

---

## END TEMPLATE B

---

---

# TEMPLATE C: COPILOT (DEVOPS/CI-CD)

**Copy everything below this line. Paste into Copilot Chat.**

---

## ASSIGNMENT: CI/CD WORKFLOWS (3 GitHub Actions)

**You are:** DevOps engineer setting up GitHub Actions for Omni-Dromenon-Engine org.

**Your task:** Create 3 essential CI/CD workflows for the GitHub org.

**Timeline:** Dec 7-8, 2025 | Deadline: Dec 8, 11:59 PM
**Output location:** `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/`

---

### WORKFLOW 1: test.yml (Run tests on every PR/push)

**Trigger:** On push to any branch + on pull request
**Purpose:** Ensure code quality before merging

```yaml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    
    - name: Install dependencies
      run: npm install
    
    - name: Build
      run: npm run build
    
    - name: Run tests
      run: npm test
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      if: always()
```

**Key points:**
- Triggers: push to main/develop, PR to main/develop
- Matrix: Tests on Node 18 + 20 (two LTS versions)
- Caching: npm cache to speed up installs
- Steps: checkout → install → build → test → coverage
- Coverage: Uploads to codecov.io (free for open source)

---

### WORKFLOW 2: deploy-docs.yml (Deploy docs to GitHub Pages)

**Trigger:** Push to main when docs/ folder changes
**Purpose:** Keep documentation site up-to-date automatically

```yaml
name: Deploy Docs

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
      - '.github/workflows/deploy-docs.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install MkDocs
      run: |
        pip install mkdocs
        pip install mkdocs-material
        pip install mkdocs-mermaid2-plugin
    
    - name: Build docs
      run: mkdocs build
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
        cname: omni-dromenon-machina.github.io
```

**Key points:**
- Trigger: Only when docs/ changes (doesn't run on every push)
- Python 3.9: MkDocs requirement
- MkDocs plugins: material theme + mermaid diagrams
- Publish: Automatically deploys to gh-pages branch (GitHub Pages)
- CNAME: Optional (for custom domain if needed)

---

### WORKFLOW 3: release.yml (Publish releases & NPM packages)

**Trigger:** On git tag (e.g., `git tag v1.0.0 && git push --tags`)
**Purpose:** Automate GitHub releases + npm package publishing

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        registry-url: 'https://registry.npmjs.org'
    
    - name: Install dependencies
      run: npm install
    
    - name: Build
      run: npm run build
    
    - name: Create Release
      uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body_path: CHANGELOG.md
        draft: false
        prerelease: false
    
    - name: Publish to npm
      run: npm publish
      env:
        NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Key points:**
- Trigger: Any tag matching `v*` (semantic versioning)
- Build: Compiles TypeScript before publishing
- Release: Creates GitHub Release with CHANGELOG.md
- NPM: Publishes built package to npm registry
- Secrets: GitHub token (automatic) + NPM_TOKEN (must be set in repo settings)

---

### FILE STRUCTURE

Create 3 files in `.github/workflows/`:

```
.github/workflows/
├── test.yml            ← Run tests on PR/push
├── deploy-docs.yml     ← Deploy docs to GitHub Pages
└── release.yml         ← Publish releases + npm
```

---

### SETUP REQUIREMENTS (One-time, human does this Dec 11)

Before these workflows can run, repo maintainer must:

1. **Enable GitHub Pages:**
   - Repo settings → Pages → Source = GitHub Actions

2. **Set NPM_TOKEN secret (optional, only if publishing to npm):**
   - Generate token at npmjs.com/settings/tokens
   - Repo settings → Secrets and variables → Actions → New secret
   - Name: `NPM_TOKEN`
   - Value: [your npm token]

3. **Ensure package.json has build + test scripts:**
   ```json
   {
     "scripts": {
       "build": "tsc",
       "test": "jest",
       "benchmark": "ts-node benchmarks/"
     }
   }
   ```

4. **Ensure mkdocs.yml exists in repo root** (for deploy-docs workflow)

---

### SUCCESS CRITERIA

```bash
# 1. YAML syntax valid
cd /Users/4jp/Desktop/omni-dromenon-machina/.github/workflows
# Can use: https://github.com/ghe-runner/actions-validator
# Or: yamllint *.yml

# 2. Files exist
ls -la test.yml deploy-docs.yml release.yml
# Expected: All 3 files present

# 3. Trigger conditions make sense
# test.yml: runs on push + PR
# deploy-docs.yml: runs on push to main only
# release.yml: runs on tag only

# 4. Secrets referenced (but not stored in YAML)
grep "secrets\." *.yml
# Expected: Only references like ${{ secrets.GITHUB_TOKEN }}
# NOT actual token values!

# 5. GitHub Actions best practices
# ✅ Uses official actions (@v3, @v4)
# ✅ Caching enabled (npm cache)
# ✅ Conditional steps (if: always())
# ✅ Clear job names
# ✅ Comments explaining purpose
```

---

### DEBUGGING TIPS

**If workflow fails:**
1. Check GitHub Actions tab in repo for error logs
2. Common issues:
   - Missing `package.json` scripts (ensure npm test, npm build exist)
   - Node version mismatch (use LTS: 18.x or 20.x)
   - Missing mkdocs.yml for docs workflow
   - NPM_TOKEN not set for release workflow

**View workflow status:**
- GitHub repo → Actions tab → Click workflow → See run history

---

### OUTPUT FORMAT

**Files:**
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/test.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/deploy-docs.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/release.yml`

**Submit:** Paste the 3 workflow files as text when complete

**Deadline:** Dec 8, 11:59 PM

---

## END TEMPLATE C

---

---

# FINAL BRIEFING CHECKLIST

**For Jules:**
- [ ] Copy Template A (consensus algorithm assignment)
- [ ] Paste into Claude Code / coding assistant
- [ ] Brief: "Implement weighted consensus algorithm with tests + benchmark"
- [ ] Expected output: `core-engine/src/consensus/weighted-consensus.ts` + tests

**For Gemini:**
- [ ] Copy Template B (grant narrative assignment)
- [ ] Paste into Gemini
- [ ] Brief: "Write 1200-word grant narrative for Ars Electronica"
- [ ] Expected output: `GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`

**For Copilot:**
- [ ] Copy Template C (CI/CD workflows assignment)
- [ ] Paste into Copilot Chat
- [ ] Brief: "Create 3 GitHub Actions workflows (test, deploy-docs, release)"
- [ ] Expected output: `.github/workflows/{test,deploy-docs,release}.yml`

---

**TIMING: Send briefs now (Dec 6 evening)**
**EXECUTION: Dec 7-8 (autonomous)**
**REVIEW: Dec 11 morning (human validation gate)**

**YOU ARE READY TO DEPLOY PHASE A.**
