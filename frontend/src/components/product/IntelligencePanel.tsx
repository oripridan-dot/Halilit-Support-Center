/**
 * IntelligencePanel — JIT-enriched product intelligence
 *
 * Shows the enriched description, best-for / avoid-if insights,
 * famous users, and known issues — all from the JIT agent.
 */

import React from "react";
import type { FamousUser, KnownIssue } from "../../types";

interface IntelligencePanelProps {
  enrichedDescription: string;
  bestFor: string[];
  avoidIf: string[];
  famousUsers: FamousUser[];
  knownIssues: KnownIssue[];
  brandAccentClass?: string;
}

export const IntelligencePanel: React.FC<IntelligencePanelProps> = ({
  enrichedDescription,
  bestFor,
  avoidIf,
  famousUsers,
  knownIssues,
  brandAccentClass = "text-blue-400",
}) => {
  return (
    <div className="space-y-4">
      {/* Enriched Description */}
      {enrichedDescription && (
        <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
          <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
            AI-Enhanced Overview
          </h2>
          <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">
            {enrichedDescription}
          </p>
        </div>
      )}

      {/* Best For / Avoid If */}
      {(bestFor.length > 0 || avoidIf.length > 0) && (
        <div className="grid grid-cols-2 gap-3">
          {bestFor.length > 0 && (
            <div className="bg-emerald-950/20 border border-emerald-500/20 rounded-xl p-4">
              <h3 className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-3">
                Best For
              </h3>
              <ul className="space-y-2 text-sm text-zinc-300">
                {bestFor.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-400 mt-0.5 shrink-0">✓</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          {avoidIf.length > 0 && (
            <div className="bg-orange-950/20 border border-orange-500/20 rounded-xl p-4">
              <h3 className="text-[11px] font-bold text-orange-400 uppercase tracking-wider mb-3">
                Avoid If
              </h3>
              <ul className="space-y-2 text-sm text-zinc-300">
                {avoidIf.map((item, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-orange-400 mt-0.5 shrink-0">✗</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Famous Users / Artist Spotlight */}
      {famousUsers.length > 0 && (
        <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
          <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
            Artist Spotlight
          </h2>
          <div className="flex flex-wrap gap-2">
            {famousUsers.map((user, idx) => (
              <div
                key={idx}
                className="bg-purple-500/10 border border-purple-500/20 rounded-lg px-3 py-2"
              >
                <span className={`text-xs font-semibold ${brandAccentClass}`}>
                  {user.name}
                </span>
                {user.context && (
                  <p className="text-[10px] text-zinc-500 mt-0.5">
                    {user.context}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Known Issues */}
      {knownIssues.length > 0 && (
        <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
          <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            Known Issues
          </h2>
          <div className="space-y-2">
            {knownIssues.map((issue, idx) => (
              <div
                key={idx}
                className={`rounded-lg px-3 py-2 border ${
                  issue.severity === "high"
                    ? "bg-red-500/10 border-red-500/20"
                    : issue.severity === "medium"
                      ? "bg-amber-500/10 border-amber-500/20"
                      : "bg-zinc-500/10 border-zinc-500/20"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[10px] font-bold uppercase ${
                      issue.severity === "high"
                        ? "text-red-400"
                        : issue.severity === "medium"
                          ? "text-amber-400"
                          : "text-zinc-400"
                    }`}
                  >
                    {issue.severity}
                  </span>
                  <span className="text-xs text-zinc-300">{issue.issue}</span>
                </div>
                {issue.source && (
                  <p className="text-[10px] text-zinc-600 mt-0.5">
                    Source: {issue.source}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
