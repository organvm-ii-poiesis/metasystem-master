/**
 * Omni-Performative Engine — OSC Module
 * 
 * Handles communication with SuperCollider via Open Sound Control protocol.
 * Sends consensus state as OSC messages for real-time audio synthesis.
 */

import { Client as OscClient } from 'node-osc';
import { ConsensusState, OscConfig, PARAMETER_NAMES } from './types.js';

// ============================================================================
// OSC Sender
// ============================================================================

export class OscSender {
  private client: OscClient | null = null;
  private config: OscConfig;
  private messageCount = 0;
  private lastSendTime = 0;
  
  constructor(config: OscConfig) {
    this.config = config;
    
    if (config.enabled) {
      this.connect();
    }
  }
  
  /**
   * Establish OSC connection.
   */
  private connect(): void {
    try {
      this.client = new OscClient(this.config.host, this.config.port);
      console.log(`[OSC] Connected to ${this.config.host}:${this.config.port}`);
    } catch (error) {
      console.error('[OSC] Connection failed:', error);
      this.client = null;
    }
  }
  
  /**
   * Send consensus state to SuperCollider.
   * 
   * Sends individual messages per parameter for fine-grained control,
   * plus a bundled message with all parameters.
   */
  send(consensus: ConsensusState): void {
    if (!this.client || !this.config.enabled) return;
    
    const now = Date.now();
    
    try {
      // Individual parameter messages
      // Address format: /ope/<parameter>
      for (const param of PARAMETER_NAMES) {
        this.client.send(`/ope/${param}`, consensus[param]);
      }
      
      // Bundled message with all parameters + metadata
      // Address: /ope/state
      // Args: [intensity, density, pitch, participantCount, variance_mean]
      const avgVariance = (
        consensus.variance.intensity +
        consensus.variance.density +
        consensus.variance.pitch
      ) / 3;
      
      this.client.send(
        '/ope/state',
        consensus.intensity,
        consensus.density,
        consensus.pitch,
        consensus.participantCount,
        avgVariance
      );
      
      // Participant count (useful for scaling effects)
      this.client.send('/ope/participants', consensus.participantCount);
      
      this.messageCount++;
      this.lastSendTime = now;
      
    } catch (error) {
      console.error('[OSC] Send error:', error);
    }
  }
  
  /**
   * Send performer override notification.
   */
  sendOverride(param: string, value: number, locked: boolean): void {
    if (!this.client || !this.config.enabled) return;
    
    try {
      this.client.send(`/ope/override/${param}`, value, locked ? 1 : 0);
    } catch (error) {
      console.error('[OSC] Override send error:', error);
    }
  }
  
  /**
   * Send emergency mute.
   */
  sendMute(muted: boolean): void {
    if (!this.client || !this.config.enabled) return;
    
    try {
      this.client.send('/ope/mute', muted ? 1 : 0);
    } catch (error) {
      console.error('[OSC] Mute send error:', error);
    }
  }
  
  /**
   * Send heartbeat/ping for connection monitoring.
   */
  sendHeartbeat(): void {
    if (!this.client || !this.config.enabled) return;
    
    try {
      this.client.send('/ope/heartbeat', Date.now());
    } catch (error) {
      // Silent fail on heartbeat
    }
  }
  
  /**
   * Get statistics.
   */
  getStats(): { messageCount: number; lastSendTime: number } {
    return {
      messageCount: this.messageCount,
      lastSendTime: this.lastSendTime,
    };
  }
  
  /**
   * Close connection.
   */
  close(): void {
    if (this.client) {
      this.client.close();
      this.client = null;
      console.log('[OSC] Connection closed');
    }
  }
  
  /**
   * Update configuration and reconnect if needed.
   */
  updateConfig(config: Partial<OscConfig>): void {
    const wasEnabled = this.config.enabled;
    const hostChanged = config.host && config.host !== this.config.host;
    const portChanged = config.port && config.port !== this.config.port;
    
    this.config = { ...this.config, ...config };
    
    // Reconnect if parameters changed
    if (this.config.enabled && (hostChanged || portChanged || !wasEnabled)) {
      this.close();
      this.connect();
    } else if (!this.config.enabled && wasEnabled) {
      this.close();
    }
  }
}

// ============================================================================
// OSC Address Reference
// ============================================================================

/**
 * OSC Address Schema for SuperCollider:
 * 
 * /ope/intensity      float (0-1)     Individual parameter
 * /ope/density        float (0-1)     Individual parameter  
 * /ope/pitch          float (0-1)     Individual parameter
 * /ope/state          float[5]        [intensity, density, pitch, participants, variance]
 * /ope/participants   int             Current participant count
 * /ope/override/<p>   float, int      Value and lock state for parameter
 * /ope/mute           int (0/1)       Emergency mute state
 * /ope/heartbeat      int             Timestamp for connection monitoring
 */

export const OSC_ADDRESSES = {
  intensity: '/ope/intensity',
  density: '/ope/density',
  pitch: '/ope/pitch',
  state: '/ope/state',
  participants: '/ope/participants',
  override: (param: string) => `/ope/override/${param}`,
  mute: '/ope/mute',
  heartbeat: '/ope/heartbeat',
} as const;
