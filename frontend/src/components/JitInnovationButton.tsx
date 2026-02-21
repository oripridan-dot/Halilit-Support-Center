/**
 * JitInnovationButton — "Call the Factory" floating widget
 * =========================================================
 * A globally visible, floating action button that lets any Halilit warehouse
 * operator submit an unmet need directly into the JIT Innovation Pipeline.
 *
 * Level 10 Upgrade:
 *   • "Liquid" mode (default) — calls /api/innovation/liquid and renders
 *     the result instantly via <LiquidCanvas /> with no compilation.
 *   • "Deep" mode — calls /api/innovation/request and triggers the full
 *     Boardroom → Spec Writer → Repo Agent → Darwin pipeline.
 *
 * Usage: Drop <JitInnovationButton /> inside the root App shell.
 */

import React, { useState, useRef, useEffect } from "react";
import { LiquidCanvas, type LiquidSchema } from "./LiquidCanvas";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/**
 * Represents the result of submitting an innovation request to the deep pipeline.
 */
interface InnovationRequestResult {
  status: string;
  message: string;
}

/**
 * Represents the result of a Liquid JIT synthesis.
 */
interface LiquidRequestResult {
  status: "success" | "error";
  ui_schema?: LiquidSchema;
  sql_preview?: string;
  message?: string;
}

/**
 * Represents the different states of the innovation panel.
 * "liquid" = LiquidCanvas overlay is active.
 */
type InnovationPanelState =
  | "idle"
  | "submitting"
  | "success"
  | "error"
  | "liquid";

/** Submission mode: instant SDUI ("liquid") or full file-writing pipeline ("deep"). */
type SubmitMode = "liquid" | "deep";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * A floating action button that allows users to submit innovation requests.
 */
