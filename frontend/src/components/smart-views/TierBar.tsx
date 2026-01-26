import { AnimatePresence, motion } from "framer-motion";
import { RotateCcw, ZoomIn } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { getPriceValue } from "../../lib/priceFormatter";
import type { Product } from "../../types";

interface TierBarProps {
  products: Product[];
  onHoverProduct: (product: Product | null) => void;
  onSelectProduct: (productId: string) => void;
}

// Visual constants
const NODE_SIZE = 48; // Size of the product orb (px)
const X_BUFFER = 0.05; // 5% padding on sides
const Y_BUFFER = 0.15; // 15% padding top/bottom

export const TierBar = ({ products, onHoverProduct, onSelectProduct }: TierBarProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // 1. Calculate Global Extremes (Price & Score)
  const { minPrice, maxPrice } = useMemo(() => {
    if (!products.length) return { minPrice: 0, maxPrice: 10000 };
    const prices = products.map(getPriceValue);
    return { minPrice: Math.min(...prices), maxPrice: Math.max(...prices) };
  }, [products]);

  // 2. Zoom State
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null);
  const currentMin = zoomDomain ? zoomDomain[0] : minPrice;
  const currentMax = zoomDomain ? zoomDomain[1] : maxPrice;
  const isZoomed = zoomDomain !== null;

  // 3. Smart Layout Engine (Collision Avoidance)
  // This runs whenever the product list or zoom changes.
  // It maps Price -> X and Score -> Y, then nudges overlapping nodes.
  const computedLayout = useMemo(() => {
    const rangeSpan = currentMax - currentMin || 1;
    
    // Initial Mapping
    let nodes = products.map(p => {
      const price = getPriceValue(p);
      const score = p.score || 50; // Use calculated score or default

      // Raw Coordinates (0.0 to 1.0)
      const rawX = (price - currentMin) / rangeSpan;
      const rawY = score / 100;

      return {
        id: p.id,
        product: p,
        price,
        // Clamp X to visual buffer
        x: X_BUFFER + (rawX * (1 - (X_BUFFER * 2))), 
        // Clamp Y to visual buffer
        y: Y_BUFFER + (rawY * (1 - (Y_BUFFER * 2))),
        visible: price >= currentMin && price <= currentMax
      };
    }).filter(n => n.visible);

    // Collision Resolution (Simple Iterative Nudge)
    // We do 3 passes to push nodes apart if they are too close
    const iterations = 3;
    const thresholdX = 0.03; // ~3% width overlap
    const thresholdY = 0.10; // ~10% height overlap

    for (let i = 0; i < iterations; i++) {
      // Sort by X to optimize checks
      nodes.sort((a, b) => a.x - b.x);

      for (let j = 0; j < nodes.length; j++) {
        const nodeA = nodes[j];
        for (let k = j + 1; k < nodes.length; k++) {
          const nodeB = nodes[k];
          
          // Optimization: If X distance is huge, stop checking this neighbor
          if (nodeB.x - nodeA.x > thresholdX) break;

          const diffX = Math.abs(nodeA.x - nodeB.x);
          const diffY = Math.abs(nodeA.y - nodeB.y);

          if (diffX < thresholdX && diffY < thresholdY) {
            // COLLISION DETECTED
            // Nudge Y apart (preserve X as much as possible because X is Price)
            const overlapY = thresholdY - diffY;
            const push = overlapY * 0.5;

            // Push the higher one up, lower one down
            if (nodeA.y > nodeB.y) {
               nodeA.y = Math.min(1 - Y_BUFFER, nodeA.y + push);
               nodeB.y = Math.max(Y_BUFFER, nodeB.y - push);
            } else {
               nodeB.y = Math.min(1 - Y_BUFFER, nodeB.y + push);
               nodeA.y = Math.max(Y_BUFFER, nodeA.y - push);
            }
          }
        }
      }
    }
    return nodes;
  }, [products, currentMin, currentMax]);


  // 4. Interaction (Zoom Handles)
  const [dragRange, setDragRange] = useState<[number, number]>([0, 1]);
  const [pullBackIntent, setPullBackIntent] = useState<"left" | "right" | null>(null);

  // Reset logic
  useEffect(() => {
    setZoomDomain(null);
    setDragRange([0, 1]);
  }, [products.length]); // Reset on category change

  return (
    <div className="w-full h-full relative group/tierbar select-none overflow-hidden bg-[#0a0a0c]" ref={containerRef}>
      
      {/* --- LAYER 0: THE GRID (Context) --- */}
      <div className="absolute inset-0 pointer-events-none opacity-20">
        {/* Y-Axis Zones */}
        <div className="absolute top-[10%] left-0 w-full border-t border-dashed border-amber-500/50 flex items-center">
            <span className="text-[9px] text-amber-500 font-mono pl-2 bg-[#0a0a0c]">TRENDING</span>
        </div>
        <div className="absolute top-[50%] left-0 w-full border-t border-zinc-800" />
        <div className="absolute bottom-[10%] left-0 w-full border-t border-dashed border-zinc-800 flex items-center">
            <span className="text-[9px] text-zinc-700 font-mono pl-2 bg-[#0a0a0c]">NICHE</span>
        </div>

        {/* X-Axis Grid (Dynamic) */}
        {[0.25, 0.5, 0.75].map(pct => (
          <div key={pct} className="absolute top-0 bottom-0 border-l border-zinc-800" style={{ left: `${pct * 100}%` }} />
        ))}
      </div>

      {/* --- LAYER 1: THE NODES --- */}
      <div className="absolute inset-0">
        <AnimatePresence>
          {computedLayout.map((node) => (
            <motion.button
              key={node.id}
              layoutId={node.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ 
                opacity: 1, 
                scale: 1, 
                left: `${node.x * 100}%`,
                bottom: `${node.y * 100}%` 
              }}
              exit={{ opacity: 0, scale: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 25 }}
              className="absolute w-12 h-12 -ml-6 -mb-6 flex items-center justify-center pointer-events-auto group/node z-10"
              onMouseEnter={() => onHoverProduct(node.product)}
              onClick={() => onSelectProduct(node.id)}
            >
              {/* Connection Line to Price Axis */}
              <div className="absolute top-1/2 left-1/2 w-px h-[500px] bg-gradient-to-b from-amber-500/20 to-transparent pointer-events-none opacity-0 group-hover/node:opacity-100 transition-opacity origin-top transform rotate-180" />

              {/* The Orb */}
              <div className="relative w-full h-full bg-zinc-900/90 backdrop-blur-md rounded-full border border-zinc-700 hover:border-amber-500 hover:scale-125 hover:shadow-[0_0_20px_rgba(245,158,11,0.5)] transition-all duration-200 overflow-hidden flex items-center justify-center p-1.5 z-20">
                <img
                  src={node.product.logo_url}
                  alt={node.product.brand}
                  className="w-full h-full object-contain opacity-80 group-hover/node:opacity-100 group-hover/node:invert"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                    // Simple text fallback
                    const parent = e.currentTarget.parentElement;
                    if (parent) parent.innerHTML = `<span class="text-[8px] font-bold text-zinc-500">${node.product.brand.substring(0,3)}</span>`;
                  }}
                />
              </div>

              {/* Price Tooltip (On Hover) */}
              <div className="absolute -bottom-6 left-1/2 -translate-x-1/2 opacity-0 group-hover/node:opacity-100 transition-opacity whitespace-nowrap z-30">
                <div className="bg-black/90 text-amber-500 text-[9px] font-mono px-2 py-0.5 rounded border border-amber-900/50">
                  ₪{Math.round(node.price).toLocaleString()}
                </div>
              </div>
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* --- LAYER 2: INTERACTION HANDLES (Curtains) --- */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Left Curtain */}
        <motion.div 
            animate={{ width: `${dragRange[0] * 100}%` }} 
            className={`absolute left-0 top-0 bottom-0 bg-black/60 backdrop-blur-[2px] border-r border-amber-500/30 z-40 transition-colors ${
                pullBackIntent === "left" ? "bg-red-500/10 border-red-500/50" : ""
            }`}
        >
           {/* Left Handle */}
           <div
            className={`absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 h-16 min-w-[3rem] px-3 rounded-lg flex flex-col items-center justify-center cursor-ew-resize pointer-events-auto shadow-xl border transition-all z-50 ${
              pullBackIntent === "left"
                ? "bg-red-900/80 border-red-500 text-red-200"
                : "bg-zinc-800 hover:bg-zinc-700 border-zinc-600 text-white"
            }`}
             onMouseDown={(e) => {
              const startX = e.clientX;
              const width = containerRef.current?.offsetWidth || 1;

              const onMove = (moveE: MouseEvent) => {
                const deltaPx = moveE.clientX - startX;
                const deltaPct = deltaPx / width;

                // Logic for Left Handle (Starts at 0)
                if (isZoomed && deltaPct < -0.05) {
                  setPullBackIntent("left");
                  setDragRange([0, dragRange[1]]); 
                } else {
                  setPullBackIntent(null);
                  const newVal = Math.max(0, Math.min(dragRange[1] - 0.1, deltaPct));
                  setDragRange([newVal, dragRange[1]]);
                }
              };

              const onUp = (upE: MouseEvent) => {
                window.removeEventListener("mousemove", onMove);
                window.removeEventListener("mouseup", onUp);

                const deltaPx = upE.clientX - startX;
                const deltaPct = deltaPx / width;

                if (isZoomed && deltaPct < -0.05) {
                  setZoomDomain(null);
                  setPullBackIntent(null);
                  setDragRange([0, 1]);
                } else {
                  const newVal = Math.max(0, Math.min(0.9, deltaPct));
                  if (newVal > 0.05) {
                    const span = currentMax - currentMin;
                    const newMinPrice = currentMin + newVal * span;
                    setZoomDomain([newMinPrice, currentMax]);
                  }
                  setDragRange([0, 1]); 
                  setPullBackIntent(null);
                }
              };
              window.addEventListener("mousemove", onMove);
              window.addEventListener("mouseup", onUp);
            }}
           >
            {pullBackIntent === "left" ? (
              <RotateCcw className="w-4 h-4 animate-spin-slow" />
            ) : (
              <div className="flex flex-col items-center">
                <span className="text-[9px] text-zinc-400 font-mono tracking-wider mb-0.5">MIN</span>
                <span className="font-bold font-mono tracking-tighter">₪{Math.round(currentMin + dragRange[0] * (currentMax - currentMin)).toLocaleString()}</span>
              </div>
            )}
           </div>
        </motion.div>

        {/* Right Curtain */}
        <motion.div 
            animate={{ width: `${(1 - dragRange[1]) * 100}%` }} 
            className={`absolute right-0 top-0 bottom-0 bg-black/60 backdrop-blur-[2px] border-l border-amber-500/30 z-40 transition-colors ${
                pullBackIntent === "right" ? "bg-red-500/10 border-red-500/50" : ""
            }`}
        >
           {/* Right Handle */}
           <div
            className={`absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 h-16 min-w-[3rem] px-3 rounded-lg flex flex-col items-center justify-center cursor-ew-resize pointer-events-auto shadow-xl border transition-all z-50 ${
                pullBackIntent === "right"
                  ? "bg-red-900/80 border-red-500 text-red-200"
                  : "bg-zinc-800 hover:bg-zinc-700 border-zinc-600 text-white"
              }`}
             onMouseDown={(e) => {
              const startX = e.clientX;
              const width = containerRef.current?.offsetWidth || 1;

              const onMove = (moveE: MouseEvent) => {
                const deltaPx = moveE.clientX - startX;
                const deltaPct = deltaPx / width;

                // Logic for Right Handle (Starts at 1.0)
                if (isZoomed && deltaPct > 0.05) {
                  setPullBackIntent("right");
                  setDragRange([dragRange[0], 1]);
                } else {
                  setPullBackIntent(null);
                  const newVal = Math.min(1, Math.max(dragRange[0] + 0.1, 1 + deltaPct));
                  setDragRange([dragRange[0], newVal]);
                }
              };

              const onUp = (upE: MouseEvent) => {
                window.removeEventListener("mousemove", onMove);
                window.removeEventListener("mouseup", onUp);

                const deltaPx = upE.clientX - startX;
                const deltaPct = deltaPx / width;

                if (isZoomed && deltaPct > 0.05) {
                  setZoomDomain(null);
                  setPullBackIntent(null);
                  setDragRange([0, 1]);
                } else {
                  const newVal = Math.min(1, Math.max(dragRange[0] + 0.1, 1 + deltaPct));
                  if (newVal < 0.95) {
                    const span = currentMax - currentMin;
                    const newMaxPrice = currentMin + newVal * span;
                    setZoomDomain([currentMin, newMaxPrice]);
                  }
                  setDragRange([0, 1]);
                  setPullBackIntent(null);
                }
              };
              window.addEventListener("mousemove", onMove);
              window.addEventListener("mouseup", onUp);
            }}
           >
            {pullBackIntent === "right" ? (
              <RotateCcw className="w-4 h-4 animate-spin-slow" />
            ) : (
              <div className="flex flex-col items-center">
                <span className="text-[9px] text-zinc-400 font-mono tracking-wider mb-0.5">MAX</span>
                <span className="font-bold font-mono tracking-tighter">₪{Math.round(currentMin + dragRange[1] * (currentMax - currentMin)).toLocaleString()}</span>
              </div>
            )}
           </div>
        </motion.div>
      </div>

      {/* --- FOOTER: Axis Labels --- */}
      <div className="absolute bottom-1 inset-x-4 flex justify-between text-[10px] text-zinc-600 font-mono border-t border-zinc-800 pt-1">
        <span>MIN: ₪{Math.round(currentMin).toLocaleString()}</span>
        <span className="text-zinc-800">PRICE SPECTRUM</span>
        <span>MAX: ₪{Math.round(currentMax).toLocaleString()}</span>
      </div>

      {/* Zoom Indicator */}
      <AnimatePresence>
        {isZoomed && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-amber-500 text-black px-3 py-1 rounded-full text-xs font-bold shadow-xl z-50 pointer-events-none"
          >
            <ZoomIn className="w-3 h-3" /> ZOOM ACTIVE
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
