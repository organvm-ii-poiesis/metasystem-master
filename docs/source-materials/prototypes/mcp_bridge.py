#!/usr/bin/env python3
"""
MCP Bridge - Exposes Knowledge Graph to AI Tools

Provides MCP (Model Context Protocol) endpoints for Claude Code and other
AI tools to access the unified knowledge graph. Enables conversation
persistence and context injection.

Critical for solving the "context loss" problem.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Import knowledge graph
sys.path.insert(0, str(Path(__file__).parent))
from knowledge_graph import KnowledgeGraph


app = Flask(__name__)
CORS(app)  # Enable CORS for browser access

# Initialize knowledge graph
kg = KnowledgeGraph()

# Current conversation tracking
current_conversation_id: Optional[str] = None


# =============================================================================
# Core MCP Endpoints
# =============================================================================

@app.route('/metasystem/context/current', methods=['GET'])
def get_current_context():
    """Get current system context for AI.

    Returns context including:
    - Active projects (seen in last 24 hours)
    - Recent files (seen in last 2 hours)
    - Active conversations
    - Recent decisions
    - Clipboard context (if my--father-mother available)

    Query params:
        limit: Maximum items per category (default: 20)
        hours: Time window in hours (default: 24)
    """
    limit = int(request.args.get('limit', 20))
    hours = int(request.args.get('hours', 24))

    context = {
        'timestamp': datetime.now().isoformat(),
        'active_projects': kg.query_entities(type='project', last_seen_hours=hours, limit=limit),
        'recent_files': kg.query_entities(type='file', last_seen_hours=2, limit=limit),
        'active_conversations': kg.query_conversations(active=True, limit=limit),
        'recent_decisions': kg.query_entities(type='decision', limit=10),
        'stats': kg.get_stats()
    }

    return jsonify(context)


@app.route('/metasystem/conversation/start', methods=['POST'])
def start_conversation():
    """Start a new conversation.

    Request body:
        {
            "tool": "claude-code" | "chatgpt" | "gemini",
            "thread_id": "optional-thread-id"
        }

    Returns:
        {
            "conversation_id": "uuid",
            "started_at": "iso-timestamp"
        }
    """
    global current_conversation_id

    data = request.json
    tool = data.get('tool', 'claude-code')
    thread_id = data.get('thread_id')

    # Get thread ID from environment if not provided
    if not thread_id:
        thread_id = os.getenv('CLAUDE_THREAD_ID', 'unknown')

    import uuid
    conv_id = str(uuid.uuid4())

    conversation = {
        'id': conv_id,
        'tool': tool,
        'thread_id': thread_id,
        'started_at': datetime.now().isoformat(),
        'context': {
            'files_accessed': [],
            'decisions': [],
            'entities_created': []
        },
        'state': {}
    }

    kg.insert_conversation(conversation)
    current_conversation_id = conv_id

    return jsonify({
        'conversation_id': conv_id,
        'started_at': conversation['started_at']
    })


@app.route('/metasystem/conversation/<conv_id>', methods=['GET'])
def get_conversation(conv_id: str):
    """Get conversation by ID."""
    conv = kg.get_conversation(conv_id)

    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    return jsonify(conv)


@app.route('/metasystem/conversation/<conv_id>/resume', methods=['GET'])
def resume_conversation(conv_id: str):
    """Resume a previous conversation.

    Returns all context needed to restore conversation state:
    - Files accessed in conversation
    - Decisions made
    - Entities created
    - Recent clipboard context (if available)
    - Conversation state

    Response:
        {
            "conversation_id": "uuid",
            "tool": "claude-code",
            "started_at": "iso-timestamp",
            "files_accessed": ["path1", "path2", ...],
            "decisions": [{entity}, ...],
            "entities_created": [{entity}, ...],
            "state": {...}
        }
    """
    conv = kg.get_conversation(conv_id)

    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    # Get all files accessed
    files = conv.get('context', {}).get('files_accessed', [])

    # Get all decisions made in this conversation
    decision_rels = kg.get_relationships(conv_id, rel_type='made_decision')
    decisions = [kg.get_entity(rel['target_id']) for rel in decision_rels]

    # Get all entities created
    entity_rels = kg.get_relationships(conv_id, rel_type='created_entity')
    entities_created = [kg.get_entity(rel['target_id']) for rel in entity_rels]

    resume_data = {
        'conversation_id': conv_id,
        'tool': conv['tool'],
        'started_at': conv['started_at'],
        'last_message_at': conv['last_message_at'],
        'files_accessed': files,
        'decisions': decisions,
        'entities_created': entities_created,
        'state': conv.get('state', {}),
        'summary': conv.get('summary', '')
    }

    return jsonify(resume_data)


@app.route('/metasystem/conversation/<conv_id>/log_file', methods=['POST'])
def log_file_access(conv_id: str):
    """Log a file access in conversation.

    Request body:
        {
            "path": "/path/to/file"
        }
    """
    conv = kg.get_conversation(conv_id)

    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    data = request.json
    file_path = data.get('path')

    if not file_path:
        return jsonify({'error': 'path required'}), 400

    # Update conversation context
    context = conv.get('context', {})
    files = context.get('files_accessed', [])
    files.append({
        'path': file_path,
        'timestamp': datetime.now().isoformat()
    })
    context['files_accessed'] = files

    kg.update_conversation(conv_id, {
        'context': context,
        'last_message_at': datetime.now().isoformat()
    })

    return jsonify({'status': 'logged'})


@app.route('/metasystem/conversation/<conv_id>/log_decision', methods=['POST'])
def log_decision(conv_id: str):
    """Log an architectural decision made in conversation.

    Request body:
        {
            "decision": "Description of decision",
            "rationale": "Why this decision was made (optional)"
        }
    """
    conv = kg.get_conversation(conv_id)

    if not conv:
        return jsonify({'error': 'Conversation not found'}), 404

    data = request.json
    decision_text = data.get('decision')

    if not decision_text:
        return jsonify({'error': 'decision required'}), 400

    # Create decision entity
    import uuid
    decision = {
        'id': str(uuid.uuid4()),
        'type': 'decision',
        'name': decision_text[:100],  # Short name
        'metadata': {
            'decision': decision_text,
            'rationale': data.get('rationale', ''),
            'conversation_id': conv_id,
            'timestamp': datetime.now().isoformat()
        }
    }

    decision_id = kg.insert_entity(decision)

    # Link to conversation
    kg.add_relationship(conv_id, decision_id, 'made_decision')

    return jsonify({'decision_id': decision_id})


# =============================================================================
# Search Endpoints
# =============================================================================

@app.route('/metasystem/search', methods=['GET'])
def search():
    """Semantic search across knowledge graph.

    Query params:
        q: Search query (required)
        types: Comma-separated entity types to filter (optional)
        limit: Maximum results (default: 20)

    Response:
        {
            "query": "search query",
            "results": [{entity}, ...]
        }
    """
    query = request.args.get('q')

    if not query:
        return jsonify({'error': 'query (q) required'}), 400

    types_str = request.args.get('types', '')
    types = [t.strip() for t in types_str.split(',') if t.strip()]
    limit = int(request.args.get('limit', 20))

    results = kg.search(query, types=types if types else None, limit=limit)

    return jsonify({
        'query': query,
        'types': types if types else 'all',
        'count': len(results),
        'results': results
    })


# =============================================================================
# Project & File Endpoints
# =============================================================================

@app.route('/metasystem/projects', methods=['GET'])
def get_projects():
    """Get all discovered projects.

    Query params:
        tech: Filter by technology (e.g., 'typescript', 'python')
        limit: Maximum results (default: 100)
    """
    tech = request.args.get('tech')
    limit = int(request.args.get('limit', 100))

    projects = kg.query_entities(type='project', limit=limit)

    # Filter by technology if specified
    if tech:
        tech_lower = tech.lower()
        projects = [
            p for p in projects
            if tech_lower in json.dumps(p.get('metadata', {})).lower()
        ]

    return jsonify({
        'count': len(projects),
        'projects': projects
    })


@app.route('/metasystem/files', methods=['GET'])
def get_files():
    """Get files in directory or matching pattern.

    Query params:
        path: Directory path or file pattern (optional)
        limit: Maximum results (default: 100)
    """
    path = request.args.get('path', '')
    limit = int(request.args.get('limit', 100))

    if path:
        # Query files with path pattern
        files = kg.query_entities(type='file', path_like=f"%{path}%", limit=limit)
    else:
        files = kg.query_entities(type='file', limit=limit)

    return jsonify({
        'count': len(files),
        'files': files
    })


@app.route('/metasystem/entity/<entity_id>', methods=['GET'])
def get_entity(entity_id: str):
    """Get entity by ID."""
    entity = kg.get_entity(entity_id)

    if not entity:
        return jsonify({'error': 'Entity not found'}), 404

    return jsonify(entity)


# =============================================================================
# Agent Integration Endpoints
# =============================================================================

@app.route('/metasystem/agents/query-context', methods=['GET'])
def query_agent_context():
    """Query context for an agent before work.
    
    Returns past decisions, patterns, and files for an agent's project.
    
    Query params:
        project: Project name (required)
        scenario: Work scenario description (optional)
        hours: Look back this many hours (default: 168)
        limit: Maximum results per category (default: 20)
    
    Returns:
        {
            "status": "success",
            "past_decisions": [...],
            "recent_files": [...],
            "patterns": [...],
            "similar_work": [...],
            "timestamp": "iso-timestamp"
        }
    """
    project = request.args.get('project')
    scenario = request.args.get('scenario', '')
    hours = int(request.args.get('hours', 168))
    limit = int(request.args.get('limit', 20))
    
    if not project:
        return jsonify({'error': 'project required'}), 400
    
    try:
        # Get past decisions in this project
        all_decisions = kg.query_entities(type='decision', limit=limit * 2)
        past_decisions = [
            d for d in all_decisions
            if project.lower() in json.dumps(d).lower()
        ][:limit]
        
        # Get recent files
        all_files = kg.query_entities(type='file', limit=limit * 2)
        recent_files = [
            f for f in all_files
            if project.lower() in json.dumps(f).lower()
        ][:limit]
        
        # Extract patterns from past decisions
        patterns = []
        categories = {}
        for decision in past_decisions:
            cat = decision.get('metadata', {}).get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            if count >= 2:
                patterns.append(f"Recurring pattern: {count} decisions in '{cat}' category")
        
        # Find similar work if scenario provided
        similar_work = []
        if scenario:
            scenario_lower = scenario.lower()
            all_similar = kg.search(scenario, limit=limit)
            similar_work = [
                item for item in all_similar
                if item.get('type') == 'decision'
            ][:limit]
        
        return jsonify({
            'status': 'success',
            'project': project,
            'scenario': scenario,
            'past_decisions': past_decisions,
            'recent_files': recent_files,
            'patterns': patterns,
            'similar_work': similar_work,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/metasystem/agents/log-decision', methods=['POST'])
def log_agent_decision():
    """Log an agent decision to knowledge graph.
    
    Allows agents to log architectural decisions, implementation choices,
    and other decisions made during autonomous work.
    
    Request body:
        {
            "agent_name": "architect" | "builder" | "critic",
            "decision": "Description of decision",
            "rationale": "Why this decision was made",
            "category": "architecture" | "design" | "implementation" | "testing" | "deployment",
            "project": "project-name (optional)",
            "tags": ["tag1", "tag2"],
            "context": {"key": "value"}  # Additional context
        }
    
    Returns:
        {
            "decision_id": "uuid",
            "status": "logged",
            "timestamp": "iso-timestamp"
        }
    """
    data = request.json
    
    required_fields = ['agent_name', 'decision', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} required'}), 400
    
    import uuid
    decision_id = str(uuid.uuid4())
    
    # Create decision entity
    decision_entity = {
        'id': decision_id,
        'type': 'decision',
        'name': f"{data['agent_name']}: {data['decision'][:80]}",
        'metadata': {
            'agent_name': data['agent_name'],
            'decision': data['decision'],
            'rationale': data.get('rationale', ''),
            'category': data['category'],
            'project': data.get('project', 'unknown'),
            'tags': data.get('tags', []),
            'context': data.get('context', {}),
            'timestamp': datetime.now().isoformat()
        }
    }
    
    kg.insert_entity(decision_entity)
    
    return jsonify({
        'decision_id': decision_id,
        'status': 'logged',
        'timestamp': decision_entity['metadata']['timestamp']
    })


@app.route('/metasystem/agents/status', methods=['GET'])
def get_agent_status():
    """Get status of all agents.
    
    Aggregates:
    - Recent decisions by agent
    - Currently active projects
    - Recent activity
    """
    # Query recent decisions
    decisions = kg.query_entities(type='decision', limit=50)
    
    agent_status = {}
    for decision in decisions:
        agent = decision.get('metadata', {}).get('agent_name', 'unknown')
        if agent not in agent_status:
            agent_status[agent] = {
                'name': agent,
                'decision_count': 0,
                'recent_decisions': [],
                'categories': {}
            }
        
        agent_status[agent]['decision_count'] += 1
        agent_status[agent]['recent_decisions'].append({
            'id': decision['id'],
            'decision': decision.get('metadata', {}).get('decision', ''),
            'timestamp': decision.get('created_at')
        })
        
        cat = decision.get('metadata', {}).get('category', 'unknown')
        agent_status[agent]['categories'][cat] = agent_status[agent]['categories'].get(cat, 0) + 1
    
    return jsonify({
        'agents': agent_status,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/metasystem/context/clipboard', methods=['GET'])
def get_clipboard_context():
    """Get clipboard context for agent use.
    
    Integrates with my--father-mother to provide recent clipboard data
    that agents can reference for context-aware decisions.
    
    Query params:
        limit: Maximum clips to return (default: 20)
        search: Search query for clipboard content (optional)
    
    Returns:
        {
            "status": "success",
            "clips": [...],
            "tags": [...],
            "timestamp": "iso-timestamp"
        }
    """
    try:
        from mfm_integration import MFMIntegration
        
        mfm = MFMIntegration()
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search')
        
        if search:
            clips = mfm.search_clipboard(search, limit=limit)
        else:
            context = mfm.get_clipboard_context(limit=limit)
            return jsonify(context)
        
        return jsonify({
            'status': 'success',
            'clips': clips,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'note': 'my--father-mother may not be installed'
        }), 500


@app.route('/metasystem/context/cross-project', methods=['GET'])
def get_cross_project_context():
    """Get context from similar work across projects.
    
    Helps agents find patterns and solutions from other projects
    that might apply to the current work.
    
    Query params:
        project: Current project name (optional)
        pattern: Search pattern (optional)
        hours: Time window in hours (default: 168 = 1 week)
        limit: Maximum results (default: 20)
    
    Returns:
        {
            "similar_decisions": [...],
            "shared_patterns": [...],
            "related_files": [...],
            "timestamp": "iso-timestamp"
        }
    """
    project = request.args.get('project', '')
    pattern = request.args.get('pattern', '')
    hours = int(request.args.get('hours', 168))
    limit = int(request.args.get('limit', 20))
    
    # Search for similar decisions across all projects
    all_decisions = kg.query_entities(type='decision', limit=limit * 2)
    
    # Filter for pattern match if provided
    if pattern:
        similar = [
            d for d in all_decisions
            if pattern.lower() in json.dumps(d).lower()
        ]
    else:
        similar = all_decisions
    
    # Get decisions from other projects
    cross_project = [
        d for d in similar
        if project and d.get('metadata', {}).get('project', '') != project
    ][:limit]
    
    return jsonify({
        'similar_decisions': cross_project,
        'pattern': pattern,
        'context_project': project,
        'total_found': len(cross_project),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/metasystem/decisions/by-category', methods=['GET'])
def get_decisions_by_category():
    """Get decisions filtered by category.
    
    Query params:
        category: Decision category (architecture, design, implementation, etc.)
        project: Filter by project (optional)
        limit: Maximum results (default: 50)
    
    Returns:
        {
            "category": "...",
            "decisions": [...],
            "count": N,
            "timestamp": "iso-timestamp"
        }
    """
    category = request.args.get('category')
    project = request.args.get('project')
    limit = int(request.args.get('limit', 50))
    
    if not category:
        return jsonify({'error': 'category required'}), 400
    
    # Query decisions of this category
    all_decisions = kg.query_entities(type='decision', limit=limit * 2)
    
    filtered = [
        d for d in all_decisions
        if d.get('metadata', {}).get('category', '') == category
    ]
    
    # Further filter by project if provided
    if project:
        filtered = [
            d for d in filtered
            if d.get('metadata', {}).get('project', '') == project
        ]
    
    return jsonify({
        'category': category,
        'project': project if project else 'all',
        'decisions': filtered[:limit],
        'count': len(filtered[:limit]),
        'timestamp': datetime.now().isoformat()
    })


# =============================================================================
# Stats & Health Endpoints
# =============================================================================

@app.route('/metasystem/stats', methods=['GET'])
def get_stats():
    """Get knowledge graph statistics."""
    stats = kg.get_stats()
    return jsonify(stats)


@app.route('/metasystem/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    healthy = kg.check_integrity()

    stats = kg.get_stats()

    return jsonify({
        'status': 'healthy' if healthy else 'degraded',
        'db_integrity': healthy,
        'db_size_mb': stats['db_size_mb'],
        'total_entities': stats['total_entities'],
        'total_conversations': stats['total_conversations']
    })


# =============================================================================
# Main
# =============================================================================

def main():
    """Run MCP bridge server."""
    import argparse

    parser = argparse.ArgumentParser(description='Metasystem MCP Bridge')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print(f"🚀 Starting MCP Bridge on {args.host}:{args.port}")
    print(f"📊 Knowledge Graph: {kg.db_path}")
    print(f"")
    print(f"Context & Conversation Endpoints:")
    print(f"  GET  /metasystem/context/current")
    print(f"  POST /metasystem/conversation/start")
    print(f"  GET  /metasystem/conversation/<id>/resume")
    print(f"")
    print(f"Agent Integration Endpoints:")
    print(f"  POST /metasystem/agents/log-decision")
    print(f"  GET  /metasystem/agents/status")
    print(f"  GET  /metasystem/context/clipboard")
    print(f"  GET  /metasystem/context/cross-project")
    print(f"  GET  /metasystem/decisions/by-category")
    print(f"")
    print(f"Search & Discovery Endpoints:")
    print(f"  GET  /metasystem/search?q=<query>")
    print(f"  GET  /metasystem/projects")
    print(f"  GET  /metasystem/files")
    print(f"")
    print(f"System Endpoints:")
    print(f"  GET  /metasystem/stats")
    print(f"  GET  /metasystem/health")
    print(f"")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
