/**
 * ComparisonPanel — Side-by-side product comparison (self-fetching)
 *
 * Accepts productId + targetId and fetches comparison via the JIT explore API.
 * Displays AI-powered comparison including spec-by-spec breakdown and recommendation.
 */

import React, { useEffect, useState } from "react";
import type { ProductComparison } from "../../types";
import { ResearchAnimation } from "./ResearchAnimation";

interface ComparisonPanelProps {
  productId: string;
  targetId: string;
  onClose: () => void;
  comparison?: ProductComparison;
}

export const ComparisonPanel: React.FC<ComparisonPanelProps> = ({
  productId,
  targetId,
  onClose,
  comparison: externalComparison,
}) => {
  const [comparison, setComparison] = useState<ProductComparison | null>(
    externalComparison || null,
  );
  const [loading, setLoading] = useState(!externalComparison);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (externalComparison) {
      setComparison(externalComparison);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch("/api/jit/explore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_id: productId,
        action_type: "comparison",
        target_id: targetId,
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error(`Compare failed: ${res.statusText}`);
        return res.json();
      })
      .then((data) => {
        if (cancelled) return;
        // The explore endpoint returns comparison data in the response
        setComparison(data as ProductComparison);
        setLoading(false);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err.message);
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [productId, targetId, externalComparison]);

  if (loading) {
    return (
      <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
        <ResearchAnimation
          brandName="comparison"
          message="Comparing products…"
          progress={50}
        />
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="bg-slate-900/80 rounded-xl p-4 border border-red-500/20">
        <div className="flex items-center justify-between">
          <p className="text-xs text-red-400">
            {error || "Comparison unavailable"}
          </p>
          <button
            onClick={onClose}
            className="text-xs text-zinc-500 hover:text-white transition-colors px-2 py-1 rounded hover:bg-slate-800"
          >
            Close ✕
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
          Product Comparison
        </h2>
        <button
          onClick={onClose}
          className="text-xs text-zinc-500 hover:text-white transition-colors px-2 py-1 rounded hover:bg-slate-800"
        >
          Close ✕
        </button>
      </div>

      {/* Summary */}
      <p className="text-sm text-zinc-300 leading-relaxed">
        {comparison.summary}
      </p>

      {/* Product names header */}
      <div className="grid grid-cols-[1fr_1fr_1fr] gap-3 text-center">
        <div />
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg px-3 py-2">
          <p className="text-xs font-semibold text-blue-400 truncate">
            {comparison.product_a.name}
          </p>
          {comparison.product_a.price > 0 && (
            <p className="text-[10px] text-zinc-400">
              ₪{comparison.product_a.price.toLocaleString("he-IL")}
            </p>
          )}
        </div>
        <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg px-3 py-2">
          <p className="text-xs font-semibold text-purple-400 truncate">
            {comparison.product_b.name}
          </p>
          {comparison.product_b.price > 0 && (
            <p className="text-[10px] text-zinc-400">
              ₪{comparison.product_b.price.toLocaleString("he-IL")}
            </p>
          )}
        </div>
      </div>

      {/* Spec comparison table */}
      {comparison.spec_comparison && comparison.spec_comparison.length > 0 && (
        <div className="space-y-0.5">
          {comparison.spec_comparison.map((row, idx) => (
            <div
              key={idx}
              className={`grid grid-cols-[1fr_1fr_1fr] gap-3 py-2 px-2 rounded text-xs ${
                idx % 2 === 0 ? "bg-slate-800/20" : ""
              }`}
            >
              <span className="text-zinc-500 capitalize">{row.feature}</span>
              <span
                className={`text-center font-medium ${row.advantage === "a" ? "text-blue-400" : "text-zinc-300"}`}
              >
                {row.product_a_value}
                {row.advantage === "a" && " ★"}
              </span>
              <span
                className={`text-center font-medium ${row.advantage === "b" ? "text-purple-400" : "text-zinc-300"}`}
              >
                {row.product_b_value}
                {row.advantage === "b" && " ★"}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Use cases */}
      <div className="grid grid-cols-2 gap-3">
        {comparison.use_case_a && (
          <div className="bg-blue-500/5 border border-blue-500/15 rounded-lg p-3">
            <p className="text-[10px] text-blue-400 uppercase tracking-wider font-semibold mb-1">
              Best for
            </p>
            <p className="text-xs text-zinc-300">{comparison.use_case_a}</p>
          </div>
        )}
        {comparison.use_case_b && (
          <div className="bg-purple-500/5 border border-purple-500/15 rounded-lg p-3">
            <p className="text-[10px] text-purple-400 uppercase tracking-wider font-semibold mb-1">
              Best for
            </p>
            <p className="text-xs text-zinc-300">{comparison.use_case_b}</p>
          </div>
        )}
      </div>

      {/* Recommendation */}
      {comparison.recommendation && (
        <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-4">
          <p className="text-[10px] text-emerald-400 uppercase tracking-wider font-semibold mb-1">
            Recommendation
          </p>
          <p className="text-sm text-zinc-300">{comparison.recommendation}</p>
        </div>
      )}

      {/* Price value */}
      {comparison.price_value && (
        <p className="text-xs text-zinc-500 italic">{comparison.price_value}</p>
      )}
    </div>
  );
};
