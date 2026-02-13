#!/usr/bin/env python3
"""
Metasystem Web Dashboard Server
Provides real-time visualization of orchestrator status and system health.
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from threading import Thread, Event
import time

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS

from meta_orchestrator import MetaOrchestrator
from knowledge_graph import KnowledgeGraph


# Setup logging
log_dir = Path.home() / '.metasystem' / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_dir / 'dashboard_server.log')]
)
logger = logging.getLogger('DashboardServer')

app = Flask(__name__)
CORS(app)

# Global state
orchestrator = None
kg = None
stop_event = Event()


# HTML Dashboard Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Metasystem Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #444;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-line {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 0.95em;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-indicator {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4CAF50;
            animation: pulse 2s infinite;
        }
        
        .status-indicator.offline {
            background: #f44336;
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #2d2d44;
            border: 1px solid #444;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: #00d4ff;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1);
        }
        
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #00d4ff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-content {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #3a3a52;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #aaa;
            font-size: 0.9em;
        }
        
        .metric-value {
            color: #00d4ff;
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .daemon-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .daemon-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px;
            background: rgba(0, 212, 255, 0.05);
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }
        
        .daemon-status {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4CAF50;
        }
        
        .daemon-status.running {
            background: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
        }
        
        .daemon-status.stopped {
            background: #f44336;
        }
        
        .daemon-status.disabled {
            background: #666;
        }
        
        .daemon-name {
            flex: 1;
            font-weight: 500;
        }
        
        .daemon-info {
            font-size: 0.8em;
            color: #aaa;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        button {
            padding: 8px 16px;
            background: linear-gradient(135deg, #00d4ff 0%, #0099ff 100%);
            color: #1e1e2e;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9em;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0, 212, 255, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        button.secondary {
            background: #444;
            color: #e0e0e0;
        }
        
        button.secondary:hover {
            background: #555;
            box-shadow: 0 8px 16px rgba(100, 100, 100, 0.2);
        }
        
        .last-updated {
            font-size: 0.85em;
            color: #777;
            margin-top: 10px;
            text-align: right;
        }
        
        .error {
            background: rgba(244, 67, 54, 0.1);
            border: 1px solid #f44336;
            color: #ff6b6b;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .success {
            background: rgba(76, 175, 80, 0.1);
            border: 1px solid #4CAF50;
            color: #66BB6A;
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #888;
        }
        
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid rgba(0, 212, 255, 0.2);
            border-top-color: #00d4ff;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 10px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .two-column {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        @media (max-width: 900px) {
            .two-column {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Metasystem Dashboard</h1>
            <div class="status-line">
                <div class="status-item">
                    <div class="status-indicator" id="statusIndicator"></div>
                    <span id="statusText">Initializing...</span>
                </div>
                <div class="status-item">
                    <span id="lastUpdated">Last updated: never</span>
                </div>
            </div>
        </header>

        <div id="messageContainer"></div>

        <div class="controls" style="margin-bottom: 30px;">
            <button onclick="runDiscovery()">🔍 Discover</button>
            <button onclick="runSync()">🔄 Sync</button>
            <button onclick="runHealthCheck()">💚 Health Check</button>
            <button class="secondary" onclick="location.reload()">🔄 Refresh</button>
            <button class="secondary" onclick="toggleAutoRefresh()">⏸️ Auto-Refresh</button>
        </div>

        <div class="grid">
            <!-- Orchestrator Status -->
            <div class="card">
                <h2>🎯 Orchestrator</h2>
                <div class="card-content" id="orchestratorContent">
                    <div class="loading"><span class="spinner"></span>Loading...</div>
                </div>
            </div>

            <!-- Knowledge Graph Stats -->
            <div class="card">
                <h2>📊 Knowledge Graph</h2>
                <div class="card-content" id="kgContent">
                    <div class="loading"><span class="spinner"></span>Loading...</div>
                </div>
            </div>

            <!-- System Health -->
            <div class="card">
                <h2>🏥 System Health</h2>
                <div class="card-content" id="healthContent">
                    <div class="loading"><span class="spinner"></span>Loading...</div>
                </div>
            </div>

            <!-- Daemon Status -->
            <div class="card">
                <h2>⚙️ Daemons</h2>
                <div class="card-content" id="daemonContent">
                    <div class="loading"><span class="spinner"></span>Loading...</div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="card" style="grid-column: span 1;">
                <h2>📅 Recent Activity</h2>
                <div class="card-content" id="activityContent">
                    <div class="loading"><span class="spinner"></span>Loading...</div>
                </div>
            </div>

            <!-- Quick Actions -->
            <div class="card" style="grid-column: span 1;">
                <h2>⚡ Quick Actions</h2>
                <div class="card-content">
                    <button onclick="viewLogs('meta-orchestrator')" style="width: 100%; margin-bottom: 10px;">View Orchestrator Logs</button>
                    <button class="secondary" onclick="openTerminal()" style="width: 100%;">Open Terminal</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let autoRefresh = true;
        let refreshInterval = 5000; // 5 seconds

        // Format timestamp
        function formatTime(isoString) {
            if (!isoString) return 'never';
            const date = new Date(isoString);
            const now = new Date();
            const diff = now - date;
            
            if (diff < 60000) return 'just now';
            if (diff < 3600000) return Math.floor(diff / 60000) + 'm ago';
            if (diff < 86400000) return Math.floor(diff / 3600000) + 'h ago';
            return date.toLocaleDateString();
        }

        // Update status
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                // Update indicator
                const indicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                
                if (data.running) {
                    indicator.classList.remove('offline');
                    statusText.textContent = 'System Running';
                } else {
                    indicator.classList.add('offline');
                    statusText.textContent = 'System Offline';
                }
                
                // Update last updated
                document.getElementById('lastUpdated').textContent = 
                    'Last updated: ' + new Date().toLocaleTimeString();
                
                // Update orchestrator card
                const orchestratorHtml = `
                    <div class="metric">
                        <span class="metric-label">Status</span>
                        <span class="metric-value">${data.running ? '🟢 Running' : '🔴 Offline'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Config Path</span>
                        <span class="metric-value" style="font-size: 0.9em; word-break: break-all;">${data.config_path}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Daemons</span>
                        <span class="metric-value">${Object.keys(data.daemons).length}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Discovery</span>
                        <span class="metric-value">${formatTime(data.last_discovery)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Sync</span>
                        <span class="metric-value">${formatTime(data.last_sync)}</span>
                    </div>
                `;
                document.getElementById('orchestratorContent').innerHTML = orchestratorHtml;
                
                // Update daemon list
                const daemonHtml = Object.entries(data.daemons).map(([name, daemon]) => {
                    const statusClass = daemon.enabled ? (daemon.running ? 'running' : 'stopped') : 'disabled';
                    const statusText = daemon.enabled ? (daemon.running ? 'Running' : 'Stopped') : 'Disabled';
                    const restarts = daemon.restart_count > 0 ? ` (${daemon.restart_count} restarts)` : '';
                    
                    return `
                        <div class="daemon-item">
                            <div class="daemon-status ${statusClass}"></div>
                            <div class="daemon-name">${name}</div>
                            <div class="daemon-info">${statusText}${restarts}</div>
                        </div>
                    `;
                }).join('');
                document.getElementById('daemonContent').innerHTML = daemonHtml || '<p>No daemons</p>';
                
            } catch (error) {
                console.error('Error updating status:', error);
                showMessage('Error connecting to orchestrator', 'error');
            }
        }

        // Update health
        async function updateHealth() {
            try {
                const response = await fetch('/api/health');
                const data = await response.json();
                
                if (data.status !== 'success') {
                    document.getElementById('healthContent').innerHTML = '<p>Health check skipped (ran recently)</p>';
                    return;
                }
                
                const kg = data.knowledge_graph || {};
                const disk = data.disk_space || {};
                const overall = data.overall_status || 'unknown';
                
                const healthHtml = `
                    <div class="metric">
                        <span class="metric-label">Overall Status</span>
                        <span class="metric-value">${overall.toUpperCase()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">KG Entities</span>
                        <span class="metric-value">${kg.entities || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">KG Size</span>
                        <span class="metric-value">${(kg.size_mb || 0).toFixed(2)}MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Disk Free</span>
                        <span class="metric-value">${(disk.free_gb || 0).toFixed(1)}GB / ${(disk.total_gb || 0).toFixed(1)}GB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Check</span>
                        <span class="metric-value">${formatTime(data.created_at)}</span>
                    </div>
                `;
                document.getElementById('healthContent').innerHTML = healthHtml;
                
            } catch (error) {
                console.error('Error updating health:', error);
            }
        }

        // Update KG stats
        async function updateKGStats() {
            try {
                const response = await fetch('/api/kg-stats');
                const data = await response.json();
                
                const kgHtml = `
                    <div class="metric">
                        <span class="metric-label">Total Entities</span>
                        <span class="metric-value">${data.entity_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Conversations</span>
                        <span class="metric-value">${data.conversation_count || 0}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Database Size</span>
                        <span class="metric-value">${(data.db_size_mb || 0).toFixed(2)}MB</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Indexed</span>
                        <span class="metric-value">FTS5 Ready</span>
                    </div>
                `;
                document.getElementById('kgContent').innerHTML = kgHtml;
                
            } catch (error) {
                console.error('Error updating KG stats:', error);
            }
        }

        // Update activity
        async function updateActivity() {
            try {
                const response = await fetch('/api/recent-activity');
                const data = await response.json();
                
                if (!data.events || data.events.length === 0) {
                    document.getElementById('activityContent').innerHTML = '<p>No recent activity</p>';
                    return;
                }
                
                const activityHtml = data.events.slice(0, 5).map(event => `
                    <div class="metric">
                        <span class="metric-label">${event.type}</span>
                        <span class="metric-value" style="font-size: 0.9em;">${formatTime(event.timestamp)}</span>
                    </div>
                `).join('');
                
                document.getElementById('activityContent').innerHTML = activityHtml;
                
            } catch (error) {
                console.error('Error updating activity:', error);
            }
        }

        // Run operations
        async function runDiscovery() {
            showMessage('Running discovery...', 'info');
            try {
                const response = await fetch('/api/discovery', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    showMessage(`✓ Found ${data.projects_found} projects, ${data.tools_found} tools`, 'success');
                    updateStatus();
                } else {
                    showMessage('Discovery failed: ' + (data.error || 'unknown'), 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }

        async function runSync() {
            showMessage('Running sync...', 'info');
            try {
                const response = await fetch('/api/sync', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    showMessage('✓ Sync completed', 'success');
                    updateStatus();
                } else {
                    showMessage('Sync failed: ' + (data.error || 'unknown'), 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }

        async function runHealthCheck() {
            showMessage('Running health check...', 'info');
            try {
                const response = await fetch('/api/health', { method: 'POST' });
                const data = await response.json();
                if (data.status === 'success') {
                    showMessage('✓ System healthy', 'success');
                    updateHealth();
                } else {
                    showMessage('Health check failed: ' + (data.error || 'unknown'), 'error');
                }
            } catch (error) {
                showMessage('Error: ' + error.message, 'error');
            }
        }

        function viewLogs(daemon) {
            alert('Open Terminal.app and run:\ntail -f ~/.metasystem/logs/' + daemon + '.log');
        }

        function openTerminal() {
            alert('Open Terminal.app and navigate to the metasystem-core directory.');
        }

        function toggleAutoRefresh() {
            autoRefresh = !autoRefresh;
            if (autoRefresh) {
                alert('Auto-refresh enabled');
                startAutoRefresh();
            } else {
                alert('Auto-refresh disabled');
            }
        }

        function showMessage(message, type = 'info') {
            const container = document.getElementById('messageContainer');
            const div = document.createElement('div');
            div.className = type;
            div.textContent = message;
            div.style.marginBottom = '10px';
            container.appendChild(div);
            
            if (type !== 'error') {
                setTimeout(() => div.remove(), 5000);
            }
        }

        function startAutoRefresh() {
            if (autoRefresh) {
                updateStatus();
                updateHealth();
                updateKGStats();
                updateActivity();
                setTimeout(startAutoRefresh, refreshInterval);
            }
        }

        // Initial load
        window.addEventListener('load', () => {
            updateStatus();
            updateHealth();
            updateKGStats();
            updateActivity();
            startAutoRefresh();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'r') {
                    e.preventDefault();
                    location.reload();
                }
                if (e.key === 'd') {
                    e.preventDefault();
                    runDiscovery();
                }
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve dashboard HTML."""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def api_status():
    """Get orchestrator status."""
    try:
        status = orchestrator.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET', 'POST'])
