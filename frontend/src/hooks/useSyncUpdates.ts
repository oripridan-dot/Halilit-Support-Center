/**
 * useSyncUpdates Hook
 * Real-time sync updates from backend auto-sync engine
 * Integrates with frontend data stores to push product updates
 */

import { useState, useCallback, useRef, useEffect } from 'react';

export interface SyncEvent {
    type: string;
    product_id?: string;
    product_name?: string;
    batch_id?: string;
    status?: string;
    error?: string;
    progress?: number;
    total?: number;
    percent_complete?: number;
    timestamp: string;
    [key: string]: any;
}

export interface SyncProgress {
    currentProduct: number;
    totalProducts: number;
    percentComplete: number;
    currentPhase: string;
    events: SyncEvent[];
}

export const useSyncUpdates = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [syncStatus, setSyncStatus] = useState<string>('idle');
    const [progress, setProgress] = useState<SyncProgress>({
        currentProduct: 0,
        totalProducts: 0,
        percentComplete: 0,
        currentPhase: '',
        events: []
    });

    const abortControllerRef = useRef<AbortController | null>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    /**
     * Sync a single product result to frontend
     */
    const syncProduct = useCallback(
        async (
            productData: any,
            onProgress?: (event: SyncEvent) => void
        ) => {
            setIsLoading(true);
            setError(null);
            setSyncStatus('syncing');
            setProgress({
                currentProduct: 0,
                totalProducts: 1,
                percentComplete: 0,
                currentPhase: 'starting',
                events: []
            });

            try {
                const response = await fetch('/api/copilot/sync', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(productData)
                });

                if (!response.body) {
                    throw new Error('No response body');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');

                    for (let i = 0; i < lines.length - 1; i++) {
                        const line = lines[i].trim();
                        if (line.startsWith('data: ')) {
                            try {
                                const eventData = JSON.parse(line.slice(6));

                                // Update progress based on event type
                                if (eventData.type === 'sync_phase') {
                                    setProgress(prev => ({
                                        ...prev,
                                        currentPhase: eventData.phase,
                                        percentComplete: (eventData.progress?.split('/')[0] || '1') as any * 25,
                                        events: [...prev.events, eventData]
                                    }));
                                } else if (eventData.type === 'product_synced') {
                                    setProgress(prev => ({
                                        ...prev,
                                        currentProduct: 1,
                                        percentComplete: 100,
                                        events: [...prev.events, eventData]
                                    }));
                                }

                                onProgress?.(eventData);
                            } catch (e) {
                                console.error('Failed to parse event:', e);
                            }
                        }
                    }

                    buffer = lines[lines.length - 1];
                }

                setSyncStatus('completed');
                setIsLoading(false);
                return true;
            } catch (err) {
                const errorMsg = err instanceof Error ? err.message : String(err);
                setError(errorMsg);
                setSyncStatus('error');
                setIsLoading(false);
                return false;
            }
        },
        []
    );

    /**
     * Sync a batch of products to frontend
     */
    const syncBatch = useCallback(
        async (
            products: any[],
            brand: string,
            onProgress?: (event: SyncEvent) => void
        ) => {
            setIsLoading(true);
            setError(null);
            setSyncStatus('syncing');
            setProgress({
                currentProduct: 0,
                totalProducts: products.length,
                percentComplete: 0,
                currentPhase: 'starting',
                events: []
            });

            try {
                const response = await fetch('/api/copilot/sync-batch', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        products,
                        brand
                    })
                });

                if (!response.body) {
                    throw new Error('No response body');
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');

                    for (let i = 0; i < lines.length - 1; i++) {
                        const line = lines[i].trim();
                        if (line.startsWith('data: ')) {
                            try {
                                const eventData = JSON.parse(line.slice(6));

                                // Update progress based on event type
                                if (eventData.type === 'batch_progress') {
                                    setProgress(prev => ({
                                        ...prev,
                                        currentProduct: eventData.progress,
                                        totalProducts: eventData.total,
                                        percentComplete: eventData.percent_complete,
                                        currentPhase: `${eventData.progress}/${eventData.total}`,
                                        events: [...prev.events, eventData]
                                    }));
                                } else if (eventData.type === 'batch_sync_completed') {
                                    setProgress(prev => ({
                                        ...prev,
                                        percentComplete: 100,
                                        currentPhase: 'completed',
                                        events: [...prev.events, eventData]
                                    }));
                                }

                                onProgress?.(eventData);
                            } catch (e) {
                                console.error('Failed to parse event:', e);
                            }
                        }
                    }

                    buffer = lines[lines.length - 1];
                }

                setSyncStatus('completed');
                setIsLoading(false);
                return true;
            } catch (err) {
                const errorMsg = err instanceof Error ? err.message : String(err);
                setError(errorMsg);
                setSyncStatus('error');
                setIsLoading(false);
                return false;
            }
        },
        []
    );

    /**
     * Get sync history
     */
    const getSyncHistory = useCallback(async (limit: number = 50) => {
        try {
            const response = await fetch(`/api/copilot/sync/history?limit=${limit}`);
            const data = await response.json();
            return data.history || [];
        } catch (err) {
            console.error('Failed to get sync history:', err);
            return [];
        }
    }, []);

    /**
     * Get status of a specific sync batch
     */
    const getBatchStatus = useCallback(async (batchId: string) => {
        try {
            const response = await fetch(`/api/copilot/sync/batch-status/${batchId}`);
            const data = await response.json();
            return data.batch_status;
        } catch (err) {
            console.error('Failed to get batch status:', err);
            return null;
        }
    }, []);

    /**
     * Toggle auto-sync on/off
     */
    const toggleSync = useCallback(async (enabled: boolean) => {
        try {
            const response = await fetch('/api/copilot/sync/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled })
            });
            const data = await response.json();
            return data.sync_enabled;
        } catch (err) {
            console.error('Failed to toggle sync:', err);
            return false;
        }
    }, []);

    /**
     * Clear sync history
     */
    const clearHistory = useCallback(async () => {
        try {
            const response = await fetch('/api/copilot/sync/history', {
                method: 'DELETE'
            });
            const data = await response.json();
            return data.status === 'cleared';
        } catch (err) {
            console.error('Failed to clear sync history:', err);
            return false;
        }
    }, []);

    /**
     * Cancel ongoing sync
     */
    const cancel = useCallback(() => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
        }
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            abortControllerRef.current = null;
        }
        setSyncStatus('idle');
        setIsLoading(false);
    }, []);

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (eventSourceRef.current) {
                eventSourceRef.current.close();
            }
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, []);

    return {
        // Methods
        syncProduct,
        syncBatch,
        getSyncHistory,
        getBatchStatus,
        toggleSync,
        clearHistory,
        cancel,

        // State
        isLoading,
        error,
        status: syncStatus,
        progress
    };
};

/**
 * useProgressTracker Hook (for sync progress display)
 * Simplified version of the Copilot progress tracker for sync operations
 */
export const useProgressTracker = () => {
    const [progress, setProgress] = useState<number>(0);
    const [totalSteps, setTotalSteps] = useState<number>(0);
    const [currentStep, setCurrentStep] = useState<number>(0);
    const [events, setEvents] = useState<SyncEvent[]>([]);

    const trackProgress = useCallback((event: SyncEvent) => {
        setEvents(prev => [...prev, event]);

        if (event.percent_complete !== undefined) {
            setProgress(event.percent_complete);
        }
        if (event.total !== undefined) {
            setTotalSteps(event.total);
        }
        if (event.progress !== undefined) {
            setCurrentStep(event.progress);
        }
    }, []);

    const reset = useCallback(() => {
        setProgress(0);
        setTotalSteps(0);
        setCurrentStep(0);
        setEvents([]);
    }, []);

    return {
        progress,
        totalSteps,
        currentStep,
        events,
        trackProgress,
        reset
    };
};
