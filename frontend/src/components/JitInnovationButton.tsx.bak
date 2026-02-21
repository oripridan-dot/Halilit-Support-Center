/**
 * JitInnovationButton — "Call the Factory" floating widget
 * =========================================================
 * A globally visible, floating action button that lets any Halilit warehouse
 * operator submit an unmet need directly into the JIT Innovation Pipeline.
 *
 * When submitted, the backend's Boardroom → Spec Writer → Repo Agent →
 * Darwin Shadow Cell pipeline runs asynchronously and produces a
 * FEATURE_PROPOSAL.md awaiting Governor review.
 *
 * Usage: Drop <JitInnovationButton /> inside the root App shell.
 */

import React, { useState, useRef, useEffect } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface SubmitResult {
  status: string;
  message: string;
}

type PanelState = "idle" | "submitting" | "success" | "error";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export const JitInnovationButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [need, setNeed] = useState("");
  const [panelState, setPanelState] = useState<PanelState>("idle");
  const [statusMessage, setStatusMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus textarea when panel opens
  useEffect(() => {
    if (isOpen && panelState === "idle") {
      setTimeout(() => textareaRef.current?.focus(), 80);
    }
  }, [isOpen, panelState]);

  // Reset panel to idle state
  const reset = () => {
    setNeed("");
    setPanelState("idle");
    setStatusMessage("");
  };

  const handleOpen = () => {
    reset();
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setTimeout(reset, 300); // Reset after close animation
  };

  const handleSubmit = async () => {
    const trimmed = need.trim();
    if (!trimmed) return;

    setPanelState("submitting");
    setStatusMessage("Waking the Factory…");

    try {
      const response = await fetch("/api/innovation/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          operator_role: "Warehouse Staff",
          current_context: window.location.pathname,
          need_description: trimmed,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data: SubmitResult = await response.json();
      setPanelState("success");
      setStatusMessage(
        data.message ??
          "Pipeline activated. A FEATURE_PROPOSAL will appear in docs/ when ready.",
      );
    } catch (err) {
      setPanelState("error");
      setStatusMessage(
        err instanceof Error
          ? err.message
          : "Unexpected error — check the server logs.",
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <>
      {/* ── Floating Trigger Button ── */}
      <button
        onClick={handleOpen}
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
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          onClick={handleClose}
          aria-hidden="true"
        />
      )}

      {/* ── Panel ── */}
      {isOpen && (
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
                The AI Factory will design, test &amp; propose a solution.
              </p>
            </div>
            <button
              onClick={handleClose}
              aria-label="Close panel"
              className="text-zinc-600 hover:text-zinc-300 transition-colors p-1 rounded-md hover:bg-zinc-800"
            >
              ✕
            </button>
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
                  value={need}
                  onChange={(e) => setNeed(e.target.value)}
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
                  onClick={handleClose}
                  className="text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  disabled={!need.trim()}
                  className="
                    px-4 py-1.5 rounded-lg text-xs font-semibold
                    bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed
                    text-white transition-all active:scale-95
                  "
                >
                  Send to Factory →
                </button>
              </>
            )}
            {(panelState === "success" || panelState === "error") && (
              <button
                onClick={panelState === "success" ? handleClose : reset}
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
