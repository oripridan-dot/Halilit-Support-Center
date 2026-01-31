import React from "react";
import type { GoldenProduct } from "../../types";

export const ProductCard = ({ product }: { product: GoldenProduct }) => {
  // sandbox mode: allow all tiers
  const isRefined = product.processed_badge?.level === "DIAMOND";
  const isCoal = product.processed_badge?.level === "COAL";

  return (
    <div
      className={`card tier-${product.processed_badge?.level?.toLowerCase() || "unknown"} p-4 border rounded-md mb-2 bg-zinc-900 border-zinc-800 relative`}
    >
      {!isRefined && (
        <div
          className={`warning-banner text-[10px] font-bold px-2 py-1 mb-2 inline-block rounded ${isCoal ? "bg-red-900 text-red-100" : "bg-amber-900 text-amber-100"}`}
        >
          {isCoal ? "LOW DATA QUALITY" : "PENDING VERIFICATION"}
        </div>
      )}

      {/* HEADER: Identity */}
      <h3 className="text-lg font-bold text-white mb-1">
        {product.identity?.name ?? product.name ?? "Unknown Product"}
      </h3>

      {/* BADGE: Trust Level */}
      {isRefined && (
        <span className="badge-diamond inline-flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-500/50 mb-2">
          💎 Verified & Tested
        </span>
      )}

      {/* CONTEXT: Real World Data */}
      <div className="context-overlay text-sm text-zinc-400">
        <ul className="space-y-1">
          {product.context?.verified_pros?.map((pro) => (
            <li key={pro} className="flex items-start gap-2">
              <span className="text-emerald-500">✅</span>
              <span>{pro}</span>
            </li>
          ))}
        </ul>
        {(product.context?.trusted_sources?.length ?? 0) > 0 && (
          <div className="sources mt-2 pt-2 border-t border-zinc-800 text-xs text-zinc-500">
            Verified by:{" "}
            {product.context?.trusted_sources?.map((s) => s.name).join(", ")}
          </div>
        )}
      </div>

      {/* Fallback Image Logic */}
      {(!product.identity?.official_images ||
        product.identity.official_images.length === 0) && (
        <div className="text-xs text-zinc-600 italic mt-2">
          No Image Available
        </div>
      )}
    </div>
  );
};
