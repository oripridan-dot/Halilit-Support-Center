import { useState, useEffect } from 'react';
import { GalaxyCategory } from '../types/galaxy';

export const useGalaxyData = () => {
    const [data, setData] = useState<GalaxyCategory[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchData = async () => {
        try {
            setLoading(true);
            // Ensure this endpoint matches your server.py
            const response = await fetch('http://localhost:8000/api/galaxy-view');

            if (!response.ok) {
                throw new Error('Failed to fetch galaxy data');
            }

            const jsonData = await response.json();
            setData(jsonData);
            setError(null);
        } catch (err) {
            console.error("Galaxy Fetch Error:", err);
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    return { data, loading, error, refetch: fetchData };
};
