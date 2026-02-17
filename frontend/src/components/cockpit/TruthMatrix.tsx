/**
 * Truth Matrix — Source transparency for price, specs, and relations.
 * Surfaces verification level so users know what to trust.
 */

import React from "react";
import { Shield, CheckCircle, AlertTriangle, FileText, Link2, ShoppingBag } from "lucide-react";

export type DataTrust = {
  price_source?: "halilit" | "official" | "estimated" | "none";
  specs_source?: "halilit" | "official" | "none";
  description_source?: "halilit" | "official" | "synthesized" | "none";
  image_source?: "halilit" | "official" | "none";
  review_source?: "contextual" | "none";
};

export type RelationshipMetaRecord = {
  sources_verified?: string[];
  confidence?: number;
  discovered_from?: string;
};

interface TruthMatrixProps {
  dataTrust: DataTrust | undefined;
  /** For relations: do we have any official/verified links? */
  relationsVerified: boolean;
  /** Do we have any store-recommended (commercial) links? */
  relationsCommercial: boolean;
  /** Any relations at all (inferred/soft)? */
  hasRelations: boolean;
  brandColor?: string;
  className?: string;
}

const verifiedSources = ["official", "official_text_match", "official_url_match"];

function isSpecsVerified(source: string | undefined): boolean {
  return source === "official";
}

function isPriceVerified(source: string | undefined): boolean {
  return source === "halilit" || source === "official";
}

export function TruthMatrix({
  dataTrust,
  relationsVerified,
  relationsCommercial,
  hasRelations,
  brandColor = "#3b82f6",
  className = "",
}: TruthMatrixProps) {
  const priceSource = dataTrust?.price_source ?? "none";
  const specsSource = dataTrust?.specs_source ?? "none";
  const priceVerified = isPriceVerified(priceSource);
  const specsVerified = isSpecsVerified(specsSource);

  const rows: {
    label: string;
    icon: React.ReactNode;
    status: "verified" | "inferred" | "none";
    detail: string;
    /** Optional tooltip explaining what this row means */
    title?: string;
  }[] = [
    {
      label: "Price",
      icon: <ShoppingBag size={12} className="shrink-0" />,
      status: priceVerified ? "verified" : priceSource === "estimated" ? "inferred" : "none",
      detail: priceVerified ? "Verified (Halilit)" : priceSource === "estimated" ? "Estimated" : "Not set",
    },
    {
      label: "Specs",
      icon: <FileText size={12} className="shrink-0" />,
      status: specsVerified ? "verified" : specsSource === "halilit" ? "inferred" : "none",
      detail: specsVerified ? "Verified (Official)" : specsSource === "halilit" ? "Halilit" : "Not set",
    },
    {
      label: "Relations",
      icon: <Link2 size={12} className="shrink-0" />,
      status: relationsVerified ? "verified" : relationsCommercial ? "inferred" : hasRelations ? "inferred" : "none",
      detail: relationsVerified
        ? "Verified (Manufacturer)"
        : relationsCommercial
          ? "Store recommended"
          : hasRelations
            ? "Likely compatible — double-check"
            : "None",
      title:
        "Accessories, compatible gear, and alternatives. Verified = from manufacturer; Store = Halilit/commercial; Likely = same category — confirm before buying.",
    },
  ];

  return (
    <div
      className={`rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-4 space-y-2 ${className}`}
      role="region"
      aria-label="Data source and verification"
    >
      <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-2 flex items-center gap-2">
        <Shield size={12} style={{ color: brandColor }} />
        Truth Matrix
      </h3>
      <ul className="space-y-2">
        {rows.map((row) => (
          <li
            key={row.label}
            className="flex items-center gap-2 text-[11px]"
            title={row.title}
          >
            <span className="text-zinc-500 w-14 shrink-0 flex items-center gap-1">
              {row.icon}
              {row.label}
            </span>
            {row.status === "verified" && (
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle size={10} aria-hidden />
                {row.detail}
              </span>
            )}
            {row.status === "inferred" && (
              <span className="flex items-center gap-1 text-amber-400/90 font-medium">
                <AlertTriangle size={10} aria-hidden />
                {row.detail}
              </span>
            )}
            {row.status === "none" && (
              <span className="text-zinc-500">{row.detail}</span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
