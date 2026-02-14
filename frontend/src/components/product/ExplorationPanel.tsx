/**
 * ExplorationPanel — Premium exploration results renderer
 *
 * Renders setup guides, deep dives, artist spotlights, etc.
 * with a visual-first design optimized for readability and engagement.
 *
 * Setup Guide features:
 *   - Mini table-of-contents with progress tracking
 *   - Checkable steps that persist per session
 *   - Vertical timeline with numbered nodes
 *   - Amber pro-tip callouts
 *   - Section-aware icons
 *   - Circular progress rings per section
 */

import React, { useState, useRef, useCallback, useMemo, useEffect } from "react";
import type { ExplorationResult } from "../../hooks/useExploration";

/* ═══════════════════════════════════════════════════════
   TYPES
   ═══════════════════════════════════════════════════════ */

interface ExplorationPanelProps {
  result: ExplorationResult;
  onClose: () => void;
  brandColor?: string;
}

interface GuideSection {
  title: string;
  steps: GuideStep[];
  [key: string]: unknown;
}

interface GuideStep {
  step: number;
  title: string;
  instruction: string;
  tip?: string;
  [key: string]: unknown;
}

/* ═══════════════════════════════════════════════════════
   CONSTANTS
   ═══════════════════════════════════════════════════════ */

const TYPE_LABELS: Record<string, string> = {
  setup: "Setup Guide",
  artists: "Artist Spotlight",
  issues: "Field Notes & Known Issues",
  accessories: "Essential Accessories",
  deep_dive: "Deep Dive",
  compare: "Comparison",
};

const TYPE_ICONS: Record<string, string> = {
  setup: "\ud83d\udee0\ufe0f",
  artists: "\ud83c\udfa7",
  issues: "\u26a0\ufe0f",
  accessories: "\ud83c\udf92",
  deep_dive: "\ud83c\udf93",
  compare: "\u2694\ufe0f",
};

const META_KEYS = new Set([
  "product_id", "action_type", "topic", "format",
  "product", "guideType", "guide_type",
]);

const SECTION_ICONS: Record<string, string> = {
  unboxing: "\ud83d\udce6", box: "\ud83d\udce6", whats_in: "\ud83d\udce6", "what's": "\ud83d\udce6",
  setup: "\u2699\ufe0f", physical: "\ud83d\udccf", placement: "\ud83d\udccf", position: "\ud83d\udccf",
  connection: "\ud83d\udd0c", cable: "\ud83d\udd0c", signal: "\ud83d\udd0c", connect: "\ud83d\udd0c",
  power: "\u26a1", calibrat: "\ud83c\udf9a\ufe0f", setting: "\ud83c\udf9b\ufe0f",
  audio: "\ud83d\udd0a", sound: "\ud83c\udfb5", recording: "\ud83c\udf99\ufe0f",
  perform: "\ud83c\udfb9", scenario: "\ud83c\udfaf", live: "\ud83c\udfa4", common: "\ud83c\udfaf",
  home: "\ud83c\udfe0", studio: "\ud83c\udfa7", troubleshoot: "\ud83d\udd27",
  maintain: "\ud83e\uddf9", essential: "\u2705", recommend: "\ud83d\udc4d",
  overview: "\ud83d\udccb", checklist: "\u2705", getting_started: "\ud83d\ude80",
  first: "\ud83d\ude80", tip: "\ud83d\udca1", accessories: "\ud83c\udf92",
  advanced: "\ud83c\udfaf", basics: "\ud83d\udcd6",
};

function getSectionIcon(name: string): string {
  const n = name.toLowerCase().replace(/[\s-]/g, "_");
  for (const [pat, ico] of Object.entries(SECTION_ICONS)) {
    if (n.includes(pat)) return ico;
  }
  return "\u25b8";
}

/* ═══════════════════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════════════════ */

