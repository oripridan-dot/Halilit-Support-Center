// frontend/src/hooks/useLearningStream.ts
import { useEffect } from 'react';
import { useProductStore } from '../store/productStore';

export const useLearningStream = () => {
    const addInsight = useProductStore((state) => state.addInsight);

    useEffect(() => {
        // Connect to FastAPI SSE endpoint
        // Assuming the backend is running on localhost:8000 or proxied via Vite
        const eventSource = new EventSource('/api/stream/learning');

        eventSource.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                if (payload.type === 'LEARNING_INSIGHT') {
                    addInsight({
                        brand: payload.brand,
                        insight: payload.insight,
                        timestamp: new Date().toLocaleTimeString(),
                        productId: payload.productId
                    });
                }
            } catch (e) {
                console.error("Failed to parse learning stream message", e);
            }
        };

        eventSource.onerror = (err) => {
            console.error("Learning Stream Error:", err);
            eventSource.close();
        };

        return () => {
            eventSource.close();
        };
    }, [addInsight]);
};
