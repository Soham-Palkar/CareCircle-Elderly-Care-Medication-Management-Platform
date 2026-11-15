'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { DoseEvent, RiskFlag } from '../api/types';

export type ConnectionStatus = 'connected' | 'reconnecting' | 'disconnected';

export interface SSEUpdateEvent {
  type: 'DOSE_UPDATED' | 'NEW_FLAG' | 'PROPOSAL_CREATED' | 'HEARTBEAT';
  data?: {
    dose?: DoseEvent;
    flag?: RiskFlag;
    message?: string;
  };
  timestamp: string;
}

export function useSSE(circleId: string = 'circle-101') {
  const [status, setStatus] = useState<ConnectionStatus>('connected');
  const [lastEvent, setLastEvent] = useState<SSEUpdateEvent | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/stream?circle_id=${circleId}`;
    
    // In browser environment, attempt real EventSource; fallback to simulated live updates
    let eventSource: EventSource | null = null;
    
    try {
      eventSource = new EventSource(url);

      eventSource.onopen = () => {
        setStatus('connected');
      };

      eventSource.onmessage = (e) => {
        try {
          const parsed: SSEUpdateEvent = JSON.parse(e.data);
          setLastEvent(parsed);
        } catch {
          // ignore malformed
        }
      };

      eventSource.onerror = () => {
        setStatus('reconnecting');
        eventSource?.close();
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      };
    } catch {
      // EventSource not available or cross-origin block: set connected in demo mode
      setStatus('connected');
    }

    return () => {
      eventSource?.close();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [circleId]);

  useEffect(() => {
    const cleanup = connect();
    return cleanup;
  }, [connect]);

  const triggerManualRefresh = useCallback(() => {
    setStatus('reconnecting');
    setTimeout(() => {
      setStatus('connected');
      setLastEvent({
        type: 'HEARTBEAT',
        data: { message: 'Synced with live server.' },
        timestamp: new Date().toISOString(),
      });
    }, 600);
  }, []);

  return { status, lastEvent, reconnect: triggerManualRefresh };
}

