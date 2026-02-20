/**
 * ExplorationPanelGuideView.tsx
 * Setup guide sub-components: SetupGuideView, StepCard, SectionProgress.
 * Extracted from ExplorationPanel.tsx to stay under the 700-line ceiling.
 */

import React, {
  useState,
  useRef,
  useCallback,
  useMemo,
  useEffect,
} from "react";
import { formatLabel, getSectionIcon } from "./explorationUtils";

// ---------------------------------------------------------------------------
// Types (exported so ExplorationPanel can reference them)
// ---------------------------------------------------------------------------

export interface GuideStep {
  step?: number;
  title: string;
  instruction: string;
  tip?: string;
  [key: string]: unknown;
}

export interface GuideSection {
  title: string;
  steps?: GuideStep[];
}

export interface GuideData {
  title: string;
  overview: string;
  sections: GuideSection[];
}

interface SetupGuideViewProps {
  guide: GuideData;
  brandColor: string;
}

interface StepCardProps {
  step: GuideStep;
  stepNumber: number;
  isChecked: boolean;
  onToggle: () => void;
  brandColor: string;
}

interface SectionProgressProps {
  completed: number;
  total: number;
  brandColor: string;
}

// ---------------------------------------------------------------------------
// SectionProgress
// ---------------------------------------------------------------------------

const SectionProgress: React.FC<SectionProgressProps> = ({
  completed,
  total,
  brandColor,
}): JSX.Element | null => {
  if (total === 0) return null;
  const percentage = Math.round((completed / total) * 100);
  const radius = 12;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;
  return (
    <div className="relative w-8 h-8 flex items-center justify-center">
      <svg width={30} height={30} className="rotate-[-90deg]">
        <circle cx={15} cy={15} r={radius} fill="none" stroke="rgb(51 65 85 / 0.3)" strokeWidth={2.5} />
        <circle
          cx={15} cy={15} r={radius} fill="none"
          stroke={completed === total ? "#34d399" : brandColor}
          strokeWidth={2.5} strokeLinecap="round"
          strokeDasharray={circumference} strokeDashoffset={offset}
          className="transition-all duration-500"
        />
      </svg>
      <span className="absolute text-[8px] font-bold tabular-nums" style={{ color: completed === total ? "#34d399" : brandColor }}>
        {percentage}%
      </span>
    </div>
  );
};

// ---------------------------------------------------------------------------
// StepCard
// ---------------------------------------------------------------------------

