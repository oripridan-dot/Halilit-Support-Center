/**
 * JITBadge — frontend/src/components/ProductDetail/JITBadge.tsx
 *
 * Displays the live JIT intelligence phase as a status badge on the
 * Product Detail header. Updates dynamically as SSE events arrive.
 *
 * Phases: idle → snap → intel → wisdom → complete | error
 */
import React from 'react';
import { useJITIntelligence, JITPhase } from '../../hooks';

interface JITBadgeProps {
  productId: string | null;
}

const PHASE_CONFIG: Record<JITPhase, { label: string; className: string }> = {
  idle:     { label: 'JIT Ready',     className: 'bg-zinc-700 text-zinc-300' },
  snap:     { label: 'Connecting…',   className: 'bg-blue-700 text-blue-100 animate-pulse' },
  intel:    { label: 'Gathering…',    className: 'bg-yellow-600 text-yellow-100 animate-pulse' },
  wisdom:   { label: 'Analysing…',    className: 'bg-orange-600 text-orange-100 animate-pulse' },
  complete: { label: '✓ JIT Ready',   className: 'bg-green-700 text-green-100' },
  error:    { label: 'JIT Unavailable', className: 'bg-red-800 text-red-200' },
};

const JITBadge: React.FC<JITBadgeProps> = ({ productId }) => {
  const jit = useJITIntelligence(productId);
  const config = PHASE_CONFIG[jit.phase] ?? PHASE_CONFIG.idle;

  if (jit.phase === 'idle') return null;

  return (
    <span
      className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${config.className}`}
      title={jit.statusMessage || config.label}
    >
      {config.label}
    </span>
  );
};

export default JITBadge;
