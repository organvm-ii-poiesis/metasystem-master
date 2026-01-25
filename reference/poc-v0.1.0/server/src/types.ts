/**
 * Omni-Performative Engine — Type Definitions
 * 
 * Core data structures for audience input, consensus, and system state.
 */

// ============================================================================
// Audience Input Types
// ============================================================================

/**
 * Raw input from a single audience member.
 * All values normalized to 0.0 - 1.0 range.
 */
export interface AudienceInput {
  intensity: number;  // Overall energy/volume
  density: number;    // Rhythmic/textural complexity
  pitch: number;      // Harmonic center
}

/**
 * Extended input with metadata for weighting and analysis.
 */
export interface TimestampedInput extends AudienceInput {
  clientId: string;
  timestamp: number;        // Unix timestamp ms
  connectionDuration: number; // ms since connection
}

// ============================================================================
// Consensus Types
// ============================================================================

/**
 * Aggregation strategies for combining audience inputs.
 */
export type ConsensusMode = 
  | 'arithmetic'   // Simple average
  | 'weighted'     // Duration-weighted average
  | 'median'       // Median (robust to outliers)
  | 'mode';        // Cluster-based mode selection

/**
 * Result of consensus computation.
 */
export interface ConsensusState extends AudienceInput {
  participantCount: number;
  computedAt: number;       // Unix timestamp ms
  mode: ConsensusMode;
  variance: {               // Per-parameter variance (measure of agreement)
    intensity: number;
    density: number;
    pitch: number;
  };
}

// ============================================================================
// Performer Override Types
// ============================================================================

/**
 * Per-parameter override configuration.
 */
export interface ParameterOverride {
  locked: boolean;          // If true, ignore audience input
  lockedValue?: number;     // Value to use when locked
  bias: number;             // Offset added to consensus (-0.5 to +0.5)
  rangeMin: number;         // Minimum allowed value (0.0 - 1.0)
  rangeMax: number;         // Maximum allowed value (0.0 - 1.0)
}

/**
 * Complete performer override state.
 */
export interface PerformerOverrides {
  intensity: ParameterOverride;
  density: ParameterOverride;
  pitch: ParameterOverride;
  masterMute: boolean;      // Emergency silence
  masterBypass: boolean;    // Ignore all audience input
}

// ============================================================================
// Client Session Types
// ============================================================================

/**
 * Connected client session.
 */
export interface ClientSession {
  id: string;
  socketId: string;
  connectedAt: number;
  lastInput: TimestampedInput | null;
  inputCount: number;
  isPerformer: boolean;
}

// ============================================================================
// OSC Types
// ============================================================================

/**
 * OSC message for SuperCollider.
 */
export interface OscMessage {
  address: string;
  args: (number | string)[];
}

/**
 * OSC configuration.
 */
export interface OscConfig {
  host: string;
  port: number;
  enabled: boolean;
}

// ============================================================================
// Server State Types
// ============================================================================

/**
 * Complete server state snapshot.
 */
export interface ServerState {
  clients: Map<string, ClientSession>;
  currentConsensus: ConsensusState;
  overrides: PerformerOverrides;
  config: ServerConfig;
  metrics: ServerMetrics;
}

/**
 * Server configuration.
 */
export interface ServerConfig {
  port: number;
  consensusMode: ConsensusMode;
  consensusInterval: number;  // ms between consensus computations
  osc: OscConfig;
  maxClients: number;
}

/**
 * Runtime metrics for monitoring.
 */
export interface ServerMetrics {
  startedAt: number;
  totalConnections: number;
  totalInputsReceived: number;
  consensusComputations: number;
  oscMessagesSent: number;
  averageLatency: number;     // ms, rolling average
}

// ============================================================================
// Socket.io Event Types
// ============================================================================

/**
 * Events emitted by clients.
 */
export interface ClientToServerEvents {
  'input:update': (input: AudienceInput) => void;
  'performer:override': (overrides: Partial<PerformerOverrides>) => void;
  'performer:auth': (token: string) => void; // allow-secret
}

/**
 * Events emitted by server.
 */
export interface ServerToClientEvents {
  'state:consensus': (state: ConsensusState) => void;
  'state:overrides': (overrides: PerformerOverrides) => void;
  'client:welcome': (session: { id: string; participantCount: number }) => void;
  'client:count': (count: number) => void;
  'error': (message: string) => void;
}

/**
 * Inter-server events (for future clustering).
 */
export interface InterServerEvents {
  ping: () => void;
}

/**
 * Socket data attached to each connection.
 */
export interface SocketData {
  clientId: string;
  connectedAt: number;
  isPerformer: boolean;
}

// ============================================================================
// Utility Types
// ============================================================================

/**
 * Parameter names for iteration.
 */
export type ParameterName = 'intensity' | 'density' | 'pitch';

export const PARAMETER_NAMES: ParameterName[] = ['intensity', 'density', 'pitch'];

/**
 * Default values.
 */
export const DEFAULTS = {
  input: {
    intensity: 0.5,
    density: 0.5,
    pitch: 0.5,
  } as AudienceInput,
  
  override: {
    locked: false,
    bias: 0,
    rangeMin: 0,
    rangeMax: 1,
  } as ParameterOverride,
  
  consensus: {
    intensity: 0.5,
    density: 0.5,
    pitch: 0.5,
    participantCount: 0,
    computedAt: 0,
    mode: 'arithmetic' as ConsensusMode,
    variance: { intensity: 0, density: 0, pitch: 0 },
  } as ConsensusState,
} as const;
