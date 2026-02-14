import { motion } from "framer-motion";
import { ShoppingBag } from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";

export interface AccessoryItem {
  id: string;
  name: string;
  price?: number;
  image_url?: string;
  reason?: string;
}

interface SmartAccessoriesProps {
  accessories: AccessoryItem[];
  brandColor?: string;
  onProductClick?: (id: string) => void;
}

/**
 * SmartAccessories — "Don't let them leave without..." contextual upsell strip.
 */
export const SmartAccessories = ({
  accessories,
  brandColor = "#3b82f6",
  onProductClick,
}: SmartAccessoriesProps) => {
  if (!accessories || accessories.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3, ease: "easeOut" }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <ShoppingBag size={14} className="text-emerald-400" />
        <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Don't forget
        </span>
        <span className="ml-auto text-[10px] text-zinc-600">
          {accessories.length} suggestion{accessories.length !== 1 ? "s" : ""}
        </span>
      </div>

      {/* Horizontal scroll strip */}
      <div className="flex gap-3 overflow-x-auto pb-1 -mx-1 px-1">
        {accessories.map((acc, i) => (
          <button
            key={acc.id || i}
            onClick={() => onProductClick?.(acc.id)}
            className="group shrink-0 w-36 bg-zinc-800/40 hover:bg-zinc-800/70 border border-zinc-700/40 hover:border-emerald-500/30 rounded-xl p-3 transition-all duration-200 text-left"
          >
            {/* Image */}
            <div className="aspect-square bg-zinc-900/60 rounded-lg overflow-hidden mb-2">
              <ImageWithFallback
                src={acc.image_url || ""}
                alt={acc.name || "Accessory"}
                className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
              />
            </div>

            {/* Info */}
            <p className="text-[11px] text-white font-medium truncate">
              {acc.name}
            </p>
            {acc.reason && (
              <p className="text-[9px] text-zinc-500 truncate mt-0.5">
                {acc.reason}
              </p>
            )}
            {acc.price && acc.price > 0 && (
              <p className="text-[10px] text-emerald-400 font-semibold mt-1">
                {"\u20AA"}{acc.price.toLocaleString("he-IL")}
              </p>
            )}
          </button>
        ))}
      </div>
    </motion.div>
  );
};
