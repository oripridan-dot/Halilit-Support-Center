import React from 'react';
import { brandThemes } from '../../styles/brandThemes';

interface ContextBadgeProps {
  brand: string;      // e.g. "Nord"
  family?: string;    // e.g. "Grand" or "V-Drums"
  tier?: string;      // e.g. "Flagship"
}

export const ContextBadge: React.FC<ContextBadgeProps> = ({ brand, family, tier }) => {
  const theme = brandThemes[brand.toLowerCase()] || brandThemes['roland']; // Fallback
  
  return (
    <div className="absolute top-2 right-2 z-20 flex flex-col items-end gap-1 pointer-events-none">
      {/* 1. The Brand DNA (Logo + Color) */}
      <div 
        className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-white/95 shadow-sm border-l-4 backdrop-blur-sm"
        style={{ borderLeftColor: theme.colors.primary }}
      >
        <img 
          src={`/assets/logos/${brand.toLowerCase()}.svg`} 
          alt={brand}
          className="h-3 w-auto object-contain max-w-[40px]"
        />
      </div>

      {/* 2. The Family Context (Optional) */}
      {family && (
        <span className="text-[9px] font-mono font-bold tracking-wider uppercase bg-black/80 text-white px-1.5 py-0.5 rounded shadow-sm">
          {family}
        </span>
      )}
      
      {/* 3. Tier Indicator (Optional) */}
      {tier === 'Flagship' && (
         <div className="flex gap-0.5 mt-0.5">
            <div className="w-1 h-1 rounded-full bg-amber-400 shadow-[0_0_5px_rgba(251,191,36,0.8)]" />
            <div className="w-1 h-1 rounded-full bg-amber-400" />
            <div className="w-1 h-1 rounded-full bg-amber-400" />
         </div>
      )}
    </div>
  );
};
