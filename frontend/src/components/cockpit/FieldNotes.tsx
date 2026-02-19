import { motion } from "framer-motion";
import { AlertTriangle, Lightbulb, Wrench } from "lucide-react";

export interface FieldNotesData {
  tips?: string[];
  warnings?: string[];
  maintenance?: string[];
}

interface FieldNotesProps {
  notes: FieldNotesData | null;
  brandColor?: string;
  isLoading?: boolean;
}

/**
 * FieldNotes — Pro tips, real-world warnings, and maintenance advice.
 */
export const FieldNotes = ({
  notes,
  brandColor = "#3b82f6",
  isLoading = false,
}: FieldNotesProps) => {
  if (isLoading) {
    return (
      <div className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 animate-pulse">
        <div className="h-3 w-24 bg-zinc-800 rounded mb-3" />
        <div className="flex gap-2">
          <div className="h-6 w-full bg-zinc-800/40 rounded-lg" />
          <div className="h-6 w-full bg-zinc-800/40 rounded-lg" />
        </div>
      </div>
    );
  }

  if (!notes) return null;

  const hasTips = notes.tips && notes.tips.length > 0;
  const hasWarnings = notes.warnings && notes.warnings.length > 0;
  const hasMaintenance = notes.maintenance && notes.maintenance.length > 0;

  if (!hasTips && !hasWarnings && !hasMaintenance) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2, ease: "easeOut" }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5 space-y-4"
    >
      <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
        Field Notes
      </span>

      {/* Warnings first */}
      {hasWarnings && (
        <div className="space-y-2">
          {notes.warnings!.map((warning, i) => (
            <div
              key={`warn-${i}`}
              className="flex items-start gap-2.5 p-3 rounded-lg bg-amber-500/5 border border-amber-500/15"
            >
              <AlertTriangle
                size={14}
                className="text-amber-400 shrink-0 mt-0.5"
              />
              <p className="text-[11px] text-amber-200/90 leading-relaxed">
                {warning}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Pro tips */}
      {hasTips && (
        <div className="space-y-2">
          {notes.tips!.map((tip, i) => (
            <div
              key={`tip-${i}`}
              className="flex items-start gap-2.5 p-3 rounded-lg bg-blue-500/5 border border-blue-500/15"
            >
              <Lightbulb
                size={14}
                className="text-blue-400 shrink-0 mt-0.5"
              />
              <p className="text-[11px] text-zinc-300 leading-relaxed">{tip}</p>
            </div>
          ))}
        </div>
      )}

      {/* Maintenance */}
      {hasMaintenance && (
        <div className="space-y-2">
          {notes.maintenance!.map((item, i) => (
            <div
              key={`maint-${i}`}
              className="flex items-start gap-2.5 p-3 rounded-lg bg-zinc-800/40 border border-zinc-700/30"
            >
              <Wrench
                size={14}
                className="text-zinc-500 shrink-0 mt-0.5"
              />
              <p className="text-[11px] text-zinc-400 leading-relaxed">
                {item}
              </p>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
};