const StepCard: React.FC<StepCardProps> = ({
  step,
  stepNumber,
  isChecked,
  onToggle,
  brandColor,
}): JSX.Element => {
  const extraKeys = Object.keys(step).filter(
    (k) => !["step", "title", "instruction", "tip", "step_number", "stepNumber"].includes(k),
  );
  return (
    <div className={`relative flex gap-3 py-3 group transition-opacity duration-300 ${isChecked ? "opacity-60" : ""}`}>
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
      <div className="flex-1 min-w-0 pt-0.5">
        <h5 className={`text-[12px] font-semibold leading-snug transition-all ${isChecked ? "text-zinc-500 line-through" : "text-zinc-100"}`}>
          {step.title}
        </h5>
        <p className={`text-[11px] leading-relaxed mt-1 transition-colors ${isChecked ? "text-zinc-600" : "text-zinc-400"}`}>
          {step.instruction}
        </p>
        {step.tip && !isChecked && (
          <div className="mt-2.5 flex items-start gap-2 bg-amber-500/[0.05] border border-amber-500/10 rounded-lg px-3 py-2">
            <span className="text-amber-400 text-[11px] mt-0.5 shrink-0">{"\ud83d\udca1"}</span>
            <div>
              <span className="text-[8px] font-bold text-amber-500/60 uppercase tracking-widest">Pro Tip</span>
              <p className="text-[10px] text-amber-200/70 leading-relaxed mt-0.5">{step.tip}</p>
            </div>
          </div>
        )}
        {extraKeys.map((key) => (
          <div key={key} className="mt-1.5">
            <span className="text-[9px] font-semibold text-zinc-600 uppercase tracking-wider">{formatLabel(key)}</span>
            <p className="text-[11px] text-zinc-400 leading-relaxed mt-0.5">
              {typeof step[key] === "string" ? (step[key] as string) : JSON.stringify(step[key])}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// SetupGuideView
// ---------------------------------------------------------------------------

export const SetupGuideView: React.FC<SetupGuideViewProps> = ({
  guide,
  brandColor,
}): JSX.Element => {
  const totalSteps = useMemo(
    () => guide.sections.reduce((sum, s) => sum + (s.steps?.length || 0), 0),
    [guide.sections],
  );
  const [checkedSteps, setCheckedSteps] = useState<Set<string>>(() => new Set());
  const [activeSectionIdx, setActiveSectionIdx] = useState(0);
  const sectionRefs = useRef<(HTMLDivElement | null)[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  const completedCount = checkedSteps.size;
  const progressPct = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;

  const toggleStep = useCallback((sectionIndex: number, stepIndex: number): void => {
    const stepKey = `${sectionIndex}-${stepIndex}`;
    setCheckedSteps((prev) => {
      const next = new Set(prev);
      next.has(stepKey) ? next.delete(stepKey) : next.add(stepKey);
      return next;
    });
  }, []);

  const scrollToSection = useCallback((sectionIndex: number): void => {
    sectionRefs.current[sectionIndex]?.scrollIntoView({ behavior: "smooth", block: "start" });
    setActiveSectionIdx(sectionIndex);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const handleScroll = (): void => {
      const scrollTop = container.scrollTop;
      let active = 0;
      for (let i = 0; i < sectionRefs.current.length; i++) {
        const el = sectionRefs.current[i];
        if (el && el.offsetTop - container.offsetTop <= scrollTop + 80) active = i;
      }
      setActiveSectionIdx(active);
    };
    container.addEventListener("scroll", handleScroll, { passive: true });
    return () => container.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="flex">
      {/* TOC sidebar */}
      <div className="w-52 shrink-0 border-r border-slate-800/40 bg-slate-900/30 sticky top-0 self-start">
        <div className="p-4 space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">Progress</span>
              <span className="text-[10px] font-bold tabular-nums" style={{ color: brandColor }}>
                {completedCount}/{totalSteps}
              </span>
            </div>
            <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progressPct}%`, background: `linear-gradient(90deg, ${brandColor}, ${brandColor}aa)` }}
              />
            </div>
            {progressPct === 100 && (
              <p className="text-[9px] text-emerald-400 font-bold mt-1.5 flex items-center gap-1">
                <span>{"\u2713"}</span> All steps complete!
              </p>
            )}
          </div>
          <nav className="space-y-0.5">
            {guide.sections.map((section, sectionIndex) => {
              const sectionStepCount = section.steps?.length || 0;
              const sectionCompleted = section.steps?.filter((_, si) => checkedSteps.has(`${sectionIndex}-${si}`)).length || 0;
              const isActive = sectionIndex === activeSectionIdx;
              const isDone = sectionCompleted === sectionStepCount && sectionStepCount > 0;
              return (
                <button
                  key={sectionIndex}
                  onClick={() => scrollToSection(sectionIndex)}
                  className={`w-full text-left px-2.5 py-2 rounded-lg text-[11px] transition-all flex items-center gap-2 group ${isActive ? "bg-slate-800/80 text-white" : "text-zinc-500 hover:text-zinc-300 hover:bg-slate-800/30"}`}
                >
                  <span className="text-xs shrink-0">{getSectionIcon(section.title)}</span>
                  <span className="flex-1 leading-snug font-medium truncate">{section.title}</span>
                  {isDone ? (
                    <span className="text-emerald-400 text-[9px] shrink-0">{"\u2713"}</span>
                  ) : sectionStepCount > 0 ? (
                    <span className="text-[9px] text-zinc-600 tabular-nums shrink-0">{sectionCompleted}/{sectionStepCount}</span>
                  ) : null}
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Guide content */}
      <div ref={containerRef} className="flex-1 overflow-y-auto max-h-[70vh] scroll-smooth">
        {guide.overview && (
          <div className="px-6 py-4 border-b border-slate-800/30 bg-slate-900/20">
            <p className="text-sm text-zinc-400 leading-relaxed">{guide.overview}</p>
          </div>
        )}
        <div className="px-6 py-5 space-y-8">
          {guide.sections.map((section, sectionIndex) => (
            <div key={sectionIndex} ref={(el) => { sectionRefs.current[sectionIndex] = el; }}>
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-base"
                  style={{ backgroundColor: `${brandColor}12`, border: `1px solid ${brandColor}25` }}
                >
                  {getSectionIcon(section.title)}
                </div>
                <div className="flex-1">
                  <h4 className="text-[13px] font-bold text-white tracking-wide">{section.title}</h4>
                  <span className="text-[9px] text-zinc-600">{section.steps?.length || 0} steps</span>
                </div>
                <SectionProgress
                  completed={section.steps?.filter((_, si) => checkedSteps.has(`${sectionIndex}-${si}`)).length || 0}
                  total={section.steps?.length || 0}
                  brandColor={brandColor}
                />
              </div>
              {section.steps && section.steps.length > 0 && (
                <div className="relative ml-1">
                  <div
                    className="absolute left-[14px] top-6 bottom-3 w-px"
                    style={{ background: `linear-gradient(to bottom, ${brandColor}25, ${brandColor}06)` }}
                  />
                  <div className="space-y-1">
                    {section.steps.map((step, stepIndex) => (
                      <StepCard
                        key={stepIndex}
                        step={step}
                        stepNumber={step.step ?? stepIndex + 1}
                        isChecked={checkedSteps.has(`${sectionIndex}-${stepIndex}`)}
                        onToggle={() => toggleStep(sectionIndex, stepIndex)}
                        brandColor={brandColor}
                      />
                    ))}
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