def api_health():
    """Get health check results."""
    try:
        force = request.method == 'POST'
        result = orchestrator.run_health_check(force=force)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting health: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/kg-stats')
def api_kg_stats():
    """Get knowledge graph statistics."""
    try:
        stats = kg.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting KG stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/discovery', methods=['POST'])
def api_discovery():
    """Trigger discovery."""
    try:
        result = orchestrator.trigger_discovery(force=True)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering discovery: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Trigger synchronization."""
    try:
        result = orchestrator.trigger_sync(force=True)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error triggering sync: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


@app.route('/api/recent-activity')
def api_recent_activity():
    """Get recent activity."""
    try:
        # Query KG for recent events
        events = kg.search_entities('discovery_event OR health_event OR sync_event', limit=10)
        activity = {
            'events': [
                {
                    'type': e.get('type', 'unknown'),
                    'timestamp': e.get('created_at', datetime.now().isoformat())
                }
                for e in events
            ]
        }
        return jsonify(activity)
    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify({'events': []}), 500


def main():
    """Start dashboard server."""
    global orchestrator, kg
    
    try:
        logger.info("Initializing orchestrator...")
        orchestrator = MetaOrchestrator()
        
        logger.info("Initializing knowledge graph...")
        kg = KnowledgeGraph()
        
        logger.info("Starting dashboard server on http://localhost:8888")
        app.run(host='127.0.0.1', port=8888, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        logger.info("Dashboard stopped by user")
    except Exception as e:
        logger.error(f"Error starting dashboard: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
