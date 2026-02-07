import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useSocket } from './hooks/useSocket';
import { Slider } from './components/Slider';
import { CollectiveState } from './components/CollectiveState';
import { AudienceInput, PARAMETER_NAMES, PARAMETER_CONFIG } from './types';

function App() {
  // Local input state
  const [localInput, setLocalInput] = useState<AudienceInput>({
    intensity: 0.5,
    density: 0.5,
    pitch: 0.5,
  });

  // Socket connection
  const {
    isConnected,
    clientId,
    participantCount,
    consensus,
    latency,
    sendInput,
  } = useSocket();

  // Throttled send (max 20 updates/second)
  const lastSendRef = useRef<number>(0);
  const pendingInputRef = useRef<AudienceInput | null>(null);

  const throttledSend = useCallback((input: AudienceInput) => {
    const now = Date.now();
    const minInterval = 50; // 20 Hz max

    if (now - lastSendRef.current >= minInterval) {
      sendInput(input);
      lastSendRef.current = now;
      pendingInputRef.current = null;
    } else {
      pendingInputRef.current = input;
    }
  }, [sendInput]);

  // Flush pending input
  useEffect(() => {
    const interval = setInterval(() => {
      if (pendingInputRef.current) {
        sendInput(pendingInputRef.current);
        lastSendRef.current = Date.now();
        pendingInputRef.current = null;
      }
    }, 50);

    return () => clearInterval(interval);
  }, [sendInput]);

  // Handle parameter change
  const handleParameterChange = useCallback((param: keyof AudienceInput, value: number) => {
    setLocalInput((prev) => {
      const next = { ...prev, [param]: value };
      throttledSend(next);
      return next;
    });
  }, [throttledSend]);

  // Prevent pull-to-refresh on mobile
  useEffect(() => {
    const preventDefault = (e: TouchEvent) => {
      if (e.touches.length > 1) return;
      e.preventDefault();
    };

    document.addEventListener('touchmove', preventDefault, { passive: false });
    return () => document.removeEventListener('touchmove', preventDefault);
  }, []);

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <h1 style={styles.title}>Omni-Performative Engine</h1>
        <p style={styles.subtitle}>Shape the performance together</p>
      </header>

      {/* Collective state visualization */}
      <CollectiveState
        consensus={consensus!}
        participantCount={participantCount}
        latency={latency}
        isConnected={isConnected}
      />

      {/* Parameter sliders */}
      <div style={styles.sliderContainer}>
        {PARAMETER_NAMES.map((param) => (
          <Slider
            key={param}
            label={PARAMETER_CONFIG[param].label}
            description={PARAMETER_CONFIG[param].description}
            color={PARAMETER_CONFIG[param].color}
            value={localInput[param]}
            consensusValue={consensus?.[param] ?? 0.5}
            onChange={(value) => handleParameterChange(param, value)}
          />
        ))}
      </div>

      {/* Footer */}
      <footer style={styles.footer}>
        {clientId && (
          <span style={styles.clientId}>
            ID: {clientId.slice(0, 8)}
          </span>
        )}
        <span style={styles.instructions}>
          Drag sliders to influence the performance
        </span>
      </footer>

      {/* Connection overlay */}
      {!isConnected && (
        <div style={styles.overlay}>
          <div style={styles.overlayContent}>
            <div style={styles.spinner} />
            <p style={styles.overlayText}>Connecting to performance...</p>
          </div>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  app: {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    maxWidth: '480px',
    margin: '0 auto',
    padding: '16px',
    gap: '16px',
  },
  header: {
    textAlign: 'center',
    paddingTop: 'env(safe-area-inset-top)',
  },
  title: {
    fontSize: '20px',
    fontWeight: 700,
    margin: 0,
    color: '#fff',
    letterSpacing: '-0.5px',
  },
  subtitle: {
    fontSize: '12px',
    color: '#888',
    margin: '4px 0 0',
  },
  sliderContainer: {
    flex: 1,
    display: 'flex',
    justifyContent: 'space-around',
    alignItems: 'center',
    padding: '16px 0',
  },
  footer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
    paddingBottom: 'env(safe-area-inset-bottom)',
  },
  clientId: {
    fontSize: '10px',
    color: '#444',
    fontFamily: 'monospace',
  },
  instructions: {
    fontSize: '11px',
    color: '#666',
  },
  overlay: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(26, 26, 46, 0.95)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  overlayContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '16px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '3px solid rgba(255, 255, 255, 0.1)',
    borderTopColor: '#4ecdc4',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  overlayText: {
    color: '#888',
    fontSize: '14px',
  },
};

// Add keyframe animation via style tag
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);

export default App;
