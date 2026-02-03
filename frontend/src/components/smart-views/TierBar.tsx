import React from "react";

interface TierBarProps {
  activeTier: string;
  onSelectTier: (tier: string) => void;
}

const TIERS = [
  { id: "all", label: "All Products", color: "bg-slate-600" },
  { id: "entry", label: "Entry", color: "bg-green-600" },
  { id: "mid", label: "Mid-Range", color: "bg-blue-600" },
  { id: "pro", label: "Professional", color: "bg-purple-600" },
  { id: "flagship", label: "Flagship", color: "bg-amber-600" },
];

export const TierBar: React.FC<TierBarProps> = ({
  activeTier,
  onSelectTier,
}) => {
  return (
    <div className="flex items-center gap-3">
      <span className="text-slate-400 text-sm font-medium uppercase tracking-wider mr-2">
        Filter by Tier:
      </span>
      <div className="flex gap-2">
        {TIERS.map((tier) => (
          <button
            key={tier.id}
            onClick={() => onSelectTier(tier.id)}
            className={`
              px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200
              ${
                activeTier === tier.id
                  ? `${tier.color} text-white shadow-lg scale-105`
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white"
              }
            `}
          >
            {tier.label}
          </button>
        ))}
      </div>
    </div>
  );
};