export const JitInnovationButton: React.FC = () => {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [innovationNeed, setInnovationNeed] = useState("");
  const [panelState, setPanelState] = useState<InnovationPanelState>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const [submitMode, setSubmitMode] = useState<SubmitMode>("liquid");
  const [liquidSchema, setLiquidSchema] = useState<LiquidSchema | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Auto-focuses the textarea when the panel opens.
   */
  useEffect(() => {
    if (isPanelOpen && panelState === "idle") {
      setTimeout(() => textareaRef.current?.focus(), 80);
    }
  }, [isPanelOpen, panelState]);

  /**
   * Resets the panel to the idle state, clearing input and messages.
   */
  const resetPanel = (): void => {
    setInnovationNeed("");
    setPanelState("idle");
    setStatusMessage("");
    setLiquidSchema(null);
  };

  /**
   * Opens the innovation panel.
   */
  const handleOpenPanel = (): void => {
    resetPanel();
    setIsPanelOpen(true);
  };

  /**
   * Closes the panel and resets its state after a short delay to allow for animation.
   */
  const handleClosePanel = (): void => {
    setIsPanelOpen(false);
    setTimeout(resetPanel, 300); // Reset after close animation
  };

  /**
   * Handles the submission of the innovation request to the backend.
   * Routes to /api/innovation/liquid (Liquid mode) or /api/innovation/request (Deep mode).
   */
  const handleSubmit = async (): Promise<void> => {
    const trimmedNeed = innovationNeed.trim();
    if (!trimmedNeed) return;

    setPanelState("submitting");

    if (submitMode === "liquid") {
      setStatusMessage("Liquid Engine synthesising…");
      try {
        const response = await fetch("/api/innovation/liquid", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operator_role: "Warehouse Staff",
            current_context: window.location.pathname,
            need_description: trimmedNeed,
          }),
        });

        if (!response.ok)
          throw new Error(`Server responded with ${response.status}`);

        const data: LiquidRequestResult = await response.json();

        if (data.status === "success" && data.ui_schema) {
          setLiquidSchema(data.ui_schema);
          setIsPanelOpen(false); // collapse the input panel
          setPanelState("liquid"); // show the canvas
        } else {
          setPanelState("error");
          setStatusMessage(
            data.message ?? "Liquid synthesis returned no schema.",
          );
        }
      } catch (err) {
        setPanelState("error");
        setStatusMessage(
          err instanceof Error ? err.message : "Unexpected error — check logs.",
        );
      }
    } else {
      // Deep mode — full pipeline (async, proposal written to docs/)
      setStatusMessage("Waking the Factory…");
      try {
        const response = await fetch("/api/innovation/request", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            operator_role: "Warehouse Staff",
            current_context: window.location.pathname,
            need_description: trimmedNeed,
          }),
        });

        if (!response.ok)
          throw new Error(`Server responded with ${response.status}`);

        const data: InnovationRequestResult = await response.json();
        setPanelState("success");
        setStatusMessage(
          data.message ??
            "Pipeline activated. A FEATURE_PROPOSAL will appear in docs/ when ready.",
        );
      } catch (error) {
        setPanelState("error");
        setStatusMessage(
          error instanceof Error
            ? error.message
            : "Unexpected error — check the server logs.",
        );
      }
    }
  };

  /**
   * Handles keyboard input for the textarea, submitting the form when Cmd/Ctrl + Enter is pressed.
   */
  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>): void => {
    if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
      event.preventDefault();
      handleSubmit();
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <>
      {/* ── Liquid Canvas (full-screen overlay when a schema is ready) ── */}
      {panelState === "liquid" && liquidSchema && (
        <LiquidCanvas schema={liquidSchema} onClose={resetPanel} />
      )}

      {/* ── Floating Trigger Button ── */}
      <button
        onClick={handleOpenPanel}
        title="Request a JIT Feature from the AI Factory"
        aria-label="Open JIT Innovation Panel"
        className="
          fixed bottom-5 right-5 z-50
          w-12 h-12 rounded-full
          bg-blue-600 hover:bg-blue-500 active:scale-95
          shadow-lg shadow-blue-900/40
          flex items-center justify-center
          text-white text-xl
          transition-all duration-150
          focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 focus:ring-offset-black
        "
      >
        💡
      </button>

      {/* ── Overlay backdrop ── */}
      {isPanelOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={handleClosePanel}
          aria-hidden="true"
        />
      )}

      {/* ── Panel ── */}
      {isPanelOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="jit-panel-title"
          className="
            fixed bottom-20 right-5 z-50
            w-[380px] max-w-[calc(100vw-2rem)]
            rounded-2xl border border-zinc-800
            bg-[#0f0f0f] shadow-2xl shadow-black/60
            flex flex-col overflow-hidden
            transition-all duration-200
          "
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800/60">
            <div>
              <h2
                id="jit-panel-title"
                className="text-sm font-semibold text-zinc-100 tracking-tight"
              >
                💡 Request a JIT Feature
              </h2>
              <p className="text-[11px] text-zinc-500 mt-0.5">
                {submitMode === "liquid"
                  ? "Liquid mode — instant SDUI, no compilation."
                  : "Deep mode — full pipeline + spec proposal."}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {/* Mode toggle */}
              <div className="flex rounded-md overflow-hidden border border-zinc-700 text-[10px] font-medium">
                <button
                  onClick={() => setSubmitMode("liquid")}
                  className={`px-2.5 py-1 transition-colors ${
                    submitMode === "liquid"
                      ? "bg-blue-600 text-white"
                      : "bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                  }`}
                  title="Liquid: instant Server-Driven UI"
                >
                  🌊 Liquid
                </button>
                <button
                  onClick={() => setSubmitMode("deep")}
                  className={`px-2.5 py-1 transition-colors ${
                    submitMode === "deep"
                      ? "bg-purple-700 text-white"
                      : "bg-zinc-800 text-zinc-400 hover:text-zinc-200"
                  }`}
                  title="Deep: full factory pipeline + proposal"
                >
                  🧬 Deep
                </button>
              </div>
              <button
                onClick={handleClosePanel}
                aria-label="Close panel"
                className="text-zinc-600 hover:text-zinc-300 transition-colors p-1 rounded-md hover:bg-zinc-800"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Body */}
          <div className="px-5 py-4 flex flex-col gap-3">
            {panelState === "idle" && (
              <>
                <label
                  htmlFor="jit-need-input"
                  className="text-[11px] font-medium text-zinc-400 uppercase tracking-widest"
                >
                  What do you need?
                </label>
                <textarea
                  id="jit-need-input"
                  ref={textareaRef}
                  value={innovationNeed}
                  onChange={(e) => setInnovationNeed(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g. I need a printable PDF table for RMA repairs with broken serial numbers."
                  rows={4}
                  className="
                    w-full resize-none rounded-lg
                    bg-zinc-900 border border-zinc-700/60
                    px-3 py-2.5 text-sm text-zinc-200
                    placeholder:text-zinc-600
                    focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
                    transition-colors
                  "
                />
                <p className="text-[10px] text-zinc-600">
                  Press{" "}
                  <kbd className="px-1 py-0.5 rounded bg-zinc-800 text-zinc-400 text-[9px]">
                    ⌘ Enter
                  </kbd>{" "}
                  or click Send.
                </p>
              </>
            )}

            {panelState === "submitting" && (
              <div className="flex flex-col items-center gap-3 py-6">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                <p className="text-sm text-zinc-400">{statusMessage}</p>
              </div>
            )}

            {panelState === "success" && (
              <div className="flex flex-col gap-3 py-2">
                <div className="flex items-start gap-3 rounded-lg bg-emerald-950/40 border border-emerald-800/40 px-3 py-3">
                  <span className="text-emerald-400 text-lg mt-0.5">✅</span>
                  <p className="text-sm text-emerald-300 leading-snug">
                    {statusMessage}
                  </p>
                </div>
                <p className="text-[11px] text-zinc-500">
                  Check{" "}
                  <code className="text-zinc-400">
                    docs/FEATURE_PROPOSAL_*.md
                  </code>{" "}
                  when the pipeline completes.
                </p>
              </div>
            )}

            {panelState === "error" && (
              <div className="flex flex-col gap-3 py-2">
                <div className="flex items-start gap-3 rounded-lg bg-red-950/40 border border-red-800/40 px-3 py-3">
                  <span className="text-red-400 text-lg mt-0.5">⚠️</span>
                  <p className="text-sm text-red-300 leading-snug">
                    {statusMessage}
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Footer actions */}
          <div className="px-5 pb-4 flex items-center justify-between gap-2">
            {panelState === "idle" && (
              <>
                <button
                  onClick={handleClosePanel}
                  className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!innovationNeed.trim()}
                  className={`
                    px-4 py-1.5 rounded-lg text-xs font-semibold
                    ${
                      submitMode === "liquid"
                        ? "bg-blue-600 hover:bg-blue-500"
                        : "bg-purple-700 hover:bg-purple-600"
                    } disabled:opacity-40 disabled:cursor-not-allowed
                    text-white transition-all active:scale-95
                  `}
                >
                  {submitMode === "liquid"
                    ? "🌊 Synthesise"
                    : "🧬 Send to Factory →"}
                </button>
              </>
            )}
            {(panelState === "success" || panelState === "error") && (
              <button
                onClick={
                  panelState === "success" ? handleClosePanel : resetPanel
                }
                className="
                  ml-auto px-4 py-1.5 rounded-lg text-xs font-semibold
                  bg-zinc-800 hover:bg-zinc-700 text-zinc-200 transition-all active:scale-95
                "
              >
                {panelState === "success" ? "Done" : "Try again"}
              </button>
            )}
          </div>
        </div>
      )}
    </>
  );
};

export default JitInnovationButton;