export const ExplorationPanel: React.FC<ExplorationPanelProps> = ({
  result, onClose, brandColor = "#3b82f6",
}) => {
  const topic = result.topic || result.action_type;
  const label = TYPE_LABELS[topic] || "Exploration";
  const icon = TYPE_ICONS[topic] || "\ud83d\udd0d";

  // Detect if this is a structured setup guide
  const isSetupGuide = useMemo(() => {
    const data = (result.content ?? result) as Record<string, unknown>;
    return topic === "setup" && Array.isArray(data.sections);
  }, [result, topic]);

  const guideData = useMemo(() => {
    if (!isSetupGuide) return null;
    const data = (result.content ?? result) as Record<string, unknown>;
    return {
      title: (data.title as string) || label,
      overview: (data.overview as string) || "",
      sections: (data.sections as GuideSection[]) || [],
    };
  }, [result, isSetupGuide, label]);

  return (
    <div className="bg-slate-950/95 rounded-2xl border border-slate-700/40 overflow-hidden shadow-2xl shadow-black/40 backdrop-blur-sm">
      {/* HEADER */}
      <div className="relative px-6 py-4 border-b border-slate-800/60 overflow-hidden">
        <div className="absolute inset-0 opacity-[0.07]"
          style={{ background: `linear-gradient(135deg, ${brandColor}, transparent 60%)` }} />
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl"
              style={{ backgroundColor: `${brandColor}15`, border: `1px solid ${brandColor}30` }}>
              {icon}
            </div>
            <div>
              <h3 className="text-sm font-bold text-white tracking-wide">
                {guideData?.title || label}
              </h3>
              <p className="text-[10px] text-zinc-500 mt-0.5">AI-generated guide</p>
            </div>
          </div>
          <button onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg text-zinc-500 hover:text-white hover:bg-slate-800/80 transition-all">
            {"\u2715"}
          </button>
        </div>
      </div>

      {/* BODY */}
      <div className="max-h-[70vh] overflow-y-auto custom-scrollbar">
        {isSetupGuide && guideData ? (
          <SetupGuideView guide={guideData} brandColor={brandColor} />
        ) : result.format === "text" && typeof result.content === "string" ? (
          <div className="p-6">
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">
              {result.content}
            </p>
          </div>
        ) : (
          <div className="p-6">
            <GenericView data={unwrapResult(result)} brandColor={brandColor} />
          </div>
        )}
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════
   SETUP GUIDE VIEW — Premium guided layout
   ═══════════════════════════════════════════════════════ */

interface SetupGuideViewProps {
  guide: { title: string; overview: string; sections: GuideSection[] };
  brandColor: string;
}

const SetupGuideView: React.FC<SetupGuideViewProps> = ({ guide, brandColor }) => {
  const totalSteps = useMemo(
    () => guide.sections.reduce((sum, s) => sum + (s.steps?.length || 0), 0),
    [guide.sections],
  );
  const [checkedSteps, setCheckedSteps] = useState<Set<string>>(() => new Set());
  const [activeSectionIdx, setActiveSectionIdx] = useState(0);
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);

  const completedCount = checkedSteps.size;
  const progressPct = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;

  const toggleStep = useCallback((sectionIdx: number, stepIdx: number) => {
    const key = `${sectionIdx}-${stepIdx}`;
    setCheckedSteps(prev => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });
  }, []);

  const scrollToSection = useCallback((idx: number) => {
    sectionRefs.current[idx]?.scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveSectionIdx(idx);
  }, []);

  // Track scroll position to update active section in TOC
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const handleScroll = () => {
      const scrollTop = container.scrollTop;
      let active = 0;
      for (let i = 0; i < sectionRefs.current.length; i++) {
        const el = sectionRefs.current[i];
        if (el && el.offsetTop - container.offsetTop <= scrollTop + 80) {
          active = i;
        }
      }
      setActiveSectionIdx(active);
    };
    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="flex">
      {/* LEFT: Mini Table of Contents */}
      <div className="w-52 shrink-0 border-r border-slate-800/40 bg-slate-900/30 sticky top-0 self-start">
        <div className="p-4 space-y-3">
          {/* Progress indicator */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                Progress
              </span>
              <span className="text-[10px] font-bold tabular-nums" style={{ color: brandColor }}>
                {completedCount}/{totalSteps}
              </span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 ease-out"
                style={{
                  width: `${progressPct}%`,
                  background: `linear-gradient(90deg, ${brandColor}, ${brandColor}aa)`,
                }}
              />
            </div>
            {progressPct === 100 && (
              <p className="text-[9px] text-emerald-400 font-bold mt-1.5 flex items-center gap-1">
                <span>{"\u2713"}</span> All steps complete!
              </p>
            )}
          </div>

          {/* Section links */}
          <nav className="space-y-0.5">
            {guide.sections.map((section, idx) => {
              const sectionStepCount = section.steps?.length || 0;
              const sectionCompleted = section.steps?.filter((_, si) =>
                checkedSteps.has(`${idx}-${si}`)).length || 0;
              const isActive = idx === activeSectionIdx;
              const isDone = sectionCompleted === sectionStepCount && sectionStepCount > 0;

              return (
                <button
                  key={idx}
                  onClick={() => scrollToSection(idx)}
                  className={`w-full text-left px-2.5 py-2 rounded-lg text-[11px] transition-all flex items-center gap-2 group
                    ${isActive
                      ? "bg-slate-800/80 text-white"
                      : "text-zinc-500 hover:text-zinc-300 hover:bg-slate-800/30"
                    }`}
                >
                  <span className="text-xs shrink-0">{getSectionIcon(section.title)}</span>
                  <span className="flex-1 leading-snug font-medium truncate">
                    {section.title}
                  </span>
                  {isDone ? (
                    <span className="text-emerald-400 text-[9px] shrink-0">{"\u2713"}</span>
                  ) : sectionStepCount > 0 ? (
                    <span className="text-[9px] text-zinc-600 tabular-nums shrink-0">
                      {sectionCompleted}/{sectionStepCount}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* RIGHT: Guide content */}
      <div ref={containerRef} className="flex-1 overflow-y-auto max-h-[70vh] scroll-smooth">
        {/* Overview banner */}
        {guide.overview && (
          <div className="px-6 py-4 border-b border-slate-800/30 bg-slate-900/20">
            <p className="text-sm text-zinc-400 leading-relaxed">{guide.overview}</p>
          </div>
        )}

        {/* Sections */}
        <div className="px-6 py-5 space-y-8">
          {guide.sections.map((section, sIdx) => (
            <div
              key={sIdx}
              ref={el => { sectionRefs.current[sIdx] = el; }}
            >
              {/* Section header */}
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                  style={{ backgroundColor: `${brandColor}12`, border: `1px solid ${brandColor}25` }}
                >
                  {getSectionIcon(section.title)}
                </div>
                <div className="flex-1">
                  <h4 className="text-[13px] font-bold text-white tracking-wide">
                    {section.title}
                  </h4>
                  <span className="text-[9px] text-zinc-600">
                    {section.steps?.length || 0} steps
                  </span>
                </div>
                <SectionProgress
                  completed={section.steps?.filter((_, si) => checkedSteps.has(`${sIdx}-${si}`)).length || 0}
                  total={section.steps?.length || 0}
                  brandColor={brandColor}
                />
              </div>

              {/* Steps */}
              {section.steps && section.steps.length > 0 && (
                <div className="relative ml-1">
                  {/* Vertical connector line */}
                  <div
                    className="absolute left-[14px] top-6 bottom-3 w-px"
                    style={{ background: `linear-gradient(to bottom, ${brandColor}25, ${brandColor}06)` }}
                  />

                  <div className="space-y-1">
                    {section.steps.map((step, stIdx) => {
                      const stepKey = `${sIdx}-${stIdx}`;
                      const isChecked = checkedSteps.has(stepKey);

                      return (
                        <StepCard
                          key={stIdx}
                          step={step}
                          stepNumber={step.step ?? stIdx + 1}
                          isChecked={isChecked}
                          onToggle={() => toggleStep(sIdx, stIdx)}
                          brandColor={brandColor}
                        />
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════
   STEP CARD
   ═══════════════════════════════════════════════════════ */

interface StepCardProps {
  step: GuideStep;
  stepNumber: number;
  isChecked: boolean;
  onToggle: () => void;
  brandColor: string;
}

const StepCard: React.FC<StepCardProps> = ({ step, stepNumber, isChecked, onToggle, brandColor }) => {
  const extraKeys = Object.keys(step).filter(
    k => !["step", "title", "instruction", "tip", "step_number", "stepNumber"].includes(k)
  );

  return (
    <div className={`relative flex gap-3 py-3 group transition-opacity duration-300 ${isChecked ? "opacity-60" : ""}`}>
      {/* Step node (clickable checkbox) */}
      <button
        onClick={onToggle}
        className="relative z-10 w-7 h-7 rounded-lg flex items-center justify-center text-[10px] font-bold shrink-0 transition-all duration-200 hover:scale-110"
        style={{
          backgroundColor: isChecked ? `${brandColor}25` : `${brandColor}10`,
          color: isChecked ? "#34d399" : brandColor,
          border: `1.5px solid ${isChecked ? "#34d39950" : `${brandColor}30`}`,
        }}
        title={isChecked ? "Mark as incomplete" : "Mark as done"}
      >
        {isChecked ? "\u2713" : stepNumber}
      </button>

      {/* Content */}
      <div className="flex-1 min-w-0 pt-0.5">
        <h5 className={`text-[12px] font-semibold leading-snug transition-all ${isChecked ? "text-zinc-500 line-through" : "text-zinc-100"}`}>
          {step.title}
        </h5>
        <p className={`text-[11px] leading-relaxed mt-1 transition-colors ${isChecked ? "text-zinc-600" : "text-zinc-400"}`}>
          {step.instruction}
        </p>

        {/* Pro Tip */}
        {step.tip && !isChecked && (
          <div className="mt-2.5 flex items-start gap-2 bg-amber-500/[0.05] border border-amber-500/10 rounded-lg px-3 py-2">
            <span className="text-amber-400 text-[11px] mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
            <div>
              <span className="text-[8px] font-bold text-amber-500/60 uppercase tracking-widest">Pro Tip</span>
              <p className="text-[10px] text-amber-200/70 leading-relaxed mt-0.5">{step.tip}</p>
            </div>
          </div>
        )}

        {/* Extra fields */}
        {extraKeys.map(k => (
          <div key={k} className="mt-1.5">
            <span className="text-[9px] font-semibold text-zinc-600 uppercase tracking-wider">{formatLabel(k)}</span>
            <p className="text-[11px] text-zinc-400 leading-relaxed mt-0.5">
              {typeof step[k] === "string" ? (step[k] as string) : JSON.stringify(step[k])}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════
   SECTION PROGRESS RING
   ═══════════════════════════════════════════════════════ */

const SectionProgress: React.FC<{
  completed: number; total: number; brandColor: string;
}> = ({ completed, total, brandColor }) => {
  if (total === 0) return null;
  const pct = Math.round((completed / total) * 100);
  const r = 12;
  const c = 2 * Math.PI * r;
  const offset = c - (pct / 100) * c;

  return (
    <div className="relative w-8 h-8 flex items-center justify-center">
      <svg width={30} height={30} className="rotate-[-90deg]">
        <circle cx={15} cy={15} r={r} fill="none" stroke="rgb(51 65 85 / 0.3)" strokeWidth={2.5} />
        <circle
          cx={15} cy={15} r={r} fill="none"
          stroke={completed === total ? "#34d399" : brandColor}
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-[8px] font-bold tabular-nums" style={{ color: completed === total ? "#34d399" : brandColor }}>
        {pct}%
      </span>
    </div>
  );
};

/* ═══════════════════════════════════════════════════════
   GENERIC VIEW — For non-setup-guide explorations
   ═══════════════════════════════════════════════════════ */

const GenericView: React.FC<{
  data: unknown; brandColor: string;
}> = ({ data, brandColor }) => (
  <RenderValue value={data} brandColor={brandColor} depth={0} />
);

/* ═══════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════ */

function unwrapResult(result: ExplorationResult): unknown {
  if (result.content && Array.isArray(result.content) && result.content.length === 1 && typeof result.content[0] === "object")
    return result.content[0];
  if (result.content !== undefined) return result.content;
  const clean: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(result)) if (!META_KEYS.has(k)) clean[k] = v;
  return clean;
}

function formatLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/([a-z])([A-Z])/g, "$1 $2").replace(/\b\w/g, c => c.toUpperCase());
}

function isPrimitive(v: unknown): v is string | number | boolean {
  return typeof v === "string" || typeof v === "number" || typeof v === "boolean";
}

const TITLE_KEYS = new Set([
  "title", "scenarioName", "scenario_name", "name", "label",
  "instruction", "heading", "section_title", "sectionTitle",
]);

const TIP_KEYS = new Set([
  "tip", "tips", "pro_tip", "proTip", "pro_tips",
  "note", "notes", "warning", "caution", "important",
]);

function isTipKey(k: string): boolean {
  return TIP_KEYS.has(k.toLowerCase().replace(/[\s-]/g, "_"));
}

function getTitleFromObj(obj: Record<string, unknown>): [string | null, string | null] {
  const key = Object.keys(obj).find(k => TITLE_KEYS.has(k));
  return key ? [key, String(obj[key])] : [null, null];
}

/* ═══════════════════════════════════════════════════════
   RECURSIVE VALUE RENDERER (for generic explorations)
   ═══════════════════════════════════════════════════════ */

const RenderValue: React.FC<{
  value: unknown; brandColor: string; depth: number; label?: string;
}> = ({ value, brandColor, depth, label }) => {
  if (value === null || value === undefined) return null;

  // String
  if (typeof value === "string") {
    if (label && isTipKey(label)) {
      return (
        <div className="flex items-start gap-2.5 bg-amber-500/[0.06] border border-amber-500/15 rounded-xl px-4 py-3 mt-1.5">
          <span className="text-amber-400 text-sm mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
          <div>
            <span className="text-[9px] font-bold text-amber-400/70 uppercase tracking-widest">Pro Tip</span>
            <p className="text-xs text-amber-200/80 leading-relaxed mt-0.5">{value}</p>
          </div>
        </div>
      );
    }
    return label ? (
      <div className="mb-2">
        <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider">{formatLabel(label)}</span>
        <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line mt-0.5">{value}</p>
      </div>
    ) : (
      <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{value}</p>
    );
  }

  // Number / boolean
  if (typeof value === "number" || typeof value === "boolean")
    return <span className="text-sm text-zinc-300 font-medium">{String(value)}</span>;

  // Array
  if (Array.isArray(value)) {
    if (value.length === 0) return null;
    if (value.every(v => typeof v === "string")) {
      return (
        <ul className="space-y-1.5 ml-0.5">
          {(value as string[]).map((item, idx) => (
            <li key={idx} className="flex items-start gap-2.5 text-sm text-zinc-300">
              <span className="mt-1.5 w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: brandColor }} />
              <span className="leading-relaxed">{item}</span>
            </li>
          ))}
        </ul>
      );
    }

    return (
      <div className="space-y-3">
        {value.map((item, idx) => {
          if (typeof item === "string") {
            return (
              <div key={idx} className="flex items-start gap-2.5 text-sm text-zinc-300">
                <span className="mt-1.5 w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: brandColor }} />
                <span>{item}</span>
              </div>
            );
          }
          if (typeof item !== "object" || item === null) {
            return <span key={idx} className="text-xs text-zinc-400">{String(item)}</span>;
          }
          return <RenderCard key={idx} obj={item as Record<string, unknown>} brandColor={brandColor} depth={depth + 1} index={idx} total={value.length} />;
        })}
      </div>
    );
  }

  // Object
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    return <RenderCard obj={obj} brandColor={brandColor} depth={depth} />;
  }

  return <span className="text-xs text-zinc-400">{String(value)}</span>;
};

/** Card renderer for object values */
const RenderCard: React.FC<{
  obj: Record<string, unknown>; brandColor: string; depth: number; index?: number; total?: number;
}> = ({ obj, brandColor, depth, index, total }) => {
  const [titleKey, title] = getTitleFromObj(obj);
  const sectionIcon = title ? getSectionIcon(title) : "\u25b8";
  const contentKeys = Object.keys(obj).filter(k => k !== titleKey && !META_KEYS.has(k));

  return (
    <div className="rounded-xl border overflow-hidden"
      style={{
        borderColor: depth < 1 ? `${brandColor}20` : "rgb(51 65 85 / 0.3)",
        backgroundColor: depth < 1 ? `${brandColor}03` : "rgb(30 41 59 / 0.25)",
      }}>
      {title && (
        <div className="px-4 py-2.5 border-b flex items-center gap-2.5"
          style={{ borderColor: `${brandColor}10`, background: `linear-gradient(90deg, ${brandColor}06, transparent)` }}>
          <span className="text-sm">{sectionIcon}</span>
          <h4 className="text-xs font-bold text-zinc-200 tracking-wide uppercase flex-1">{title}</h4>
          {typeof index === "number" && typeof total === "number" && (
            <span className="text-[9px] text-zinc-600">{index + 1}/{total}</span>
          )}
        </div>
      )}
      <div className="px-4 py-3 space-y-2">
        {contentKeys.map(k => {
          const val = obj[k];
          if (isTipKey(k) && typeof val === "string") {
            return (
              <div key={k} className="flex items-start gap-2.5 bg-amber-500/[0.06] border border-amber-500/15 rounded-xl px-4 py-3">
                <span className="text-amber-400 text-sm mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
                <div>
                  <span className="text-[9px] font-bold text-amber-400/70 uppercase tracking-widest">Pro Tip</span>
                  <p className="text-xs text-amber-200/80 leading-relaxed mt-0.5">{val}</p>
                </div>
              </div>
            );
          }
          return <RenderValue key={k} value={val} brandColor={brandColor} depth={depth + 1} label={isPrimitive(val) ? k : undefined} />;
        })}
      </div>
    </div>
  );
};
