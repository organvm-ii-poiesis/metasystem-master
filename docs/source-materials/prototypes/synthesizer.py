#!/usr/bin/env python3
"""
Synthesizer Agent - Auto-Documentation Generation

Automatically generates documentation from knowledge graph data:
- System overview documents
- Project catalogs
- Decision logs
- Workflow guides
- Architecture diagrams (mermaid)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from documentation_generator import DocumentationGenerator
from knowledge_graph import KnowledgeGraph


class SynthesizerAgent:
    """Autonomous documentation synthesis agent."""

    def __init__(self, kg: KnowledgeGraph = None):
        self.kg = kg or KnowledgeGraph()
        self.output_dir = Path.home() / "Documents"

    def generate_all_docs(self) -> Dict[str, Any]:
        """Generate all documentation.

        Returns:
            Report dict with generated files
        """
        print("📚 Synthesizing documentation from knowledge graph...\n")

        generator = DocumentationGenerator(self.kg, str(self.output_dir))
        generator.generate_all()

        # Additional documentation
        self._generate_architecture_diagram()
        self._generate_quick_start_guide()

        report = {
            'timestamp': datetime.now().isoformat(),
            'output_dir': str(self.output_dir),
            'files_generated': [
                'WORKSPACE-INDEX.md',
                'DECISIONS.md',
                'TOOLS-INDEX.md',
                'METASYSTEM-MAP.md',
                'WORKFLOWS.md',
                'ARCHITECTURE.md',
                'QUICK-START.md'
            ]
        }

        print(f"\n✅ Documentation generated in {self.output_dir}")
        print(f"   {len(report['files_generated'])} files created")

        return report

    def _generate_architecture_diagram(self):
        """Generate system architecture diagram in mermaid format."""
        content = "# System Architecture\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "## Component Diagram\n\n"
        content += "```mermaid\n"
        content += "graph TB\n"
        content += "    subgraph User[\"User Interface\"]\n"
        content += "        CLI[Claude Code CLI]\n"
        content += "        ChatGPT[ChatGPT]\n"
        content += "        Gemini[Gemini]\n"
        content += "    end\n\n"

        content += "    subgraph Core[\"Metasystem Core\"]\n"
        content += "        KG[Knowledge Graph<br/>SQLite + FTS5]\n"
        content += "        CM[Context Manager<br/>Conversation Persistence]\n"
        content += "        SD[Sorting Daemon<br/>File Organization]\n"
        content += "        SE[Sync Engine<br/>Multi-Machine Sync]\n"
        content += "    end\n\n"

        content += "    subgraph Agents[\"Autonomous Agents\"]\n"
        content += "        Maintainer[Maintainer<br/>Health Checks]\n"
        content += "        Cataloger[Cataloger<br/>Discovery]\n"
        content += "        Synthesizer[Synthesizer<br/>Auto-Docs]\n"
        content += "    end\n\n"

        content += "    subgraph Orchestrator[\"Omni-Dromenon-Machina\"]\n"
        content += "        NW[NightWatchman<br/>Autonomous Patrol]\n"
        content += "        ARCH[ARCHITECT<br/>Claude]\n"
        content += "        BUILD[BUILDER<br/>GPT-4o]\n"
        content += "        CRITIC[CRITIC<br/>Gemini]\n"
        content += "    end\n\n"

        content += "    subgraph Storage[\"Storage\"]\n"
        content += "        Local[Local<br/>~/.metasystem]\n"
        content += "        iCloud[iCloud Drive]\n"
        content += "        External[External Drive]\n"
        content += "    end\n\n"

        content += "    CLI --> CM\n"
        content += "    ChatGPT --> CM\n"
        content += "    Gemini --> CM\n\n"

        content += "    CM --> KG\n"
        content += "    SD --> KG\n"
        content += "    SE --> KG\n\n"

        content += "    Maintainer --> KG\n"
        content += "    Cataloger --> KG\n"
        content += "    Synthesizer --> KG\n\n"

        content += "    NW --> KG\n"
        content += "    NW --> ARCH\n"
        content += "    NW --> CRITIC\n"
        content += "    ARCH --> KG\n"
        content += "    BUILD --> KG\n\n"

        content += "    KG --> Local\n"
        content += "    SE --> iCloud\n"
        content += "    SE --> External\n"
        content += "```\n\n"

        content += "## Data Flow\n\n"
        content += "```mermaid\n"
        content += "sequenceDiagram\n"
        content += "    participant User\n"
        content += "    participant CM as Context Manager\n"
        content += "    participant KG as Knowledge Graph\n"
        content += "    participant NW as NightWatchman\n"
        content += "    participant Agent as ARCHITECT\n\n"

        content += "    User->>CM: Start conversation\n"
        content += "    CM->>KG: Log conversation start\n"
        content += "    User->>CM: Perform work\n"
        content += "    CM->>KG: Log files accessed\n"
        content += "    CM->>KG: Log decisions made\n"
        content += "    NW->>KG: Query past decisions\n"
        content += "    KG-->>NW: Return context\n"
        content += "    NW->>Agent: Dispatch with context\n"
        content += "    Agent->>KG: Log new decision\n"
        content += "    User->>CM: Resume conversation\n"
        content += "    CM->>KG: Retrieve context\n"
        content += "    KG-->>CM: Full conversation state\n"
        content += "```\n\n"

        # Write file
        output_path = self.output_dir / "ARCHITECTURE.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")

    def _generate_quick_start_guide(self):
        """Generate quick start guide."""
        content = "# Quick Start Guide\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "Get started with the metasystem in 5 minutes!\n\n"
        content += "---\n\n"

        content += "## Prerequisites\n\n"
        content += "- macOS (tested on Sonoma/Sequoia)\n"
        content += "- Python 3.10+\n"
        content += "- iCloud Drive enabled (optional for sync)\n\n"

        content += "## Setup\n\n"
        content += "### 1. Install Dependencies\n\n"
        content += "```bash\n"
        content += "cd /Users/4jp/Workspace/metasystem-core\n"
        content += "python3 -m venv .venv\n"
        content += "source .venv/bin/activate\n"
        content += "pip install -r requirements.txt\n"
        content += "```\n\n"

        content += "### 2. Initialize Knowledge Graph\n\n"
        content += "```bash\n"
        content += "# Discovery scan (finds all projects)\n"
        content += "python3 discovery_engine.py discover\n"
        content += "```\n\n"

        content += "### 3. Start Background Services\n\n"
        content += "```bash\n"
        content += "# Load LaunchAgents\n"
        content += "launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist\n"
        content += "launchctl load ~/Library/LaunchAgents/com.metasystem.sync-daemon.plist\n"
        content += "```\n\n"

        content += "## Daily Workflow\n\n"

        content += "### Start New Work Session\n\n"
        content += "```bash\n"
        content += "cd /Users/4jp/Workspace/metasystem-core\n"
        content += "source .venv/bin/activate\n\n"
        content += "# Start conversation tracking\n"
        content += "python3 context_manager.py start\n"
        content += "```\n\n"

        content += "### Resume Previous Session\n\n"
        content += "```bash\n"
        content += "# List recent conversations\n"
        content += "python3 context_manager.py recent\n\n"
        content += "# Resume specific conversation\n"
        content += "python3 context_manager.py resume --conv-id=<ID>\n"
        content += "```\n\n"

        content += "### Search Past Work\n\n"
        content += "```bash\n"
        content += "# Search decisions\n"
        content += "python3 context_manager.py search --query=\"architecture\"\n\n"
        content += "# Search knowledge graph\n"
        content += "python3 knowledge_graph.py search --query=\"typescript\" --type=project\n"
        content += "```\n\n"

        content += "## Maintenance\n\n"

        content += "### Health Checks\n\n"
        content += "```bash\n"
        content += "# Run health check\n"
        content += "python3 agents/maintainer.py\n\n"
        content += "# Check only (no auto-repair)\n"
        content += "python3 agents/maintainer.py --no-repair\n"
        content += "```\n\n"

        content += "### Manual Sync\n\n"
        content += "```bash\n"
        content += "# Check sync status\n"
        content += "python3 sync_engine.py status\n\n"
        content += "# Manual sync\n"
        content += "python3 sync_engine.py sync\n"
        content += "```\n\n"

        content += "### Update Documentation\n\n"
        content += "```bash\n"
        content += "# Regenerate all docs\n"
        content += "python3 documentation_generator.py --all\n\n"
        content += "# Or use synthesizer agent\n"
        content += "python3 agents/synthesizer.py generate\n"
        content += "```\n\n"

        content += "## Troubleshooting\n\n"

        content += "### Sorting Daemon Not Running\n\n"
        content += "```bash\n"
        content += "# Check status\n"
        content += "launchctl list | grep metasystem\n\n"
        content += "# Restart\n"
        content += "launchctl unload ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist\n"
        content += "launchctl load ~/Library/LaunchAgents/com.metasystem.sorting-daemon.plist\n"
        content += "```\n\n"

        content += "### Database Issues\n\n"
        content += "```bash\n"
        content += "# Verify integrity\n"
        content += "python3 sync_engine.py verify\n\n"
        content += "# Health check with auto-repair\n"
        content += "python3 agents/maintainer.py\n"
        content += "```\n\n"

        content += "### Context Not Persisting\n\n"
        content += "```bash\n"
        content += "# Check conversation was created\n"
        content += "python3 context_manager.py recent\n\n"
        content += "# Manually log decision\n"
        content += "python3 context_manager.py log-decision \\\n"
        content += "  --decision=\"Your decision\" \\\n"
        content += "  --rationale=\"Your rationale\"\n"
        content += "```\n\n"

        content += "## Next Steps\n\n"
        content += "- Read `ARCHITECTURE.md` for system overview\n"
        content += "- Browse `WORKSPACE-INDEX.md` for project catalog\n"
        content += "- Review `DECISIONS.md` for architectural decisions\n"
        content += "- Check `WORKFLOWS.md` for common workflows\n\n"

        # Write file
        output_path = self.output_dir / "QUICK-START.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Auto-documentation synthesis')
    parser.add_argument('command', choices=['generate'],
                        help='Generate documentation')
    parser.add_argument('--output-dir', type=str,
                        help='Output directory (default: ~/Documents)')

    args = parser.parse_args()

    synthesizer = SynthesizerAgent()

    if args.output_dir:
        synthesizer.output_dir = Path(args.output_dir)

    if args.command == 'generate':
        synthesizer.generate_all_docs()


if __name__ == '__main__':
    main()
