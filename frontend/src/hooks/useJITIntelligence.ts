import { useState, useEffect, useCallback, useRef } from "react";
import type { VerdictData } from "../components/cockpit/VerdictCard";
import type { ReviewSource } from "../components/cockpit/TrustedConsensus";
import type { FieldNotesData } from "../components/cockpit/FieldNotes";
import type { ExplorationPath } from "../components/cockpit/ExplorationDock";

/**
 * JIT Intelligence phases:
 *   idle    — Not started
 *   snap    — Loading inventory data (~200ms)
 *   intel   — Reading product pages (~2s)
 *   wisdom  — Consulting trusted sources + AI (~5s)
 *   complete — All data loaded
 *   error   — Something went wrong
 */
export type JITPhase = "idle" | "snap" | "intel" | "wisdom" | "complete" | "error";

export interface JITIntelligenceState {
  phase: JITPhase;
  statusMessage: string;
  snap: SnapData | null;
  officialSpecs: OfficialSpecsData | null;
  verdict: VerdictData | null;
  trustedReviews: ReviewSource[];
  fieldNotes: FieldNotesData | null;
  explorationPaths: ExplorationPath[];
  isComplete: boolean;
  isCached: boolean;
  error: string | null;
}

interface SnapData {
  name: string;
  brand: string;
  price: number;
  price_eilat: number;
  thumbnail: string;
  halilit_url: string;
  category_hint: string;
}

interface OfficialSpecsData {
  specs: Record<string, unknown>;
  features: string[];
  description: string;
  images: string[];
}

const INITIAL_STATE: JITIntelligenceState = {
  phase: "idle",
  statusMessage: "",
  snap: null,
  officialSpecs: null,
  verdict: null,
  trustedReviews: [],
  fieldNotes: null,
  explorationPaths: [],
  isComplete: false,
  isCached: false,
  error: null,
};

/**
 * useJITIntelligence — Connects to the JIT SSE endpoint and progressively
 * populates intelligence data for the Product Cockpit.
 *
 * Usage:
 *   const jit = useJITIntelligence(productId);
 *   // jit.phase, jit.verdict, jit.fieldNotes, etc.
 */
export function useJITIntelligence(productId: string | null) {
  const [state, setState] = useState<JITIntelligenceState>(INITIAL_STATE);
  const abortRef = useRef<AbortController | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(async () => {
    if (!productId) return;

    // Abort any previous connection
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    // Reset state
    setState({ ...INITIAL_STATE, phase: "snap", statusMessage: "Connecting..." });

    try {
      const response = await fetch(`/api/jit/product/${encodeURIComponent(productId)}`, {
        method: "POST",
        signal: controller.signal,
        headers: { Accept: "text/event-stream" },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response body");
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events from buffer
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        let currentEvent = "";
        let currentData = "";

        for (const line of lines) {
          if (line.startsWith("event: ")) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            currentData = line.slice(6);
          } else if (line === "" && currentEvent && currentData) {
            // End of event — process it
            try {
              const data = JSON.parse(currentData);
              processEvent(currentEvent, data, setState);
            } catch (e) {
              console.warn("Failed to parse SSE event:", currentEvent, e);
            }
            currentEvent = "";
            currentData = "";
          }
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") return; // Expected on cleanup
      console.error("JIT stream error:", err);
      setState((prev) => ({
        ...prev,
        phase: "error",
        error: err.message || "Connection failed",
        statusMessage: "Intelligence unavailable",
      }));
    }
  }, [productId]);

  // Connect when productId changes
  useEffect(() => {
    connect();

    return () => {
      abortRef.current?.abort();
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  return state;
}

/**
 * Process a single SSE event and update state accordingly.
 */
function processEvent(
  event: string,
  data: any,
  setState: React.Dispatch<React.SetStateAction<JITIntelligenceState>>,
) {
  switch (event) {
    case "status":
      setState((prev) => ({
        ...prev,
        phase: data.phase as JITPhase || prev.phase,
        statusMessage: data.message || "",
      }));
      break;

    case "snap":
      setState((prev) => ({
        ...prev,
        phase: "snap",
        snap: data,
      }));
      break;

    case "official_specs":
      setState((prev) => ({
        ...prev,
        phase: "intel",
        officialSpecs: data,
      }));
      break;

    case "trusted_reviews":
      setState((prev) => ({
        ...prev,
        trustedReviews: data.reviews || [],
      }));
      break;

    case "verdict":
      setState((prev) => ({
        ...prev,
        verdict: data,
      }));
      break;

    case "field_notes":
      setState((prev) => ({
        ...prev,
        fieldNotes: data,
      }));
      break;

    case "exploration":
      setState((prev) => ({
        ...prev,
        explorationPaths: data.paths || [],
      }));
      break;

    case "complete":
      setState((prev) => ({
        ...prev,
        phase: "complete",
        isComplete: true,
        isCached: data.cached || false,
        statusMessage: data.cached ? "Loaded from cache" : "Intelligence complete",
      }));
      break;

    default:
      console.warn("Unknown JIT event:", event);
  }
}

export default useJITIntelligence;
