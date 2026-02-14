/**
 * useExploration — Hook for JIT exploration actions
 *
 * Fires exploration requests (compare, deep-dive, setup, etc.)
 * and manages the loading + result state for each action.
 */

import { useMutation } from '@tanstack/react-query';

export interface ExplorationResult {
    product_id: string;
    action_type: string;
    topic: string;
    content?: string;
    format?: string;
    [key: string]: unknown;
}

async function fetchExploration(body: {
    product_id: string;
    action_type: string;
    topic?: string;
    target_id?: string;
}): Promise<ExplorationResult> {
    const response = await fetch('/api/jit/explore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
    if (!response.ok) {
        throw new Error(`Exploration failed: ${response.statusText}`);
    }
    return response.json();
}

export function useExploration() {
    const mutation = useMutation<ExplorationResult, Error, {
        product_id: string;
        action_type: string;
        topic?: string;
        target_id?: string;
    }>({
        mutationFn: fetchExploration,
    });

    return {
        explore: mutation.mutate,
        exploreAsync: mutation.mutateAsync,
        result: mutation.data ?? null,
        isExploring: mutation.isPending,
        error: mutation.error?.message ?? null,
        reset: mutation.reset,
    };
}
