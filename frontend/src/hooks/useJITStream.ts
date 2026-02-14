/**
 * useJITStream — SSE streaming hook for JIT Intelligence
 *
 * Connects to /api/jit/{product_id}/stream and provides
 * real-time phase transitions: snap → promise → deliver.
 *
 * The hook manages:
 *  - EventSource connection lifecycle
 *  - Phase state machine (idle → snap → promise → deliver → complete)
 *  - Auto-reconnect on error
 *  - Cleanup on unmount
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import type { JITStreamState, JITSnap, JITPromise, JITDelivery } from '../types';

const INITIAL_STATE: JITStreamState = {
    phase: 'idle',
    snap: null,
    promise: null,
    delivery: null,
    error: null,
    cached: false,
    durationMs: 0,
};

export function useJITStream(productId: string | null) {
    const [state, setState] = useState<JITStreamState>(INITIAL_STATE);
    const eventSourceRef = useRef<EventSource | null>(null);
    const mountedRef = useRef(true);

    const connect = useCallback((pid: string) => {
        // Close existing connection
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }

        setState({ ...INITIAL_STATE, phase: 'idle' });

        const es = new EventSource(`/api/jit/${encodeURIComponent(pid)}/stream`);
        eventSourceRef.current = es;

        es.addEventListener('snap', (e) => {
            if (!mountedRef.current) return;
            try {
                const data: JITSnap = JSON.parse(e.data);
                setState(prev => ({ ...prev, phase: 'snap', snap: data }));
            } catch (err) {
                console.error('[JIT] Failed to parse snap:', err);
            }
        });

        es.addEventListener('promise', (e) => {
            if (!mountedRef.current) return;
            try {
                const data: JITPromise = JSON.parse(e.data);
                setState(prev => ({ ...prev, phase: 'promise', promise: data }));
            } catch (err) {
                console.error('[JIT] Failed to parse promise:', err);
            }
        });

        es.addEventListener('deliver', (e) => {
            if (!mountedRef.current) return;
            try {
                const data: JITDelivery = JSON.parse(e.data);
                setState(prev => ({ ...prev, phase: 'deliver', delivery: data }));
            } catch (err) {
                console.error('[JIT] Failed to parse deliver:', err);
            }
        });

        es.addEventListener('complete', (e) => {
            if (!mountedRef.current) return;
            try {
                const data = JSON.parse(e.data);
                setState(prev => ({
                    ...prev,
                    phase: 'complete',
                    cached: data.cached ?? false,
                    durationMs: data.duration_ms ?? 0,
                }));
            } catch {
                setState(prev => ({ ...prev, phase: 'complete' }));
            }
            es.close();
        });

        es.addEventListener('error', (e) => {
            if (!mountedRef.current) return;
            // Check if it's a server-sent error event or connection error
            if (e instanceof MessageEvent) {
                try {
                    const data = JSON.parse(e.data);
                    setState(prev => ({ ...prev, phase: 'error', error: data.message || 'Unknown error' }));
                } catch {
                    setState(prev => ({ ...prev, phase: 'error', error: 'Stream error' }));
                }
            }
            es.close();
        });

        es.onerror = () => {
            if (!mountedRef.current) return;
            // Only set error if we haven't completed
            setState(prev => {
                if (prev.phase === 'complete' || prev.phase === 'deliver') return prev;
                return { ...prev, phase: 'error', error: 'Connection lost' };
            });
            es.close();
        };
    }, []);

    // Connect when productId changes
    useEffect(() => {
        mountedRef.current = true;

        if (productId) {
            connect(productId);
        } else {
            setState(INITIAL_STATE);
        }

        return () => {
            mountedRef.current = false;
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
                eventSourceRef.current = null;
            }
        };
    }, [productId, connect]);

    const retry = useCallback(() => {
        if (productId) connect(productId);
    }, [productId, connect]);

    return {
        ...state,
        retry,
        isLoading: state.phase === 'idle' || state.phase === 'snap' || state.phase === 'promise',
        isReady: state.phase === 'deliver' || state.phase === 'complete',
        hasError: state.phase === 'error',
    };
}
