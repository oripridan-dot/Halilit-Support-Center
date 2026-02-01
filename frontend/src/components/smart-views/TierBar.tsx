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
const X_BUFFER = 0.1; // 10% padding on sides
const Y_BUFFER = 0.2; // 20% padding top/bottom

export const TierBar = ({
  products,
  onHoverProduct,
  onSelectProduct,
}: TierBarProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // 1. Calculate Statistics & Scale
  const { minPrice, maxPrice, lowerFence, upperFence } = useMemo(() => {
    if (!products.length)
      return { minPrice: 0, maxPrice: 10000, lowerFence: 0, upperFence: 10000 };

    // Sort prices to find distribution
    const prices = products.map(getPriceValue).sort((a, b) => a - b);
    const min = prices[0];
    const max = prices[prices.length - 1];

    // Find Interquartile Range to ignore extreme outliers for default view
    const q1Index = Math.floor(prices.length * 0.25);
    const q3Index = Math.floor(prices.length * 0.75);
    const q1 = prices[q1Index] || min;
    const q3 = prices[q3Index] || max;
    const iqr = q3 - q1;

    // Calculate "Fences" (The meaningful range)
    // We expand slightly to include "most" items but cut off the "far priced" ones
    // Using 1.5 * IQR is standard statistic outlier detection
    let lower = Math.max(0, q1 - iqr * 1.5);
    let upper = q3 + iqr * 1.5;

    // Safety clamp if distribution is too tight
    if (upper <= lower + 100) {
      lower = min;
      upper = max;
    }

    return {
      minPrice: min,
      maxPrice: max,
      lowerFence: lower,
      upperFence: upper,
    };
  }, [products]);

  // 2. Zoom State
  // Initial state is "Fence" (Smart Focus), not "Full Range"
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null);
  const currentMin = zoomDomain ? zoomDomain[0] : lowerFence;
  const currentMax = zoomDomain ? zoomDomain[1] : upperFence;
  const isZoomed =
    zoomDomain !== null || currentMin !== minPrice || currentMax !== maxPrice;

  // 3. Smart Layout Engine (Collision Avoidance + Log Scale)
  const computedLayout = useMemo(() => {
    const rangeSpan = Math.log(currentMax) - Math.log(Math.max(1, currentMin)); // Logarithmic Span

    // Initial Mapping
    const nodes = products.map((p) => {
      const price = getPriceValue(p);
      const score = p.tier_score || 50;

      // Outlier Detection
      const isOutlierLow = price < currentMin;
      const isOutlierHigh = price > currentMax;

      let rawX;

      if (isOutlierHigh) {
        rawX = 1.02; // Push off-screen right
      } else if (isOutlierLow) {
        rawX = -0.02; // Push off-screen left
      } else {
        // Logarithmic Scaling for X
        // This expands the "center mass" of cheaper items and compresses high end
        // log(x) - log(min) / log(max) - log(min)
        const safePrice = Math.max(1, price);
        const safeMin = Math.max(1, currentMin);
        rawX = (Math.log(safePrice) - Math.log(safeMin)) / rangeSpan;
      }

      // Linear Scaling for Y (Score)
      const rawY = score / 100;

      return {
        id: p.id,
        product: p,
        price,
        // Clamp X to visual buffer if visible
        x:
          isOutlierHigh || isOutlierLow
            ? rawX
            : X_BUFFER + rawX * (1 - X_BUFFER * 2),
        y: Y_BUFFER + rawY * (1 - Y_BUFFER * 2),
        visible: !isOutlierHigh && !isOutlierLow,
        outlier: isOutlierHigh ? "high" : isOutlierLow ? "low" : false,
      };
    });

    const visibleNodes = nodes.filter((n) => n.visible);

    // Collision Resolution (Iterative Relaxation)
    const iterations = 15; // Higher iterations for denser clusters
    const thresholdX = 0.035;
    const thresholdY = 0.1;

    for (let i = 0; i < iterations; i++) {
      visibleNodes.sort((a, b) => a.x - b.x);
      const alpha = 1.0 - i / iterations;

      for (let j = 0; j < visibleNodes.length; j++) {
        const nodeA = visibleNodes[j];
        for (let k = j + 1; k < visibleNodes.length; k++) {
          const nodeB = visibleNodes[k];

          if (nodeB.x - nodeA.x > thresholdX) break;

          const diffX = Math.abs(nodeA.x - nodeB.x);
          const diffY = Math.abs(nodeA.y - nodeB.y);

          if (diffX < thresholdX && diffY < thresholdY) {
            const overlapY = thresholdY - diffY;
            const overlapX = thresholdX - diffX;

            const pushY = overlapY * 0.6 * alpha;
            const pushX = overlapX * 0.2 * alpha;

            if (nodeA.y > nodeB.y) {
              nodeA.y = Math.min(0.95, nodeA.y + pushY);
              nodeB.y = Math.max(0.05, nodeB.y - pushY);
            } else {
              nodeB.y = Math.min(0.95, nodeB.y + pushY);
              nodeA.y = Math.max(0.05, nodeA.y - pushY);
            }

            if (nodeA.x > nodeB.x) {
              nodeA.x = Math.min(0.98, nodeA.x + pushX);
              nodeB.x = Math.max(0.02, nodeB.x - pushX);
            } else {
              nodeB.x = Math.min(0.98, nodeB.x + pushX);
              nodeA.x = Math.max(0.02, nodeA.x - pushX);
            }
          }
        }
      }
    }

    // Re-merge with outliers for rendering logic
    return { visibleNodes, outliers: nodes.filter((n) => n.outlier) };
  }, [products, currentMin, currentMax]);

  // 4. Interaction (Zoom Handles)
  const [dragRange, setDragRange] = useState<[number, number]>([0, 1]);
  const [pullBackIntent, setPullBackIntent] = useState<"left" | "right" | null>(
    null,
  );
  const [hoveredProductId, setHoveredProductId] = useState<string | null>(null);

  // Reset logic
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setZoomDomain(null);
    setDragRange([0, 1]);
  }, [products.length]); // Reset on category change

  return (
    <div
      className="w-full h-full relative group/tierbar select-none overflow-hidden bg-[#0a0a0c]"
      ref={containerRef}
    >
      {/* --- LAYER 0: THE GRID (Context) --- */}
      <div className="absolute inset-0 pointer-events-none opacity-40">
        {/* Y-Axis Background Gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-amber-900/5 via-transparent to-transparent pointer-events-none" />

        {/* Y-Axis Zones */}
        <div className="absolute top-[15%] left-0 w-full border-t border-dashed border-zinc-800 flex items-center group/zone">
          <span className="text-[9px] text-zinc-600 font-mono pl-2">
            HIGH TIER
          </span>
        </div>

        <div className="absolute top-[50%] left-0 w-full border-t border-zinc-800" />

        <div className="absolute bottom-[15%] left-0 w-full border-t border-dashed border-zinc-800 flex items-center">
          <span className="text-[9px] text-zinc-700 font-mono pl-2">
            ENTRY LEVEL
          </span>
        </div>

        {/* X-Axis Grid (Price Intervals) */}
        {Array.from({ length: 9 }).map((_, i) => {
          const pct = (i + 1) * 0.1;
          const isMajor = i === 4; // Center line (50%)
          return (
            <div
              key={pct}
              className={`absolute top-0 bottom-0 border-l ${isMajor ? "border-zinc-700" : "border-zinc-800/50"}`}
              style={{ left: `${pct * 100}%` }}
            >
              {isMajor && (
                <div className="absolute bottom-1 right-1 text-[9px] text-zinc-600 font-mono rotate-90 origin-bottom-right">
                  MEDIAN
                </div>
              )}
            </div>
          );
        })}

        {/* Dynamic Price Labels on Bottom Axis */}
        <div className="absolute bottom-0 w-full flex justify-between px-4 py-2 text-[10px] text-zinc-400 font-bold font-mono tracking-wider z-20">
          <span>₪{Math.round(currentMin).toLocaleString()}</span>
          <span className="opacity-50">
            ₪
            {Math.round(
              currentMin + (currentMax - currentMin) * 0.25,
            ).toLocaleString()}
          </span>
          <span className="text-amber-500">
            ₪
            {Math.round(
              currentMin + (currentMax - currentMin) * 0.5,
            ).toLocaleString()}
          </span>
          <span className="opacity-50">
            ₪
            {Math.round(
              currentMin + (currentMax - currentMin) * 0.75,
            ).toLocaleString()}
          </span>
          <span>₪{Math.round(currentMax).toLocaleString()}</span>
        </div>
      </div>

      {/* --- LAYER 1: THE NODES --- */}
      <div className="absolute inset-0">
        <AnimatePresence>
          {computedLayout.visibleNodes.map((node) => (
            <motion.button
              key={node.id}
              layoutId={node.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: 1,
                scale: 1,
                left: `${node.x * 100}%`,
                bottom: `${node.y * 100}%`,
              }}
              exit={{ opacity: 0, scale: 0 }}
              transition={{ type: "spring", stiffness: 200, damping: 25 }}
              className="absolute w-12 h-12 -ml-6 -mb-6 flex items-center justify-center pointer-events-auto group/node z-10"
              onMouseEnter={() => {
                onHoverProduct(node.product);
                setHoveredProductId(node.id ?? null);
              }}
              onMouseLeave={() => {
                onHoverProduct(null);
                setHoveredProductId(null);
              }}
              onClick={() => onSelectProduct(node.id ?? "")}
            >
              {/* Connection Line to Price Axis */}
              <div className="absolute top-1/2 left-1/2 w-px h-[500px] bg-gradient-to-b from-amber-500/20 to-transparent pointer-events-none opacity-0 group-hover/node:opacity-100 transition-opacity origin-top transform rotate-180" />

              {/* The Orb */}
              <div className="relative w-full h-full bg-zinc-900/90 backdrop-blur-md rounded-full border border-zinc-700 hover:border-amber-500 hover:scale-125 hover:shadow-[0_0_20px_rgba(245,158,11,0.5)] transition-all duration-200 overflow-hidden flex items-center justify-center p-1.5 z-20">
                <span className="text-[8px] font-bold text-zinc-500">
                  {(node.product.brand_id ?? "").substring(0, 3).toUpperCase()}
                </span>
              </div>

              {/* Price Tooltip (On Hover) */}
              <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 opacity-0 group-hover/node:opacity-100 transition-opacity whitespace-nowrap z-50 pointer-events-none">
                <div className="bg-black text-amber-500 text-[10px] font-bold font-mono px-2 py-1 rounded border border-amber-500/50 shadow-xl">
                  {node.product.currency}{" "}
                  {Math.round(node.price).toLocaleString()}
                </div>
              </div>
            </motion.button>
          ))}

          {/* Outliers Indication */}
          {computedLayout.outliers.map((node) => (
            <motion.button
              key={node.id}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: 0.5,
                scale: 0.8,
                left: node.outlier === "high" ? "98%" : "2%",
                bottom: `${node.y * 100}%`,
              }}
              className="absolute w-6 h-6 -ml-3 -mb-3 flex items-center justify-center pointer-events-auto group/outlier z-5"
              onMouseEnter={() => {
                onHoverProduct(node.product);
                setHoveredProductId(node.id ?? null);
              }}
              onMouseLeave={() => {
                onHoverProduct(null);
                setHoveredProductId(null);
              }}
              onClick={() => onSelectProduct(node.id ?? "")}
            >
              <div className="w-2 h-2 rounded-full bg-zinc-600 group-hover/outlier:bg-amber-500 group-hover/outlier:scale-150 transition-all" />
            </motion.button>
          ))}
        </AnimatePresence>
      </div>

      {/* --- LAYER 2: INTERACTION HANDLES (Curtains) --- */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Left Curtain */}
        <motion.div
          animate={{ width: `${dragRange[0] * 100}%` }}
          className={`absolute left-0 top-0 bottom-0 bg-black/80 backdrop-blur-sm border-r-2 border-amber-500/50 z-40 transition-colors shadow-[5px_0_20px_rgba(0,0,0,0.5)] ${
            pullBackIntent === "left" ? "bg-red-950/40 border-red-500/50" : ""
          }`}
        >
          {/* Left Handle */}
          <div
            className={`absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 h-20 min-w-[3.5rem] px-3 rounded-lg flex flex-col items-center justify-center cursor-ew-resize pointer-events-auto shadow-2xl border-2 transition-all z-50 ${
              pullBackIntent === "left"
                ? "bg-red-900 border-red-500 text-red-100 scale-110"
                : "bg-zinc-800 hover:bg-zinc-700 border-amber-500/50 text-white hover:scale-110"
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
                  const newVal = Math.max(
                    0,
                    Math.min(dragRange[1] - 0.1, deltaPct),
                  );
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
                <span className="text-[9px] text-zinc-400 font-mono tracking-wider mb-0.5">
                  MIN
                </span>
                <span className="font-bold font-mono tracking-tighter">
                  ₪
                  {Math.round(
                    currentMin + dragRange[0] * (currentMax - currentMin),
                  ).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Right Curtain */}
        <motion.div
          animate={{ width: `${(1 - dragRange[1]) * 100}%` }}
          className={`absolute right-0 top-0 bottom-0 bg-black/80 backdrop-blur-sm border-l-2 border-amber-500/50 z-40 transition-colors shadow-[-5px_0_20px_rgba(0,0,0,0.5)] ${
            pullBackIntent === "right" ? "bg-red-950/40 border-red-500/50" : ""
          }`}
        >
          {/* Right Handle */}
          <div
            className={`absolute left-0 top-1/2 -translate-y-1/2 -translate-x-1/2 h-20 min-w-[3.5rem] px-3 rounded-lg flex flex-col items-center justify-center cursor-ew-resize pointer-events-auto shadow-2xl border-2 transition-all z-50 ${
              pullBackIntent === "right"
                ? "bg-red-900 border-red-500 text-red-100 scale-110"
                : "bg-zinc-800 hover:bg-zinc-700 border-amber-500/50 text-white hover:scale-110"
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
                  const newVal = Math.min(
                    1,
                    Math.max(dragRange[0] + 0.1, 1 + deltaPct),
                  );
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
                  const newVal = Math.min(
                    1,
                    Math.max(dragRange[0] + 0.1, 1 + deltaPct),
                  );
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
                <span className="text-[9px] text-zinc-400 font-mono tracking-wider mb-0.5">
                  MAX
                </span>
                <span className="font-bold font-mono tracking-tighter">
                  ₪
                  {Math.round(
                    currentMin + dragRange[1] * (currentMax - currentMin),
                  ).toLocaleString()}
                </span>
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
