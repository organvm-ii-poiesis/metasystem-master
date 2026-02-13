#!/usr/bin/env python3
"""
Documentation Generator - Auto-generate system documentation from knowledge graph

This script reads entities and relationships from the knowledge graph and
generates comprehensive markdown documentation.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from knowledge_graph import KnowledgeGraph


class DocumentationGenerator:
    def __init__(self, kg: KnowledgeGraph, output_dir: str):
        self.kg = kg
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self):
        """Generate all documentation files"""
        print("📚 Generating system documentation...")

        self.generate_workspace_index()
        self.generate_decisions_log()
        self.generate_tools_index()
        self.generate_metasystem_map()
        self.generate_workflows()

        print("✅ Documentation generated successfully!")

    def generate_workspace_index(self):
        """Generate index of all projects in workspace"""
        projects = self.kg.query_entities(type='project')

        content = "# Workspace Project Index\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**Total Projects**: {len(projects)}\n\n"
        content += "---\n\n"

        # Group by tech stack
        by_tech: Dict[str, List[Any]] = {}
        for project in projects:
            tech_stack = project.get('metadata', {}).get('tech_stack', {})

            # Handle both dict and list formats, ensure backend is always a string
            if isinstance(tech_stack, dict):
                backend = str(tech_stack.get('backend', 'Unknown'))
            elif isinstance(tech_stack, list) and len(tech_stack) > 0:
                # If it's a list, join elements or take first one
                backend = ', '.join(str(t) for t in tech_stack) if tech_stack else 'Unknown'
            else:
                backend = 'Unknown'

            # Ensure backend is hashable (string)
            backend = str(backend)[:50]  # Limit length for readability

            if backend not in by_tech:
                by_tech[backend] = []
            by_tech[backend].append(project)

        # Generate sections
        for tech, projs in sorted(by_tech.items()):
            content += f"## {tech} Projects\n\n"

            for p in sorted(projs, key=lambda x: x.get('name', '')):
                name = p.get('name', 'Unknown')
                path = p.get('path', 'Unknown')
                description = p.get('metadata', {}).get('description', 'No description')

                content += f"### {name}\n\n"
                content += f"**Path**: `{path}`\n\n"
                content += f"**Description**: {description}\n\n"

                # Tech stack details
                tech_stack = p.get('metadata', {}).get('tech_stack', {})
                if tech_stack:
                    content += "**Tech Stack**:\n"
                    if isinstance(tech_stack, dict):
                        for key, value in tech_stack.items():
                            if value:
                                content += f"- {key.title()}: {value}\n"
                    elif isinstance(tech_stack, list):
                        for item in tech_stack:
                            content += f"- {item}\n"
                    content += "\n"

                content += "---\n\n"

        # Write file
        output_path = self.output_dir / "WORKSPACE-INDEX.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")

    def generate_decisions_log(self):
        """Generate log of all architectural decisions"""
        decisions = self.kg.query_entities(type='decision')

        content = "# Architectural Decisions Log\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**Total Decisions**: {len(decisions)}\n\n"
        content += "---\n\n"

        # Group by project
        by_project: Dict[str, List[Any]] = {}
        for decision in decisions:
            project = decision.get('metadata', {}).get('project', 'Global')

            if project not in by_project:
                by_project[project] = []
            by_project[project].append(decision)

        # Generate sections
        for project, decs in sorted(by_project.items()):
            content += f"## {project}\n\n"

            for d in sorted(decs, key=lambda x: x.get('created_at', ''), reverse=True):
                decision_text = d.get('metadata', {}).get('decision', d.get('name', 'Unknown'))
                rationale = d.get('metadata', {}).get('rationale', 'No rationale provided')
                category = d.get('metadata', {}).get('category', 'general')
                created = d.get('created_at', 'Unknown')

                content += f"### {decision_text}\n\n"
                content += f"**Category**: {category.title()}\n\n"
                content += f"**Date**: {created[:10] if len(created) >= 10 else created}\n\n"
                content += f"**Rationale**: {rationale}\n\n"

                # Tags
                tags = d.get('metadata', {}).get('tags', [])
                if tags:
                    content += f"**Tags**: {', '.join(tags)}\n\n"

                content += "---\n\n"

        # Write file
        output_path = self.output_dir / "DECISIONS.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")

    def generate_tools_index(self):
        """Generate index of installed tools and software"""
        tools = self.kg.query_entities(type='tool')

        content = "# Tools & Software Index\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**Total Tools**: {len(tools)}\n\n"
        content += "---\n\n"

        # Sort by name
        for tool in sorted(tools, key=lambda x: x.get('name', '')):
            name = tool.get('name', 'Unknown')
            path = tool.get('path', 'N/A')
            version = tool.get('metadata', {}).get('version', 'Unknown')
            description = tool.get('metadata', {}).get('description', 'No description')

            content += f"## {name}\n\n"
            content += f"**Version**: {version}\n\n"
            content += f"**Path**: `{path}`\n\n"
            content += f"**Description**: {description}\n\n"
            content += "---\n\n"

        # Write file
        output_path = self.output_dir / "TOOLS-INDEX.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")

    def generate_metasystem_map(self):
        """Generate complete system overview map"""
        projects = self.kg.query_entities(type='project')
        decisions = self.kg.query_entities(type='decision')
        conversations = self.kg.get_recent_conversations(limit=10)

        content = "# Metasystem Map\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "Complete overview of the 4jp metasystem.\n\n"
        content += "---\n\n"

        # Statistics
        content += "## System Statistics\n\n"
        content += f"- **Projects**: {len(projects)}\n"
        content += f"- **Decisions Logged**: {len(decisions)}\n"
        content += f"- **Recent Conversations**: {len(conversations)}\n\n"
        content += "---\n\n"

        # Key Components
        content += "## Key Components\n\n"

        key_projects = ['metasystem-core', 'omni-dromenon-machina', 'my--father-mother']
        for project_name in key_projects:
            matches = [p for p in projects if p.get('name') == project_name]
            if matches:
                p = matches[0]
                content += f"### {p.get('name')}\n\n"
                content += f"**Path**: `{p.get('path')}`\n\n"
                content += f"**Description**: {p.get('metadata', {}).get('description', 'N/A')}\n\n"

        content += "---\n\n"

        # Recent Activity
        content += "## Recent Activity\n\n"

        if conversations:
            content += "### Recent Conversations\n\n"
            for conv in conversations[:5]:
                tool = conv.get('tool', 'Unknown')
                started = conv.get('started_at', 'Unknown')
                context = conv.get('context', {})
                files = len(context.get('files_accessed', []))
                decs = len(context.get('decisions', []))

                content += f"- **{tool}** session started {started[:16] if len(started) >= 16 else started}\n"
                content += f"  - Files accessed: {files}\n"
                content += f"  - Decisions made: {decs}\n\n"

        # Write file
        output_path = self.output_dir / "METASYSTEM-MAP.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")

    def generate_workflows(self):
        """Generate common workflows documentation"""
        content = "# Common Workflows\n\n"
        content += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += "Frequently used workflows and commands.\n\n"
        content += "---\n\n"

        # Development Workflow
        content += "## Development Workflow\n\n"
        content += "### Starting New Work\n\n"
        content += "```bash\n"
        content += "# Start conversation tracking\n"
        content += "cd /Users/4jp/Workspace/metasystem-core\n"
        content += "source .venv/bin/activate\n"
        content += "python3 context_manager.py start\n"
        content += "```\n\n"

        content += "### Resuming Previous Work\n\n"
        content += "```bash\n"
        content += "# List recent conversations\n"
        content += "python3 context_manager.py recent\n\n"
        content += "# Resume specific conversation\n"
        content += "python3 context_manager.py resume --conv-id=<ID>\n"
        content += "```\n\n"

        # File Organization
        content += "## File Organization\n\n"
        content += "### Manual Scan\n\n"
        content += "```bash\n"
        content += "# Scan downloads folder\n"
        content += "python3 sorting_daemon.py scan\n\n"
        content += "# Dry run (test without moving files)\n"
        content += "python3 sorting_daemon.py test\n"
        content += "```\n\n"

        # Knowledge Graph Queries
        content += "## Knowledge Graph Queries\n\n"
        content += "### Search Decisions\n\n"
        content += "```bash\n"
        content += "# Search for decisions\n"
        content += "python3 knowledge_graph.py search --query=\"architecture\" --type=decision\n\n"
        content += "# Find recent file changes\n"
        content += "python3 knowledge_graph.py query --type=file --hours=24\n"
        content += "```\n\n"

        # Documentation Generation
        content += "## Documentation\n\n"
        content += "### Regenerate System Docs\n\n"
        content += "```bash\n"
        content += "# Generate all documentation\n"
        content += "python3 documentation_generator.py --all\n\n"
        content += "# Generate specific doc\n"
        content += "python3 documentation_generator.py --workspace-index\n"
        content += "```\n\n"

        # Write file
        output_path = self.output_dir / "WORKFLOWS.md"
        output_path.write_text(content)
        print(f"  ✓ Created {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate system documentation from knowledge graph')
    parser.add_argument('--output-dir', default='/Users/4jp/Documents',
                        help='Output directory for documentation')
    parser.add_argument('--all', action='store_true',
                        help='Generate all documentation files')
    parser.add_argument('--workspace-index', action='store_true',
                        help='Generate workspace index')
    parser.add_argument('--decisions', action='store_true',
                        help='Generate decisions log')
    parser.add_argument('--tools', action='store_true',
                        help='Generate tools index')
    parser.add_argument('--metasystem-map', action='store_true',
                        help='Generate metasystem map')
    parser.add_argument('--workflows', action='store_true',
                        help='Generate workflows documentation')

    args = parser.parse_args()

    kg = KnowledgeGraph()
    generator = DocumentationGenerator(kg, args.output_dir)

    if args.all or (not any([args.workspace_index, args.decisions, args.tools,
                             args.metasystem_map, args.workflows])):
        generator.generate_all()
    else:
        if args.workspace_index:
            generator.generate_workspace_index()
        if args.decisions:
            generator.generate_decisions_log()
        if args.tools:
            generator.generate_tools_index()
        if args.metasystem_map:
            generator.generate_metasystem_map()
        if args.workflows:
            generator.generate_workflows()


if __name__ == '__main__':
    main()
