import React from 'react';
import type { ConsensusState } from '../types';

interface CollectiveStateProps {
  consensus: ConsensusState;
  participantCount: number;
  latency: number;
  isConnected: boolean;
}

export function CollectiveState({
  consensus,
  participantCount,
  latency,
  isConnected,
}: CollectiveStateProps) {
  // Calculate overall "energy" for visual effect
  const energy = (consensus.intensity + consensus.density) / 2;
  
  // Calculate agreement (inverse of variance)
  const avgVariance = (
    consensus.variance.intensity +
    consensus.variance.density +
    consensus.variance.pitch
  ) / 3;
  const agreement = Math.max(0, 1 - avgVariance * 4); // Scale variance to 0-1

  return (
    <div style={styles.container}>
      {/* Ambient background visualization */}
      <div
        style={{
          ...styles.ambient,
          opacity: isConnected ? energy * 0.5 + 0.1 : 0.05,
          transform: `scale(${1 + energy * 0.2})`,
        }}
      />

      {/* Stats bar */}
      <div style={styles.statsBar}>
        {/* Connection status */}
        <div style={styles.stat}>
          <span
            style={{
              ...styles.statusDot,
              backgroundColor: isConnected ? '#4ecdc4' : '#ff6b6b',
            }}
          />
          <span style={styles.statLabel}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Participant count */}
        <div style={styles.stat}>
          <span style={styles.statValue}>{participantCount}</span>
          <span style={styles.statLabel}>
            {participantCount === 1 ? 'Participant' : 'Participants'}
          </span>
        </div>

        {/* Latency */}
        <div style={styles.stat}>
          <span style={{
            ...styles.statValue,
            color: latency < 100 ? '#4ecdc4' : latency < 200 ? '#ffe66d' : '#ff6b6b',
          }}>
            {latency}
          </span>
          <span style={styles.statLabel}>ms</span>
        </div>
      </div>

      {/* Agreement meter */}
      <div style={styles.agreementContainer}>
        <span style={styles.agreementLabel}>Consensus</span>
        <div style={styles.agreementBar}>
          <div
            style={{
              ...styles.agreementFill,
              width: `${agreement * 100}%`,
              backgroundColor: getAgreementColor(agreement),
            }}
          />
        </div>
        <span style={styles.agreementValue}>
          {agreement < 0.3 ? 'Divergent' : agreement < 0.7 ? 'Mixed' : 'Unified'}
        </span>
      </div>
    </div>
  );
}

function getAgreementColor(agreement: number): string {
  if (agreement < 0.3) return '#ff6b6b';
  if (agreement < 0.7) return '#ffe66d';
  return '#4ecdc4';
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    position: 'relative',
    padding: '16px',
    borderRadius: '12px',
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    overflow: 'hidden',
  },
  ambient: {
    position: 'absolute',
    inset: '-50%',
    background: 'radial-gradient(circle, rgba(78, 205, 196, 0.3) 0%, transparent 70%)',
    transition: 'opacity 300ms ease-out, transform 300ms ease-out',
    pointerEvents: 'none',
  },
  statsBar: {
    position: 'relative',
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    gap: '16px',
    marginBottom: '12px',
  },
  stat: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },
  statValue: {
    fontSize: '18px',
    fontWeight: 700,
    fontVariantNumeric: 'tabular-nums',
    color: '#fff',
  },
  statLabel: {
    fontSize: '11px',
    color: '#888',
    textTransform: 'uppercase',
  },
  agreementContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  agreementLabel: {
    fontSize: '10px',
    color: '#666',
    textTransform: 'uppercase',
    width: '60px',
  },
  agreementBar: {
    flex: 1,
    height: '6px',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  agreementFill: {
    height: '100%',
    borderRadius: '3px',
    transition: 'width 200ms ease-out, background-color 200ms ease-out',
  },
  agreementValue: {
    fontSize: '10px',
    color: '#888',
    width: '60px',
    textAlign: 'right',
  },
};
