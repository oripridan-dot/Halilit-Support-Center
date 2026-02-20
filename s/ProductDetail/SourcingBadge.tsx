import React from 'react';

interface SourcingBadgeProps {
  source:
    | 'halilit'
    | 'official'
    | 'estimated'
    | 'synthesized'
    | 'contextual'
    | 'none';
  label?: string;
  size?: 'xs' | 'sm';
}

const SourcingBadge: React.FC<SourcingBadgeProps> = ({ source, label, size = 'xs' }) => {
  const badgeText = label || (() => {
    switch (source) {
      case 'halilit':
        return 'Commercial';
      case 'official':
        return 'Official';
      case 'estimated':
        return 'Estimated';
      case 'synthesized':
        return 'AI Summary';
      case 'contextual':
        return 'Reviews';
      case 'none':
        return 'Unknown';
      default:
        return 'Unknown';
    }
  })();

  const badgeStyle = (() => {
    switch (source) {
      case 'halilit':
        return 'bg-emerald-900/40 text-emerald-400 border-emerald-700';
      case 'official':
        return 'bg-blue-900/40 text-blue-400 border-blue-700';
      case 'estimated':
        return 'bg-amber-900/40 text-amber-400 border-amber-700';
      case 'synthesized':
        return 'bg-purple-900/40 text-purple-400 border-purple-700';
      case 'contextual':
        return 'bg-orange-900/40 text-orange-400 border-orange-700';
      case 'none':
        return 'bg-zinc-800 text-zinc-500 border-zinc-700';
      default:
        return 'bg-zinc-800 text-zinc-500 border-zinc-700';
    }
  })();

  const ariaLabel = `Data source: ${badgeText}`;

  return (
    <span
      aria-label={ariaLabel}
      className={`rounded-full border px-2 py-0.5 text-xs font-medium ${badgeStyle}`}
    >
      {badgeText}
    </span>
  );
};

export default SourcingBadge;