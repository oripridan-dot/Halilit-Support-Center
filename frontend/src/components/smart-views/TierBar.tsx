import { AnimatePresence, motion } from "framer-motion";
import { RotateCcw, ZoomIn } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { Product } from "../../types";

// TierBarProduct is a type alias for Product with extended functionality
export type TierBarProduct = Product;

interface TierBarProps {
  products: Product[];
  onHoverProduct: (product: Product | null) => void;
  onSelectProduct: (productId: string) => void;
}

export const TierBar = ({
  products,
  onHoverProduct,
  onSelectProduct,
}: TierBarProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // 1. Calculate Global Price Extremes (Stable across zooms)
  const { globalMin, globalMax } = useMemo(() => {
    if (!products.length) return { globalMin: 0, globalMax: 10000 };
    const prices = products.map((p) => {
      const pricing =
        typeof p.pricing === "number" ? p.pricing : p.pricing?.regular_price;
      return pricing ?? p.price ?? 0;
    });
    return { globalMin: Math.min(...prices), globalMax: Math.max(...prices) };
  }, [products]);

  // 2. Zoom State (The actual viewport)
  // null = showing full global range
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null);

  const currentMin = zoomDomain ? zoomDomain[0] : globalMin;
  const currentMax = zoomDomain ? zoomDomain[1] : globalMax;
  const isZoomed = zoomDomain !== null;

  // 3. Curtain Interaction State
  // [leftCurtainPos, rightCurtainPos] (0.0 to 1.0)
  // Always snaps back to [0, 1] after interaction
  const [dragRange, setDragRange] = useState<[number, number]>([0, 1]);
  const [pullBackIntent, setPullBackIntent] = useState<"left" | "right" | null>(
    null,
  );
  // Reset zoom when product set changes significantly
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setZoomDomain(null);

    setDragRange([0, 1]);
  }, [products.length, globalMin, globalMax]);

  // Helper: Get visual position % within Current View
  // We add a 4% buffer on each side so logos typically stay inside the rail lines
  const getPosition = (price: number) => {
    const rangeSpan = currentMax - currentMin;
    if (rangeSpan === 0) return 50;

    const rawPct = (price - currentMin) / rangeSpan;
    // Compress 0..1 -> 0.04..0.96
    return (0.04 + rawPct * 0.92) * 100;
  };

  // Helper: Check if product is visible in current view
  const isVisible = (price: number) => {
    return price >= currentMin && price <= currentMax;
  };

  return (
    <div
      className="w-full h-64 relative flex flex-col justify-end pb-8 group/tierbar select-none"
      ref={containerRef}
    >
      {/* ---------------------------------------------------------
          LAYER 0: STATE INDICATOR
         --------------------------------------------------------- */}
      <AnimatePresence>
        {isZoomed && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-0 right-0 left-0 flex justify-center items-center pointer-events-none"
          >
            <div className="bg-amber-500/10 text-amber-500 text-xs font-mono px-3 py-1 rounded-full border border-amber-500/20 flex items-center gap-2 backdrop-blur-md">
              <ZoomIn className="w-3 h-3" />
              <span>ZOOM ACTIVE</span>
              <span className="opacity-50">|</span>
              <span className="text-[10px]">PULL BACK TO RESET</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ---------------------------------------------------------
          LAYER 1: THE PRODUCT LOGO FIELD
         --------------------------------------------------------- */}
      <div className="absolute inset-x-0 bottom-16 top-0 overflow-hidden mx-12">
        <AnimatePresence mode="popLayout">
          {products.map((product) => {
            const pricing =
              typeof product.pricing === "number"
                ? product.pricing
                : product.pricing?.regular_price;
            const productPrice = pricing ?? product.price ?? 0;
            if (!isVisible(productPrice)) return null;

            const position = getPosition(productPrice);

            // Randomize Y slightly to avoid total overlap
            // 20% to 60% range keeps it more centered vertically
            const yOffset =
              20 + (product.id.charCodeAt(product.id.length - 1) % 40);

            return (
              <motion.button
                key={product.id}
                layout // This enables the "Space" out animation when zoom changes
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1, left: `${position}%` }}
                exit={{ opacity: 0, scale: 0 }}
                transition={{ type: "spring", stiffness: 300, damping: 30 }}
                className="absolute w-16 h-16 -ml-8 flex items-center justify-center pointer-events-auto"
                style={{ bottom: `${yOffset}%` }}
                onMouseEnter={() => onHoverProduct(product)}
                onClick={() => onSelectProduct(product.id)}
              >
                {/* Connecting Line to Axis */}
                <div className="absolute top-full left-1/2 w-px h-32 bg-gradient-to-b from-amber-500/50 to-transparent pointer-events-none group-hover:from-amber-400" />

                {/* The Logo Orb */}
                <div className="relative w-full h-full bg-black/80 backdrop-blur-sm rounded-lg border border-transparent hover:border-amber-500 hover:shadow-[0_0_15px_rgba(245,158,11,0.6)] flex items-center justify-center p-2 transition-all duration-200 overflow-hidden">
                  <img
                    src={product.logo_url}
                    alt={product.brand}
                    className="w-full h-full object-contain opacity-90"
                    onError={(e) => {
                      // Fallback: use product brand text
                      e.currentTarget.style.display = "none";
                      const parent = e.currentTarget.parentElement;
                      if (parent && !parent.querySelector(".brand-fallback")) {
                        const span = document.createElement("div");
                        span.className =
                          "brand-fallback text-[8px] font-bold text-amber-500 text-center px-1 leading-tight";
                        span.textContent = product.brand.split(" ")[0];
                        parent.appendChild(span);
                      }
                    }}
                  />
                </div>
              </motion.button>
            );
          })}
        </AnimatePresence>
      </div>

      {/* ---------------------------------------------------------
          LAYER 2: THE BASE AXIS (Rail)
         --------------------------------------------------------- */}
      <div className="relative h-1 bg-zinc-800 rounded-full mx-12 overflow-hidden">
        {/* We don't need active range highlight anymore because the VIEW is the active range */}
        <div className="absolute inset-0 bg-zinc-700/30" />
      </div>

      {/* ---------------------------------------------------------
          LAYER 3: THE ZOOM CURTAINS (Interaction Layer)
         --------------------------------------------------------- */}
      <div className="absolute inset-0 pointer-events-none mx-12">
        {/* LEFT CURTAIN */}
        <motion.div
          animate={{ width: `${dragRange[0] * 100}%` }}
          transition={{ type: "spring", bounce: 0, duration: 0.2 }}
          className={`absolute top-0 bottom-0 left-0 backdrop-blur-sm border-r border-zinc-700 z-20 transition-colors ${
            pullBackIntent === "left"
              ? "bg-red-500/10 border-red-500/50"
              : "bg-black/80"
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
                // Dragging Right (+): Zoom In
                // Dragging Left (-): Pull Back (if zoomed)

                if (isZoomed && deltaPct < -0.05) {
                  setPullBackIntent("left");
                  setDragRange([0, dragRange[1]]); // Keep visual at 0
                } else {
                  setPullBackIntent(null);
                  const newVal = Math.max(
                    0,
                    Math.min(dragRange[1] - 0.1, deltaPct),
                  ); // Base 0 + delta
                  setDragRange([newVal, dragRange[1]]);
                }
              };

              const onUp = (upE: MouseEvent) => {
                window.removeEventListener("mousemove", onMove);
                window.removeEventListener("mouseup", onUp);

                // Calculate outcome based on final mouse pos
                const deltaPx = upE.clientX - startX;
                const deltaPct = deltaPx / width;

                if (isZoomed && deltaPct < -0.05) {
                  // EXECUTE RESET
                  setZoomDomain(null);
                  setPullBackIntent(null);
                  setDragRange([0, 1]);
                } else {
                  // EXECUTE ZOOM
                  const newVal = Math.max(0, Math.min(0.9, deltaPct));
                  if (newVal > 0.05) {
                    // Calculate new min price
                    const span = currentMax - currentMin;
                    const newMinPrice = currentMin + newVal * span;
                    setZoomDomain([newMinPrice, currentMax]);
                  }
                  setDragRange([0, 1]); // Snap back
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

        {/* RIGHT CURTAIN */}
        <motion.div
          animate={{ width: `${(1 - dragRange[1]) * 100}%` }}
          transition={{ type: "spring", bounce: 0, duration: 0.2 }}
          className={`absolute top-0 bottom-0 right-0 backdrop-blur-sm border-l border-zinc-700 z-20 transition-colors ${
            pullBackIntent === "right"
              ? "bg-red-500/10 border-red-500/50"
              : "bg-black/80"
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
                // Dragging Left (-): Zoom In
                // Dragging Right (+): Pull Back (if zoomed)

                if (isZoomed && deltaPct > 0.05) {
                  setPullBackIntent("right");
                  setDragRange([dragRange[0], 1]); // Keep visual at 100%
                } else {
                  setPullBackIntent(null);
                  // Base 1 + delta. e.g. 1 + (-0.2) = 0.8
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
                  // EXECUTE RESET
                  setZoomDomain(null);
                  setPullBackIntent(null);
                  setDragRange([0, 1]);
                } else {
                  // EXECUTE ZOOM
                  // 1 + (-0.2) = 0.8
                  const newVal = Math.min(
                    1,
                    Math.max(dragRange[0] + 0.1, 1 + deltaPct),
                  );

                  if (newVal < 0.95) {
                    const span = currentMax - currentMin;
                    // newMax = min + percentage * span
                    const newMaxPrice = currentMin + newVal * span;
                    setZoomDomain([currentMin, newMaxPrice]);
                  }
                  setDragRange([0, 1]); // Snap back
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

      {/* Range Info Footer */}
      <div className="absolute -bottom-6 inset-x-0 flex justify-between px-4 text-[10px] text-zinc-500 font-mono">
        <span>₪{Math.round(currentMin).toLocaleString()}</span>
        <span>₪{Math.round(currentMax).toLocaleString()}</span>
      </div>
    </div>
  );
};
