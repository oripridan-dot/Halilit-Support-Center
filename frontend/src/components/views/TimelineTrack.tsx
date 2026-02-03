import React from "react";
import { Product } from "../../types/galaxy";

interface TimelineTrackProps {
  brand: string;
  products: Product[];
  onHover: (product: Product | null) => void;
  onClick: (product: Product) => void;
}

export const TimelineTrack: React.FC<TimelineTrackProps> = ({
  brand,
  products,
  onHover,
  onClick,
}) => {
  return (
    <div className="px-6">
      {/* Brand Label */}
      <div className="mb-3">
        <h3 className="text-lg font-bold text-slate-300 uppercase tracking-wider">
          {brand}
        </h3>
        <div className="h-px bg-gradient-to-r from-blue-500/50 to-transparent w-full mt-1" />
      </div>

      {/* Horizontal Scroll Track */}
      <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-track-slate-900 scrollbar-thumb-slate-700 hover:scrollbar-thumb-slate-600">
        {products.map((product) => (
          <button
            key={product.uuid}
            onMouseEnter={() => onHover(product)}
            onMouseLeave={() => onHover(null)}
            onClick={() => onClick(product)}
            className="flex-shrink-0 w-40 h-40 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-blue-500 transition-all duration-200 hover:scale-105 hover:shadow-xl hover:shadow-blue-500/20 p-3 flex flex-col items-center justify-center group"
          >
            {/* Product Image */}
            <div className="w-24 h-24 mb-2 flex items-center justify-center">
              <img
                src={product.image}
                alt={product.name}
                className="max-w-full max-h-full object-contain group-hover:scale-110 transition-transform duration-300"
              />
            </div>

            {/* Product Name (Truncated) */}
            <p className="text-xs text-slate-400 group-hover:text-white text-center line-clamp-2 font-medium">
              {product.name}
            </p>

            {/* Tier Badge */}
            <div
              className={`mt-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                product.tier === "flagship"
                  ? "bg-amber-600/20 text-amber-400 border border-amber-600/30"
                  : product.tier === "pro"
                    ? "bg-purple-600/20 text-purple-400 border border-purple-600/30"
                    : product.tier === "mid"
                      ? "bg-blue-600/20 text-blue-400 border border-blue-600/30"
                      : "bg-green-600/20 text-green-400 border border-green-600/30"
              }`}
            >
              {product.tier}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
