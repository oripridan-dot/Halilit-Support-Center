import { motion } from "framer-motion";

interface CockpitSkeletonProps {
  statusMessage?: string;
  brandColor?: string;
}

/**
 * Loading skeleton for the Product Cockpit.
 * Shows animated placeholders that match the final bento grid layout.
 */
export const CockpitSkeleton = ({
  statusMessage = "Initializing...",
  brandColor = "#3b82f6",
}: CockpitSkeletonProps) => {
  const pulse = "animate-pulse";

  return (
    <div className="space-y-4">
      {/* Status indicator */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3 px-4 py-3 rounded-xl border border-zinc-800/50 bg-zinc-900/50"
      >
        <div
          className="w-2 h-2 rounded-full animate-pulse"
          style={{ backgroundColor: brandColor }}
        />
        <span className="text-xs text-zinc-400 font-medium">
          {statusMessage}
        </span>
        <div className="ml-auto flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-zinc-600"
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.2, delay: i * 0.2, repeat: Infinity }}
            />
          ))}
        </div>
      </motion.div>

      {/* Bento grid skeleton */}
      <div className="grid grid-cols-12 gap-4">
        {/* Left: Hero image placeholder */}
        <div className={`col-span-4 space-y-3`}>
          <div
            className={`aspect-square rounded-xl bg-zinc-900/60 border border-zinc-800/40 ${pulse}`}
          />
          <div className="flex gap-2">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className={`w-14 h-14 rounded-lg bg-zinc-900/50 ${pulse}`}
              />
            ))}
          </div>
        </div>

        {/* Right: Smart card placeholders */}
        <div className="col-span-8 space-y-3">
          {/* Verdict card skeleton */}
          <div
            className={`h-32 rounded-xl bg-zinc-900/60 border border-zinc-800/40 p-4 ${pulse}`}
          >
            <div className="h-3 w-24 bg-zinc-800 rounded mb-3" />
            <div className="h-2 w-full bg-zinc-800/60 rounded mb-2" />
            <div className="h-2 w-4/5 bg-zinc-800/60 rounded mb-4" />
            <div className="flex gap-2">
              <div className="h-5 w-16 bg-zinc-800/40 rounded-full" />
              <div className="h-5 w-20 bg-zinc-800/40 rounded-full" />
              <div className="h-5 w-14 bg-zinc-800/40 rounded-full" />
            </div>
          </div>

          {/* Two-column row */}
          <div className="grid grid-cols-2 gap-3">
            {/* Specs skeleton */}
            <div
              className={`h-40 rounded-xl bg-zinc-900/60 border border-zinc-800/40 p-4 ${pulse}`}
            >
              <div className="h-3 w-20 bg-zinc-800 rounded mb-3" />
              <div className="space-y-2">
                {[0, 1, 2, 3].map((i) => (
                  <div key={i} className="flex justify-between">
                    <div className="h-2 w-20 bg-zinc-800/50 rounded" />
                    <div className="h-2 w-16 bg-zinc-800/50 rounded" />
                  </div>
                ))}
              </div>
            </div>

            {/* Trusted consensus skeleton */}
            <div
              className={`h-40 rounded-xl bg-zinc-900/60 border border-zinc-800/40 p-4 ${pulse}`}
            >
              <div className="h-3 w-28 bg-zinc-800 rounded mb-3" />
              <div className="flex gap-3 mb-3">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-8 h-8 rounded-lg bg-zinc-800/50"
                  />
                ))}
              </div>
              <div className="h-2 w-full bg-zinc-800/40 rounded" />
            </div>
          </div>

          {/* Field notes skeleton */}
          <div
            className={`h-24 rounded-xl bg-zinc-900/60 border border-zinc-800/40 p-4 ${pulse}`}
          >
            <div className="h-3 w-24 bg-zinc-800 rounded mb-3" />
            <div className="flex gap-2">
              <div className="h-6 w-full bg-zinc-800/40 rounded-lg" />
              <div className="h-6 w-full bg-zinc-800/40 rounded-lg" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
