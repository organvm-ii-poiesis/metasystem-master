/**
 * Omni-Performative Engine — Consensus Server
 * 
 * Real-time WebSocket server that aggregates audience inputs
 * and broadcasts collective state to synthesis engines via OSC.
 */

import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { v4 as uuidv4 } from 'uuid';
import 'dotenv/config';

import {
  ClientToServerEvents,
  ServerToClientEvents,
  InterServerEvents,
  SocketData,
  ClientSession,
  TimestampedInput,
  ConsensusState,
  PerformerOverrides,
  ServerConfig,
  ServerMetrics,
  ConsensusMode,
  DEFAULTS,
  PARAMETER_NAMES,
} from './types.js';

import { ConsensusEngine, applyOverrides, validateInput } from './consensus.js';
import { OscSender } from './osc.js';

// ============================================================================
// Configuration
// ============================================================================

const config: ServerConfig = {
  port: parseInt(process.env.PORT || '3001', 10),
  consensusMode: (process.env.CONSENSUS_MODE || 'arithmetic') as ConsensusMode,
  consensusInterval: parseInt(process.env.CONSENSUS_INTERVAL || '50', 10), // ms
  osc: {
    host: process.env.OSC_HOST || '127.0.0.1',
    port: parseInt(process.env.OSC_PORT || '57120', 10),
    enabled: process.env.OSC_ENABLED !== 'false',
  },
  maxClients: parseInt(process.env.MAX_CLIENTS || '1000', 10),
};

// ============================================================================
// State
// ============================================================================

const clients = new Map<string, ClientSession>();
const inputs = new Map<string, TimestampedInput>();

let currentConsensus: ConsensusState = { ...DEFAULTS.consensus };

const overrides: PerformerOverrides = {
  intensity: { ...DEFAULTS.override },
  density: { ...DEFAULTS.override },
  pitch: { ...DEFAULTS.override },
  masterMute: false,
  masterBypass: false,
};

const metrics: ServerMetrics = {
  startedAt: Date.now(),
  totalConnections: 0,
  totalInputsReceived: 0,
  consensusComputations: 0,
  oscMessagesSent: 0,
  averageLatency: 0,
};

// ============================================================================
// Initialize Services
// ============================================================================

const consensusEngine = new ConsensusEngine(config.consensusMode);
const oscSender = new OscSender(config.osc);

// ============================================================================
// Express + Socket.io Setup
// ============================================================================

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);

const io = new Server<
  ClientToServerEvents,
  ServerToClientEvents,
  InterServerEvents,
  SocketData
>(httpServer, {
  cors: {
    origin: process.env.CLIENT_ORIGIN || 'http://localhost:3000',
    methods: ['GET', 'POST'],
  },
  pingInterval: 10000,
  pingTimeout: 5000,
});

// ============================================================================
// REST Endpoints (for monitoring and admin)
// ============================================================================

app.get('/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Date.now() - metrics.startedAt,
    clients: clients.size,
  });
});

app.get('/state', (_req, res) => {
  res.json({
    consensus: currentConsensus,
    overrides,
    participantCount: clients.size,
  });
});

app.get('/metrics', (_req, res) => {
  res.json({
    ...metrics,
    currentClients: clients.size,
    uptime: Date.now() - metrics.startedAt,
    osc: oscSender.getStats(),
  });
});

// ============================================================================
// Socket.io Connection Handler
// ============================================================================

