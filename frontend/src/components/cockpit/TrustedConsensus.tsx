import { motion } from "framer-motion";
import { ExternalLink } from "lucide-react";

export interface ReviewSource {
  source: string;
  logo?: string;
  summary: string;
  url?: string;
  sentiment?: "positive" | "neutral" | "negative";
  score?: number;
}

interface TrustedConsensusProps {
  reviews: ReviewSource[];
  brandColor?: string;
  isLoading?: boolean;
}

const SENTIMENT_COLORS = {
  positive: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  neutral: "text-zinc-400 bg-zinc-500/10 border-zinc-500/20",
  negative: "text-orange-400 bg-orange-500/10 border-orange-500/20",
};

/**
 * TrustedConsensus — Review source logos + aggregate scores from Golden Circle.
 */
export const TrustedConsensus = ({
  reviews,
  brandColor = "#3b82f6",
  isLoading = false,
}: TrustedConsensusProps) => {
  if (isLoading) {
    return (
      <div className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 animate-pulse">
        <div className="h-3 w-28 bg-zinc-800 rounded mb-3" />
        <div className="flex gap-3 mb-3">
          {[0, 1, 2].map((i) => (
            <div key={i} className="w-8 h-8 rounded-lg bg-zinc-800/50" />
          ))}
        </div>
        <div className="h-2 w-full bg-zinc-800/40 rounded" />
      </div>
    );
  }

  if (!reviews || reviews.length === 0) return null;

  const avgScore =
    reviews.filter((r) => r.score).reduce((a, b) => a + (b.score || 0), 0) /
    (reviews.filter((r) => r.score).length || 1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1, ease: "easeOut" }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 relative overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Trusted Reviews
        </span>
        {avgScore > 0 && (
          <span
            className="ml-auto text-sm font-black tabular-nums"
            style={{ color: brandColor }}
          >
            {avgScore.toFixed(1)}/10
          </span>
        )}
      </div>

      {/* Review source cards */}
      <div className="space-y-2.5">
        {reviews.map((review, i) => (
          <div
            key={i}
            className="flex items-start gap-3 p-3 rounded-lg bg-zinc-800/30 border border-zinc-800/30 hover:border-zinc-700/50 transition-colors group"
          >
            {/* Source logo/icon */}
            <div className="w-8 h-8 rounded-lg bg-white/5 flex items-center justify-center shrink-0 overflow-hidden">
              {review.logo ? (
                <img
                  src={review.logo}
                  alt={review.source}
                  className="w-6 h-6 object-contain"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              ) : (
                <span className="text-[10px] font-bold text-zinc-500">
                  {review.source.slice(0, 2).toUpperCase()}
                </span>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-zinc-300">
                  {review.source}
                </span>
                {review.sentiment && (
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full border ${SENTIMENT_COLORS[review.sentiment]}`}
                  >
                    {review.sentiment}
                  </span>
                )}
                {review.score && (
                  <span className="text-[10px] font-bold text-zinc-500 ml-auto tabular-nums">
                    {review.score}/10
                  </span>
                )}
              </div>
              <p className="text-[11px] text-zinc-500 line-clamp-2 leading-relaxed">
                {review.summary}
              </p>
            </div>

            {/* Link */}
            {review.url && (
              <a
                href={review.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 rounded-md hover:bg-zinc-700/50 text-zinc-600 hover:text-zinc-400 transition-colors opacity-0 group-hover:opacity-100 shrink-0"
              >
                <ExternalLink size={12} />
              </a>
            )}
          </div>
        ))}
      </div>
    </motion.div>
  );
};
