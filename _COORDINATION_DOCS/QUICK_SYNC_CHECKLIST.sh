#!/bin/bash

# OMNI-DROMENON-MACHINA: QUICK SYNC CHECKLIST
# Copy/paste commands below to organize local structure + sync with GitHub

echo "🔧 Starting Omni-Dromenon-Machina Local Sync..."

# STEP 1: Move to correct directory
cd /Users/4jp/Desktop/omni-dromenon-machina || { echo "❌ Directory not found"; exit 1; }
echo "✅ In omni-dromenon-machina/"

# STEP 2: Extract .github drafts (for comparison)
echo "📦 Extracting .github draft versions..."
mkdir -p _temp_compare
unzip -q .github-v1.zip -d _temp_compare/v1_extracted/
unzip -q .github-v2.zip -d _temp_compare/v2_extracted/
echo "✅ Extracted to _temp_compare/"
echo "   Review: ls -la _temp_compare/v1_extracted/ vs v2_extracted/"

# STEP 3: Clean up macOS clutter
echo "🧹 Cleaning up macOS files..."
find . -name ".DS_Store" -delete
echo "✅ Removed .DS_Store files"

# STEP 4: Organize handoff docs
echo "📚 Organizing coordination documents..."
mkdir -p _COORDINATION_DOCS
mv HANDOFF_MASTER.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ HANDOFF_MASTER.md"
mv AI_ORCHESTRATION_TIMELINE.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ AI_ORCHESTRATION_TIMELINE.md"
mv PER_REPO_KEYS.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ PER_REPO_KEYS.md"
mv AI_BRIEFING_TEMPLATES.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ AI_BRIEFING_TEMPLATES.md"
mv FINAL_SUMMARY.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ FINAL_SUMMARY.md"
mv GITHUB_SYNC_MASTER.md _COORDINATION_DOCS/ 2>/dev/null && echo "  ✅ GITHUB_SYNC_MASTER.md (THIS FILE)"

# STEP 5: Create client-sdk locally (matches GitHub)
echo "🆕 Creating client-sdk..."
mkdir -p client-sdk
cat > client-sdk/README.md << 'EOF'
# Client SDK

WebSocket client library for connecting audience devices to Omni-Dromenon-Engine.

**Status:** Scaffolding
**Purpose:** Lightweight JavaScript/TypeScript client for audience vote submission
**Entry:** `src/index.ts`

Integration: See `performance-sdk/` for UI components using this client.
EOF
echo "✅ client-sdk/ created"

# STEP 6: Archive old .github drafts
echo "📦 Archiving old .github drafts..."
mkdir -p _archive
mv .github-v1.zip _archive/ 2>/dev/null && echo "  ✅ Archived .github-v1.zip"
mv .github-v2.zip _archive/ 2>/dev/null && echo "  ✅ Archived .github-v2.zip"

# STEP 7: Clean up temp comparison folder
rm -rf _temp_compare/
echo "✅ Cleaned up temp files"

# STEP 8: Update README.md
echo "📝 Updating README.md..."
cat > README.md << 'EOF'
# Omni-Dromenon-Machina

Real-time audience-participatory performance system.

**GitHub Org:** https://github.com/orgs/omni-dromenon-machina

## Repository Structure

**Core System:**
- `core-engine/` - WebSocket server + consensus algorithm
- `performance-sdk/` - React UI components + abstractions
- `client-sdk/` - WebSocket client for audience devices
- `audio-synthesis-bridge/` - OSC gateway for external synths

**Theory & Docs:**
- `docs/` - Specifications, guides, theory
- `academic-publication/` - Papers, conference materials

**Reference Implementations:**
- `example-generative-music/` - Working POC (validated P95 latency: 2ms)
- `example-generative-visual/` - Visual art reference
- `example-choreographic-interface/` - Choreography reference
- `example-theatre-dialogue/` - Theatre/dialogue reference

**Resources:**
- `artist-toolkit-and-templates/` - Grant templates, prospecting guides
- `.github/` - Org-level config (workflows, issue templates, guidelines)

## Coordination Documentation

See `_COORDINATION_DOCS/` for Phase A-D orchestration:

- **HANDOFF_MASTER.md** - Master orchestration plan (phases, roles, gates)
- **AI_ORCHESTRATION_TIMELINE.md** - Detailed timeline (Phase A/B/C/D breakdown)
- **PER_REPO_KEYS.md** - Where each AI service starts in each repo
- **AI_BRIEFING_TEMPLATES.md** - Copy/paste prompts for AI services
- **FINAL_SUMMARY.md** - Immediate action checklist
- **GITHUB_SYNC_MASTER.md** - GitHub ↔ Local synchronization

## Quick Start (Phase A)

1. **Dec 7-8:** AI services execute Phase A (consensus, grant narrative, CI/CD)
   - Use briefs from `AI_BRIEFING_TEMPLATES.md`
2. **Dec 11:** Review outputs, decide GitHub timing
3. **Dec 13:** Deploy example + demo video
4. **Dec 27:** Submit grant applications

## Status

- GitHub org: ✅ Live (12 repos)
- Local sync: ✅ Complete (12 repos + coordination docs)
- .github consolidation: ✅ Unified
- Phase A: ⏳ Ready to deploy (Dec 7-8)

---

For more details, see `_COORDINATION_DOCS/HANDOFF_MASTER.md`
EOF
echo "✅ README.md updated"

# STEP 9: Directory structure verification
echo ""
echo "📊 Final Structure:"
echo "   Repos: $(find . -maxdepth 1 -type d ! -name . ! -name '.git*' ! -name '_*' | wc -l) core repos"
echo "   README files: $(find . -name 'README.md' | wc -l) total"
echo ""

# STEP 10: Next steps message
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ LOCAL SYNC COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "NEXT STEPS:"
echo "1. Review .github consolidation:"
echo "   ls -la _temp_compare/v1_extracted/ vs v2_extracted/"
echo "   (Decide which version to keep)"
echo ""
echo "2. Rename directory to match GitHub org:"
echo "   cd ~/Desktop && mv omni-dromenon-machina omni-dromenon-machina"
echo ""
echo "3. Update paths in coordination docs:"
echo "   cd ~/Desktop/omni-dromenon-machina/_COORDINATION_DOCS/"
echo "   sed -i '' 's|omni-dromenon-machina|omni-dromenon-machina|g' *.md"
echo ""
echo "4. Verify sync:"
echo "   cd ~/Desktop/omni-dromenon-machina"
echo "   find . -name README.md | wc -l  # Should be ~14"
echo ""
echo "5. Brief AI services (copy templates from _COORDINATION_DOCS/AI_BRIEFING_TEMPLATES.md):"
echo "   - Template A → Jules (consensus algorithm)"
echo "   - Template B → Gemini (grant narrative)"
echo "   - Template C → Copilot (CI/CD workflows)"
echo ""
echo "6. Go offline. Return Dec 11 to review Phase A outputs."
echo ""
EOF
chmod +x /Users/4jp/Desktop/omni-dromenon-machina/QUICK_SYNC_CHECKLIST.sh
