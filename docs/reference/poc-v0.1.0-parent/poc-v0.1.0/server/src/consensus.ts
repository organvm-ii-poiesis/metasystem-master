/**
 * Omni-Performative Engine — Consensus Module
 * 
 * Aggregation algorithms for combining distributed audience inputs
 * into coherent collective state.
 */

import {
  AudienceInput,
  TimestampedInput,
  ConsensusState,
  ConsensusMode,
  ParameterName,
  PARAMETER_NAMES,
  DEFAULTS,
} from './types.js';

// ============================================================================
// Consensus Engine
// ============================================================================

export class ConsensusEngine {
  private mode: ConsensusMode;
  
  constructor(mode: ConsensusMode = 'arithmetic') {
    this.mode = mode;
  }
  
  /**
   * Set the aggregation mode.
   */
  setMode(mode: ConsensusMode): void {
    this.mode = mode;
  }
  
  /**
   * Compute consensus from array of inputs.
   * Returns null if no valid inputs.
   */
  compute(inputs: TimestampedInput[]): ConsensusState {
    const now = Date.now();
    
    if (inputs.length === 0) {
      return {
        ...DEFAULTS.consensus,
        computedAt: now,
        mode: this.mode,
      };
    }
    
    // Select aggregation strategy
    const aggregator = this.getAggregator(this.mode);
    
    // Compute per-parameter
    const result: AudienceInput = {
      intensity: 0,
      density: 0,
      pitch: 0,
    };
    
    const variance = {
      intensity: 0,
      density: 0,
      pitch: 0,
    };
    
    for (const param of PARAMETER_NAMES) {
      const values = inputs.map(i => i[param]);
      result[param] = aggregator(values, inputs);
      variance[param] = this.computeVariance(values, result[param]);
    }
    
    return {
      ...result,
      participantCount: inputs.length,
      computedAt: now,
      mode: this.mode,
      variance,
    };
  }
  
  /**
   * Get aggregation function for mode.
   */
  private getAggregator(
    mode: ConsensusMode
  ): (values: number[], inputs: TimestampedInput[]) => number {
    switch (mode) {
      case 'arithmetic':
        return this.arithmeticMean.bind(this);
      case 'weighted':
        return this.weightedMean.bind(this);
      case 'median':
        return this.median.bind(this);
      case 'mode':
        return this.modeClustering.bind(this);
      default:
        return this.arithmeticMean.bind(this);
    }
  }
  
  // ==========================================================================
  // Aggregation Strategies
  // ==========================================================================
  
  /**
   * Simple arithmetic mean.
   * Fast, democratic, but sensitive to outliers.
   */
  private arithmeticMean(values: number[]): number {
    if (values.length === 0) return 0.5;
    const sum = values.reduce((a, b) => a + b, 0);
    return sum / values.length;
  }
  
  /**
   * Weighted mean by connection duration.
   * Rewards sustained engagement; reduces impact of late-joiners.
   */
  private weightedMean(values: number[], inputs: TimestampedInput[]): number {
    if (values.length === 0) return 0.5;
    
    // Calculate weights based on connection duration
    // Use log scale to prevent long-connected users from dominating
    const weights = inputs.map(i => Math.log(1 + i.connectionDuration / 1000));
    const totalWeight = weights.reduce((a, b) => a + b, 0);
    
    if (totalWeight === 0) return this.arithmeticMean(values);
    
    let weightedSum = 0;
    for (let i = 0; i < values.length; i++) {
      weightedSum += values[i] * weights[i];
    }
    
    return weightedSum / totalWeight;
  }
  
  /**
   * Median value.
   * Robust to outliers; represents "typical" audience member.
   */
  private median(values: number[]): number {
    if (values.length === 0) return 0.5;
    
    const sorted = [...values].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    
    if (sorted.length % 2 === 0) {
      return (sorted[mid - 1] + sorted[mid]) / 2;
    }
    return sorted[mid];
  }
  
  /**
   * Mode via clustering.
   * Groups similar values; selects center of largest cluster.
   * Good for detecting emergent consensus among audience factions.
   */
  private modeClustering(values: number[]): number {
    if (values.length === 0) return 0.5;
    if (values.length < 3) return this.arithmeticMean(values);
    
    // Simple binning approach (5 bins across 0-1 range)
    const numBins = 5;
    const binWidth = 1 / numBins;
    const bins: number[][] = Array.from({ length: numBins }, () => []);
    
    for (const v of values) {
      const binIndex = Math.min(Math.floor(v / binWidth), numBins - 1);
      bins[binIndex].push(v);
    }
    
    // Find largest bin
    let maxBin = 0;
    let maxSize = 0;
    for (let i = 0; i < bins.length; i++) {
      if (bins[i].length > maxSize) {
        maxSize = bins[i].length;
        maxBin = i;
      }
    }
    
    // Return mean of largest bin
    return this.arithmeticMean(bins[maxBin]);
  }
  
  // ==========================================================================
  // Statistical Helpers
  // ==========================================================================
  
  /**
   * Compute variance (measure of agreement).
   * Low variance = strong consensus; high variance = divided audience.
   */
  private computeVariance(values: number[], mean: number): number {
    if (values.length < 2) return 0;
    
    const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
    const sumSquaredDiffs = squaredDiffs.reduce((a, b) => a + b, 0);
    
    return sumSquaredDiffs / values.length;
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Apply performer overrides to consensus state.
 */
export function applyOverrides(
  consensus: ConsensusState,
  overrides: import('./types.js').PerformerOverrides
): ConsensusState {
  if (overrides.masterBypass) {
    return consensus; // Return raw consensus
  }
  
  const result = { ...consensus };
  
  for (const param of PARAMETER_NAMES) {
    const override = overrides[param];
    
    if (override.locked && override.lockedValue !== undefined) {
      // Use locked value
      result[param] = override.lockedValue;
    } else {
      // Apply bias and range constraints
      let value = consensus[param] + override.bias;
      value = Math.max(override.rangeMin, Math.min(override.rangeMax, value));
      result[param] = value;
    }
  }
  
  return result;
}

/**
 * Clamp value to 0-1 range.
 */
export function clamp(value: number): number {
  return Math.max(0, Math.min(1, value));
}

/**
 * Validate input is within expected range.
 */
export function validateInput(input: AudienceInput): AudienceInput {
  return {
    intensity: clamp(input.intensity ?? 0.5),
    density: clamp(input.density ?? 0.5),
    pitch: clamp(input.pitch ?? 0.5),
  };
}
