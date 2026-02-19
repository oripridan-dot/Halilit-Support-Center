import React, { useState, useEffect } from 'react';

interface JITStatusResponse {
  jit_enabled: boolean;
  last_updated: string;
}

interface ErrorResponse {
  detail: string;
}

const JITBadge: React.FC<{ productId: string }> = ({ productId }) => {
  const [jitStatus, setJitStatus] = useState<JITStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJITStatus = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`/api/products/${productId}/jit_status`);
        if (response.ok) {
          const data: JITStatusResponse = await response.json();
          setJitStatus(data);
        } else if (response.status === 404) {
          // Product not found, do nothing (per spec)
          setJitStatus(null);
        }
         else {
          const errorData: ErrorResponse = await response.json();
          setError(errorData.detail || 'Error fetching JIT status');
        }
      } catch (err: any) {
        setError('Error fetching JIT status');
      } finally {
        setLoading(false);
      }
    };

    fetchJITStatus();
    const intervalId = setInterval(fetchJITStatus, 5000);

    return () => clearInterval(intervalId);
  }, [productId]);

  if (!productId) return null;

  if (loading) {
    return (
      <span className="bg-slate-700 text-white text-xs font-semibold mr-2 px-2.5 py-0.5 rounded dark:bg-slate-700 dark:text-slate-300">
        Loading...
      </span>
    );
  }

  if (error) {
    return (
      <span className="bg-red-500 text-white text-xs font-semibold mr-2 px-2.5 py-0.5 rounded">
        Error
      </span>
    );
  }

  if (jitStatus === null) {
      return null;
  }

  return (
    <span
      className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${
        jitStatus.jit_enabled ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
      }`}
    >
      {jitStatus.jit_enabled ? 'JIT Enabled' : 'JIT Disabled'}
    </span>
  );
};

export default JITBadge;