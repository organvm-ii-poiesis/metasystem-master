# PHASE A BRIEFING TEMPLATES: Copy-Paste Ready

**Use these templates to brief AI services Dec 6 evening**
**Each service executes independently Dec 7-8**
**Deadline: Dec 8, 11:59 PM for all deliverables**

---

## TEMPLATE A: CONSENSUS ALGORITHM (COPY TO JULES)

**You are:** Backend engineer implementing consensus voting for Omni-Dromenon-Engine

**Task:** Create weighted consensus algorithm + tests + benchmark

**Timeline:** Dec 7-8 | Deadline Dec 8, 11:59 PM

**Algorithm Specification:**

```
INPUT: Array of Vote objects
{
  voterId: string
  parameter: string
  value: number (0-100)
  weight: number (0.5-1.5)
  timestamp: number (milliseconds)
  location?: {latitude, longitude}
}

OUTPUT: ConsensusResult
{
  parameter: string
  value: number (0-100, rounded)
  confidence: number (0-1)
  participantCount: number
  executionTimeMs: number
}

PROCESS:
1. Temporal decay: 0-5s weight×1.0, 5-10s weight×0.8, >10s discard
2. Proximity bonus: <100m distance → weight+0.2
3. Outlier filter: Remove votes >2σ from mean
4. Weighted mean: Σ(value×weight)/Σ(weight)
5. Confidence: 1-(σ/100)
```

**Files to Create:**
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/src/consensus/weighted-consensus.ts`
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/tests/consensus.test.ts`
- `/Users/4jp/Desktop/omni-dromenon-machina/core-engine/benchmarks/consensus-bench.ts`

**Success Criteria:**
✅ `npm test` passes (100% coverage)
✅ `npm run benchmark` shows P95 <1ms for 1000 votes
✅ TypeScript strict mode, zero dependencies
✅ No 'any' types

---

## TEMPLATE B: GRANT NARRATIVE (COPY TO GEMINI)

**You are:** Research advisor writing compelling grant narrative

**Task:** 1200-word narrative for Ars Electronica/Mozarteum XR Residency (€40,000)

**Timeline:** Dec 7-8 | Deadline Dec 8, 11:59 PM

**Structure (Exact word count targets):**

1. **Problem (200±20w):** Why audience needs computational agency
2. **Technical (350±30w):** How weighted consensus works, P95=2ms validation
3. **Impact (300±30w):** Artist vocabulary, reciprocal creation paradigm, research potential
4. **Timeline (200±20w):** 6-month residency roadmap
5. **Risks (150±15w):** Network reliability, artist adoption, latency at scale

**Tone:** Professional, academic rigor, artistic passion evident, honest about constraints

**File Output:**
`/Users/4jp/Desktop/omni-dromenon-machina/GRANT_MATERIALS/ars-electronica-narrative-DRAFT.md`

**Success Criteria:**
✅ 1200±50 words
✅ Five sections, properly proportioned
✅ Specific metrics cited (2ms, consensus algorithm details)
✅ Grounded in POC validation, not hype
✅ Submission-ready quality

---

## TEMPLATE C: CI/CD WORKFLOWS (COPY TO COPILOT)

**You are:** DevOps engineer setting up GitHub Actions for org

**Task:** Create 3 GitHub Actions workflows

**Timeline:** Dec 7-8 | Deadline Dec 8, 11:59 PM

**Workflow 1: test.yml (runs on push/PR)**
```yaml
name: Test
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18.x, 20.x]
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
    - run: npm install
    - run: npm run build
    - run: npm test
    - uses: codecov/codecov-action@v3
      if: always()
```

**Workflow 2: deploy-docs.yml (runs on docs/ changes)**
```yaml
name: Deploy Docs
on:
  push:
    branches: [main]
    paths: ['docs/**', '.github/workflows/deploy-docs.yml']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - run: pip install mkdocs mkdocs-material
    - run: mkdocs build
    - uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site
```

**Workflow 3: release.yml (runs on git tag)**
```yaml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '20.x'
        registry-url: 'https://registry.npmjs.org'
    - run: npm install && npm run build
    - uses: actions/create-release@v1
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      with:
        tag_name: ${{ github.ref }}
        release_name: Release ${{ github.ref }}
        body_path: CHANGELOG.md
    - run: npm publish
      env:
        NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Files Output:**
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/test.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/deploy-docs.yml`
- `/Users/4jp/Desktop/omni-dromenon-machina/.github/workflows/release.yml`

**Success Criteria:**
✅ Valid YAML syntax
✅ Triggers correct (test: push/PR, docs: docs/ changes, release: tags)
✅ Uses GitHub Actions best practices
✅ Ready to push to GitHub

---

## BRIEFING CHECKLIST

**Template A → Jules:**
- [ ] Copy everything above "## TEMPLATE B"
- [ ] Paste into Jules session
- [ ] Deadline: Dec 8, 11:59 PM
- [ ] Output: Check file exists + npm test passes

**Template B → Gemini:**
- [ ] Copy everything above "## TEMPLATE C"
- [ ] Paste into Gemini session
- [ ] Deadline: Dec 8, 11:59 PM
- [ ] Output: Check file exists + word count ~1200

**Template C → Copilot:**
- [ ] Copy everything above "## BRIEFING CHECKLIST"
- [ ] Paste into Copilot session
- [ ] Deadline: Dec 8, 11:59 PM
- [ ] Output: Check all 3 workflows exist in .github/workflows/

---

**Send briefs tonight (Dec 6). Go offline through Dec 11. Return morning of Dec 11 to review outputs.**
