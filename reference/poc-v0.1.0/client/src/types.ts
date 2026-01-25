/**
 * Shared types between client and server.
 */

export interface AudienceInput {
  intensity: number;
  density: number;
  pitch: number;
}

export interface ConsensusState extends AudienceInput {
  participantCount: number;
  computedAt: number;
  mode: string;
  variance: {
    intensity: number;
    density: number;
    pitch: number;
  };
}

export interface ParameterOverride {
  locked: boolean;
  lockedValue?: number;
  bias: number;
  rangeMin: number;
  rangeMax: number;
}

export interface PerformerOverrides {
  intensity: ParameterOverride;
  density: ParameterOverride;
  pitch: ParameterOverride;
  masterMute: boolean;
  masterBypass: boolean;
}

export interface WelcomeMessage {
  id: string;
  participantCount: number;
}

export type ParameterName = 'intensity' | 'density' | 'pitch';

export const PARAMETER_NAMES: ParameterName[] = ['intensity', 'density', 'pitch'];

export const PARAMETER_CONFIG: Record<ParameterName, {
  label: string;
  color: string;
  description: string;
}> = {
  intensity: {
    label: 'Intensity',
    color: '#ff6b6b',
    description: 'Energy / Volume',
  },
  density: {
    label: 'Density',
    color: '#4ecdc4',
    description: 'Complexity / Texture',
  },
  pitch: {
    label: 'Pitch',
    color: '#ffe66d',
    description: 'Harmonic Center',
  },
};
