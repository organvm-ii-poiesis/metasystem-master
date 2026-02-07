import React, { useRef, useCallback, useState } from 'react';

interface SliderProps {
  label: string;
  value: number;
  consensusValue: number;
  color: string;
  description: string;
  locked?: boolean;
  onChange: (value: number) => void;
}

export function Slider({
  label,
  value,
  consensusValue,
  color,
  description,
  locked = false,
  onChange,
}: SliderProps) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  // Convert touch/mouse Y position to value (0-1)
  const getValueFromPosition = useCallback((clientY: number): number => {
    if (!trackRef.current) return value;

    const rect = trackRef.current.getBoundingClientRect();
    const relativeY = clientY - rect.top;
    const height = rect.height;

    // Invert: top = 1, bottom = 0
    const rawValue = 1 - relativeY / height;
    return Math.max(0, Math.min(1, rawValue));
  }, [value]);

  // Handle pointer events
  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    if (locked) return;
    
    e.preventDefault();
    setIsDragging(true);
    
    const newValue = getValueFromPosition(e.clientY);
    onChange(newValue);
    
    // Capture pointer for drag
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
  }, [locked, getValueFromPosition, onChange]);

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!isDragging || locked) return;
    
    const newValue = getValueFromPosition(e.clientY);
    onChange(newValue);
  }, [isDragging, locked, getValueFromPosition, onChange]);

  const handlePointerUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  // Keyboard support
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (locked) return;
    
    const step = e.shiftKey ? 0.1 : 0.01;
    
    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault();
        onChange(Math.min(1, value + step));
        break;
      case 'ArrowDown':
        e.preventDefault();
        onChange(Math.max(0, value - step));
        break;
      case 'Home':
        e.preventDefault();
        onChange(1);
        break;
      case 'End':
        e.preventDefault();
        onChange(0);
        break;
    }
  }, [locked, value, onChange]);

  return (
    <div style={styles.container}>
      {/* Label */}
      <div style={styles.labelContainer}>
        <span style={{ ...styles.label, color }}>{label}</span>
        <span style={styles.description}>{description}</span>
      </div>

      {/* Track */}
      <div
        ref={trackRef}
        style={{
          ...styles.track,
          opacity: locked ? 0.5 : 1,
          cursor: locked ? 'not-allowed' : 'pointer',
        }}
        role="slider"
        aria-label={label}
        aria-valuenow={Math.round(value * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
        tabIndex={locked ? -1 : 0}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={handlePointerUp}
        onKeyDown={handleKeyDown}
      >
        {/* Consensus indicator (background) */}
        <div
          style={{
            ...styles.consensusFill,
            height: `${consensusValue * 100}%`,
            backgroundColor: color,
            opacity: 0.2,
          }}
        />

        {/* User value fill */}
        <div
          style={{
            ...styles.fill,
            height: `${value * 100}%`,
            backgroundColor: color,
          }}
        />

        {/* Consensus line marker */}
        <div
          style={{
            ...styles.consensusMarker,
            bottom: `${consensusValue * 100}%`,
            backgroundColor: color,
          }}
        />

        {/* Handle */}
        <div
          style={{
            ...styles.handle,
            bottom: `calc(${value * 100}% - 16px)`,
            backgroundColor: isDragging ? color : '#fff',
            borderColor: color,
            transform: isDragging ? 'scale(1.2)' : 'scale(1)',
          }}
        />

        {/* Lock indicator */}
        {locked && (
          <div style={styles.lockOverlay}>
            <span style={styles.lockIcon}>🔒</span>
          </div>
        )}
      </div>

      {/* Value display */}
      <div style={styles.valueContainer}>
        <span style={{ ...styles.value, color }}>
          {Math.round(value * 100)}
        </span>
        <span style={styles.valueLabel}>you</span>
      </div>

      {/* Consensus value */}
      <div style={styles.consensusContainer}>
        <span style={{ ...styles.consensusValue, color }}>
          {Math.round(consensusValue * 100)}
        </span>
        <span style={styles.valueLabel}>all</span>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 8px',
    userSelect: 'none',
  },
  labelContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '2px',
  },
  label: {
    fontSize: '14px',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  description: {
    fontSize: '10px',
    color: '#888',
    textTransform: 'uppercase',
  },
  track: {
    position: 'relative',
    width: '48px',
    height: '200px',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '24px',
    overflow: 'hidden',
    touchAction: 'none',
  },
  fill: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderRadius: '0 0 24px 24px',
    transition: 'height 50ms ease-out',
  },
  consensusFill: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderRadius: '0 0 24px 24px',
  },
  consensusMarker: {
    position: 'absolute',
    left: '4px',
    right: '4px',
    height: '3px',
    borderRadius: '2px',
    transform: 'translateY(50%)',
    transition: 'bottom 100ms ease-out',
  },
  handle: {
    position: 'absolute',
    left: '50%',
    width: '32px',
    height: '32px',
    marginLeft: '-16px',
    backgroundColor: '#fff',
    borderRadius: '50%',
    border: '3px solid',
    boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
    transition: 'transform 100ms ease-out, background-color 100ms ease-out',
  },
  lockOverlay: {
    position: 'absolute',
    inset: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(0,0,0,0.5)',
    borderRadius: '24px',
  },
  lockIcon: {
    fontSize: '24px',
  },
  valueContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  value: {
    fontSize: '24px',
    fontWeight: 700,
    fontVariantNumeric: 'tabular-nums',
  },
  valueLabel: {
    fontSize: '10px',
    color: '#666',
    textTransform: 'uppercase',
  },
  consensusContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    opacity: 0.6,
  },
  consensusValue: {
    fontSize: '16px',
    fontWeight: 600,
    fontVariantNumeric: 'tabular-nums',
  },
};
