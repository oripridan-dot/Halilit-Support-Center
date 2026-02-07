import { useState, useCallback, useRef } from 'react';

/**
 * Hook for interacting with CopilotKit Skills Framework
 * 
 * Usage:
 * const { executeSkill, executePipeline, status } = useCopilotSkills();
 * const result = await executeSkill('harvest', { raw_product, brand });
 */
export function useCopilotSkills() {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [status, setStatus] = useState('idle');
    const abortControllerRef = useRef(null);

    // Execute single skill
    const executeSkill = useCallback(async (skillName, context) => {
        setIsLoading(true);
        setError(null);
        setStatus('executing');

        try {
            const response = await fetch('/api/copilot/execute-skill', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    skill: skillName,
                    context: context
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            setStatus('idle');
            return result;
        } catch (err) {
            const errorMsg = err.message || 'Unknown error';
            setError(errorMsg);
            setStatus('error');
            return { success: false, error: errorMsg };
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Execute full pipeline with streaming
    const executePipeline = useCallback(async (rawProduct, brand, onProgress) => {
        setIsLoading(true);
        setError(null);
        setStatus('streaming');
        abortControllerRef.current = new AbortController();

        try {
            const response = await fetch('/api/copilot/pipeline', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    raw_product: rawProduct,
                    brand: brand
                }),
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6));
                            if (onProgress) onProgress(event);
                        } catch (e) {
                            console.warn('Failed to parse SSE event:', e);
                        }
                    }
                }
            }

            setStatus('idle');
            return { success: true, completed: true };
        } catch (err) {
            if (err.name !== 'AbortError') {
                const errorMsg = err.message || 'Pipeline execution failed';
                setError(errorMsg);
                setStatus('error');
                return { success: false, error: errorMsg };
            }
            setStatus('idle');
            return { success: false, cancelled: true };
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Execute batch ingest with streaming
    const executeBatchIngest = useCallback(async (products, brand, onProgress) => {
        setIsLoading(true);
        setError(null);
        setStatus('streaming');
        abortControllerRef.current = new AbortController();

        try {
            const response = await fetch('/api/copilot/batch-ingest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    products: products,
                    brand: brand
                }),
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle SSE stream
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const event = JSON.parse(line.slice(6));
                            if (onProgress) onProgress(event);
                        } catch (e) {
                            console.warn('Failed to parse SSE event:', e);
                        }
                    }
                }
            }

            setStatus('idle');
            return { success: true, completed: true };
        } catch (err) {
            if (err.name !== 'AbortError') {
                const errorMsg = err.message || 'Batch ingest failed';
                setError(errorMsg);
                setStatus('error');
                return { success: false, error: errorMsg };
            }
            setStatus('idle');
            return { success: false, cancelled: true };
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Get available skills
    const getAvailableSkills = useCallback(async () => {
        try {
            const response = await fetch('/api/copilot/skills');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.error('Failed to fetch skills:', err);
            return { skills: [], error: err.message };
        }
    }, []);

    // Get pipeline status
    const getPipelineStatus = useCallback(async () => {
        try {
            const response = await fetch('/api/copilot/status');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.error('Failed to fetch status:', err);
            return { status: 'error', error: err.message };
        }
    }, []);

    // Get execution history
    const getExecutionHistory = useCallback(async (limit = 50) => {
        try {
            const response = await fetch(`/api/copilot/history?limit=${limit}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (err) {
            console.error('Failed to fetch history:', err);
            return { history: [], error: err.message };
        }
    }, []);

    // Cancel ongoing operation
    const cancel = useCallback(() => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setStatus('idle');
            setIsLoading(false);
        }
    }, []);

    return {
        // Methods
        executeSkill,
        executePipeline,
        executeBatchIngest,
        getAvailableSkills,
        getPipelineStatus,
        getExecutionHistory,
        cancel,

        // State
        isLoading,
        error,
        status
    };
}

/**
 * Hook for streaming progress updates
 * 
 * Usage:
 * const { progress, totalPhases } = useProgressTracker();
 * <ProgressBar current={progress} total={totalPhases} />
 */
export function useProgressTracker() {
    const [progress, setProgress] = useState(0);
    const [totalPhases, setTotalPhases] = useState(6);
    const [events, setEvents] = useState([]);
    const [currentPhase, setCurrentPhase] = useState(null);

    const trackProgress = useCallback((event) => {
        const { type, phase, total_phases, phase_name, status } = event;

        if (type === 'pipeline_started') {
            setProgress(0);
            setTotalPhases(total_phases || 6);
            setEvents([event]);
            setCurrentPhase('starting');
        } else if (type === 'phase_completed') {
            setProgress(phase || 0);
            setCurrentPhase(phase_name || null);
            setEvents(prev => [...prev, event]);
        } else if (type === 'pipeline_completed') {
            setProgress(totalPhases);
            setCurrentPhase(status === 'APPROVED' ? 'approved' : 'rejected');
            setEvents(prev => [...prev, event]);
        }
    }, [totalPhases]);

    const reset = useCallback(() => {
        setProgress(0);
        setTotalPhases(6);
        setEvents([]);
        setCurrentPhase(null);
    }, []);

    return {
        progress,
        totalPhases,
        events,
        currentPhase,
        trackProgress,
        reset,
        percentComplete: Math.round((progress / totalPhases) * 100)
    };
}
