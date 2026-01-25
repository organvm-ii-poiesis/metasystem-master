import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import type { AudienceInput, ConsensusState, WelcomeMessage } from '../types';

interface UseSocketOptions {
  serverUrl?: string;
  autoConnect?: boolean;
}

interface UseSocketReturn {
  isConnected: boolean;
  clientId: string | null;
  participantCount: number;
  consensus: ConsensusState | null;
  latency: number;
  sendInput: (input: AudienceInput) => void;
  connect: () => void;
  disconnect: () => void;
}

const DEFAULT_CONSENSUS: ConsensusState = {
  intensity: 0.5,
  density: 0.5,
  pitch: 0.5,
  participantCount: 0,
  computedAt: 0,
  mode: 'arithmetic',
  variance: { intensity: 0, density: 0, pitch: 0 },
};

export function useSocket(options: UseSocketOptions = {}): UseSocketReturn {
  const {
    serverUrl = import.meta.env.VITE_SERVER_URL || 'http://localhost:3001',
    autoConnect = true,
  } = options;

  const socketRef = useRef<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [clientId, setClientId] = useState<string | null>(null);
  const [participantCount, setParticipantCount] = useState(0);
  const [consensus, setConsensus] = useState<ConsensusState>(DEFAULT_CONSENSUS);
  const [latency, setLatency] = useState(0);

  // Latency tracking
  const lastSendTime = useRef<number>(0);

  // Initialize socket
  useEffect(() => {
    const socket = io(serverUrl, {
      autoConnect,
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      timeout: 10000,
    });

    socketRef.current = socket;

    // Connection events
    socket.on('connect', () => {
      console.log('[Socket] Connected');
      setIsConnected(true);
    });

    socket.on('disconnect', (reason) => {
      console.log('[Socket] Disconnected:', reason);
      setIsConnected(false);
    });

    socket.on('connect_error', (error) => {
      console.error('[Socket] Connection error:', error.message);
    });

    // Welcome message with client ID
    socket.on('client:welcome', (data: WelcomeMessage) => {
      console.log('[Socket] Welcome:', data);
      setClientId(data.id);
      setParticipantCount(data.participantCount);
    });

    // Participant count updates
    socket.on('client:count', (count: number) => {
      setParticipantCount(count);
    });

    // Consensus state updates
    socket.on('state:consensus', (state: ConsensusState) => {
      setConsensus(state);
      
      // Calculate latency if we recently sent input
      if (lastSendTime.current > 0) {
        const roundTrip = Date.now() - lastSendTime.current;
        setLatency(roundTrip);
      }
    });

    // Error handling
    socket.on('error', (message: string) => {
      console.error('[Socket] Error:', message);
    });

    // Cleanup
    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [serverUrl, autoConnect]);

  // Send input to server
  const sendInput = useCallback((input: AudienceInput) => {
    if (socketRef.current?.connected) {
      lastSendTime.current = Date.now();
      socketRef.current.emit('input:update', input);
    }
  }, []);

  // Manual connect
  const connect = useCallback(() => {
    socketRef.current?.connect();
  }, []);

  // Manual disconnect
  const disconnect = useCallback(() => {
    socketRef.current?.disconnect();
  }, []);

  return {
    isConnected,
    clientId,
    participantCount,
    consensus,
    latency,
    sendInput,
    connect,
    disconnect,
  };
}