io.on('connection', (socket) => {
  // Check capacity
  if (clients.size >= config.maxClients) {
    socket.emit('error', 'Server at capacity. Please try again later.');
    socket.disconnect(true);
    return;
  }
  
  // Create session
  const clientId = uuidv4();
  const connectedAt = Date.now();
  
  const session: ClientSession = {
    id: clientId,
    socketId: socket.id,
    connectedAt,
    lastInput: null,
    inputCount: 0,
    isPerformer: false,
  };
  
  clients.set(clientId, session);
  socket.data = { clientId, connectedAt, isPerformer: false };
  
  metrics.totalConnections++;
  
  console.log(`[WS] Client connected: ${clientId} (${clients.size} total)`);
  
  // Welcome message
  socket.emit('client:welcome', {
    id: clientId,
    participantCount: clients.size,
  });
  
  // Broadcast updated count
  io.emit('client:count', clients.size);
  
  // Send current state
  socket.emit('state:consensus', currentConsensus);
  socket.emit('state:overrides', overrides);
  
  // --------------------------------------------------------------------------
  // Input Handler
  // --------------------------------------------------------------------------
  
  socket.on('input:update', (rawInput) => {
    const session = clients.get(clientId);
    if (!session) return;
    
    // Validate and sanitize
    const input = validateInput(rawInput);
    
    // Create timestamped input
    const timestamped: TimestampedInput = {
      ...input,
      clientId,
      timestamp: Date.now(),
      connectionDuration: Date.now() - connectedAt,
    };
    
    // Store
    inputs.set(clientId, timestamped);
    session.lastInput = timestamped;
    session.inputCount++;
    
    metrics.totalInputsReceived++;
  });
  
  // --------------------------------------------------------------------------
  // Performer Override Handler
  // --------------------------------------------------------------------------
  
  socket.on('performer:override', (update) => {
    // Only allow if authenticated as performer
    if (!socket.data.isPerformer) {
      socket.emit('error', 'Not authorized as performer');
      return;
    }
    
    // Apply updates
    if (update.masterMute !== undefined) {
      overrides.masterMute = update.masterMute;
      oscSender.sendMute(update.masterMute);
    }
    
    if (update.masterBypass !== undefined) {
      overrides.masterBypass = update.masterBypass;
    }
    
    for (const param of PARAMETER_NAMES) {
      if (update[param]) {
        Object.assign(overrides[param], update[param]);
        
        if (update[param].locked !== undefined || update[param].lockedValue !== undefined) {
          oscSender.sendOverride(
            param,
            overrides[param].lockedValue ?? currentConsensus[param],
            overrides[param].locked
          );
        }
      }
    }
    
    // Broadcast override state
    io.emit('state:overrides', overrides);
  });
  
  // --------------------------------------------------------------------------
  // Performer Authentication
  // --------------------------------------------------------------------------
  
  socket.on('performer:auth', (token) => {
    // Simple token auth (replace with proper auth in production)
    const validToken = process.env.PERFORMER_TOKEN || 'performer-secret';
    
    if (token === validToken) { // allow-secret
      socket.data.isPerformer = true;
      const session = clients.get(clientId);
      if (session) session.isPerformer = true;
      console.log(`[WS] Performer authenticated: ${clientId}`);
    } else {
      socket.emit('error', 'Invalid performer token');
    }
  });
  
  // --------------------------------------------------------------------------
  // Disconnect Handler
  // --------------------------------------------------------------------------
  
  socket.on('disconnect', (reason) => {
    clients.delete(clientId);
    inputs.delete(clientId);
    
    console.log(`[WS] Client disconnected: ${clientId} (${reason})`);
    
    // Broadcast updated count
    io.emit('client:count', clients.size);
  });
});

// ============================================================================
// Consensus Loop
// ============================================================================

setInterval(() => {
  // Collect all current inputs
  const allInputs = Array.from(inputs.values());
  
  // Compute raw consensus
  const rawConsensus = consensusEngine.compute(allInputs);
  
  // Apply performer overrides
  currentConsensus = applyOverrides(rawConsensus, overrides);
  
  metrics.consensusComputations++;
  
  // Send to SuperCollider
  if (!overrides.masterMute) {
    oscSender.send(currentConsensus);
    metrics.oscMessagesSent++;
  }
  
  // Broadcast to all clients
  io.emit('state:consensus', currentConsensus);
  
}, config.consensusInterval);

// Heartbeat to SuperCollider (every 5s)
setInterval(() => {
  oscSender.sendHeartbeat();
}, 5000);

// ============================================================================
// Start Server
// ============================================================================

httpServer.listen(config.port, () => {
  console.log('');
  console.log('╔══════════════════════════════════════════════════════════════╗');
  console.log('║     OMNI-PERFORMATIVE ENGINE — Consensus Server              ║');
  console.log('╠══════════════════════════════════════════════════════════════╣');
  console.log(`║  WebSocket:  ws://localhost:${config.port}                          ║`);
  console.log(`║  REST API:   http://localhost:${config.port}                        ║`);
  console.log(`║  OSC Output: ${config.osc.host}:${config.osc.port} ${config.osc.enabled ? '(enabled)' : '(disabled)'}             ║`);
  console.log(`║  Consensus:  ${config.consensusMode} @ ${config.consensusInterval}ms                        ║`);
  console.log('╠══════════════════════════════════════════════════════════════╣');
  console.log('║  Endpoints:                                                  ║');
  console.log('║    GET /health   - Server health check                       ║');
  console.log('║    GET /state    - Current consensus + overrides             ║');
  console.log('║    GET /metrics  - Runtime statistics                        ║');
  console.log('╚══════════════════════════════════════════════════════════════╝');
  console.log('');
});

// ============================================================================
// Graceful Shutdown
// ============================================================================

process.on('SIGINT', () => {
  console.log('\n[Server] Shutting down...');
  oscSender.close();
  io.close();
  httpServer.close(() => {
    console.log('[Server] Closed.');
    process.exit(0);
  });
});
