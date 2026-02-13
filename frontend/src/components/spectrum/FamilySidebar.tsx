/**
 * FamilySidebar — Left navigation showing the domain-driven instrument family tree.
 *
 * 🎸 Guitars
 *    ├── Electric (LP Type · Strat Type · SG Type ...)
 *    ├── Acoustic (Dreadnought · Folk · Jumbo ...)
 *    └── Classical (Full · 3/4 · 1/2 ...)
 * 🎸 Bass
 *    ├── Electric Bass
 *    └── Acoustic Bass
 * 🔊 Amps & Effects
 * ...
 */
import React from "react";
import { useSpectrumV2Store } from "../../store/spectrumV2Store";
import { useInstrumentFamilies } from "../../hooks/useSpectrumV2";
import { FAMILY_ICONS } from "../../types/spectrum";
import type { InstrumentFamily } from "../../types/spectrum";

export const FamilySidebar: React.FC = () => {
  const {
    activeFamily,
    activeSubCategory,
    activeBodyType,
    setFamily,
    setSubCategory,
    setBodyType,
  } = useSpectrumV2Store();
  const { data, isLoading } = useInstrumentFamilies();

  if (isLoading) {
    return (
      <div className="w-52 bg-zinc-950 border-r border-zinc-800/60 p-4 shrink-0">
        <div className="space-y-3">
          {[...Array(7)].map((_, i) => (
            <div key={i} className="h-8 bg-zinc-900 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const families: InstrumentFamily[] = data?.families || [];

  return (
    <nav
      className="w-52 bg-zinc-950 border-r border-zinc-800/60 overflow-y-auto shrink-0
                    scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent flex flex-col"
    >
      {/* Header */}
      <div className="p-4 border-b border-zinc-800/60 shrink-0">
        <h2 className="text-white font-bold text-[11px] tracking-[0.2em] uppercase">
          Instrument Families
        </h2>
      </div>

      {/* Family Tree */}
      <div className="p-2 flex-1 overflow-y-auto">
        {/* "All" option */}
        <button
          onClick={() => setFamily(null)}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
            !activeFamily
              ? "bg-amber-500/10 text-amber-400 font-semibold"
              : "text-zinc-400 hover:text-white hover:bg-zinc-900"
          }`}
        >
          🌐 All Categories
        </button>

        <div className="mt-1 space-y-0.5">
          {families.map((family) => (
            <FamilyItem
              key={family.slug}
              family={family}
              isActive={activeFamily === family.slug}
              activeSubCategory={
                activeFamily === family.slug ? activeSubCategory : null
              }
              activeBodyType={
                activeFamily === family.slug ? activeBodyType : null
              }
              onSelectFamily={setFamily}
              onSelectSub={setSubCategory}
              onSelectBodyType={setBodyType}
            />
          ))}
        </div>
      </div>
    </nav>
  );
};

// ── Individual family item with expandable sub-categories ──

interface FamilyItemProps {
  family: InstrumentFamily;
  isActive: boolean;
  activeSubCategory: string | null;
  activeBodyType: string | null;
  onSelectFamily: (slug: string) => void;
  onSelectSub: (slug: string | null) => void;
  onSelectBodyType: (slug: string | null) => void;
}

const FamilyItem: React.FC<FamilyItemProps> = ({
  family,
  isActive,
  activeSubCategory,
  activeBodyType,
  onSelectFamily,
  onSelectSub,
  onSelectBodyType,
}) => {
  const icon = FAMILY_ICONS[family.slug] || "🎵";

  return (
    <div>
      {/* Family Button */}
      <button
        onClick={() => onSelectFamily(family.slug)}
        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-150
          flex items-center gap-2 ${
            isActive
              ? "bg-amber-500/10 text-amber-400 font-semibold"
              : "text-zinc-300 hover:text-white hover:bg-zinc-900"
          }`}
      >
        <span className="text-base leading-none">{icon}</span>
        <span className="truncate">{family.label}</span>
      </button>

      {/* Sub-categories (shown when family is active) */}
      {isActive && family.subCategories.length > 0 && (
        <div className="ml-7 mt-0.5 space-y-0.5 border-l border-zinc-800/50 pl-2 pb-1">
          {/* All sub-categories option */}
          <button
            onClick={() => onSelectSub(null)}
            className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
              !activeSubCategory
                ? "text-amber-400/80 font-medium"
                : "text-zinc-500 hover:text-zinc-300"
            }`}
          >
            All {family.label}
          </button>

          {family.subCategories.map((sub) => (
            <div key={sub.slug}>
              <button
                onClick={() => onSelectSub(sub.slug)}
                className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
                  activeSubCategory === sub.slug
                    ? "text-amber-400 bg-amber-500/5 font-medium"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {sub.label}
              </button>

              {/* Body types (shown when sub-category is active) */}
              {activeSubCategory === sub.slug && sub.bodyTypes.length > 0 && (
                <div className="ml-3 mt-0.5 flex flex-wrap gap-1 pb-1">
                  {sub.bodyTypes.map((bt) => (
                    <button
                      key={bt.slug}
                      onClick={() =>
                        onSelectBodyType(
                          activeBodyType === bt.slug ? null : bt.slug,
                        )
                      }
                      className={`px-1.5 py-0.5 rounded text-[9px] font-medium uppercase tracking-wider transition-colors ${
                        activeBodyType === bt.slug
                          ? "bg-amber-500/20 text-amber-400"
                          : "bg-zinc-900 text-zinc-600 hover:text-zinc-400"
                      }`}
                    >
                      {bt.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
