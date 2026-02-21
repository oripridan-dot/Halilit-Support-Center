/**
 * Sovereign Nerve — Self-Hosted Frontend Telemetry
 * =================================================
 * Catches uncaught JS errors and unhandled Promise rejections natively in the
 * browser and ships them to the Halilit backend ingestor.
 *
 * Zero vendor dependencies.  No API keys.  100% sovereign.
 *
 * Wired at application boot via main.tsx:
 *   import { initSovereignNerve } from "./telemetry.ts";
 *   initSovereignNerve();
 */

const TELEMETRY_ENDPOINT = "/api/telemetry/crash-report";

/** POST a crash report to the backend ingestor.  Never throws. */
const sendCrashReport = async (
    errorMsg: string,
    stack: string,
    source?: string,
): Promise<void> => {
    try {
        await fetch(TELEMETRY_ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Match the payload shape expected by process_production_error()
            body: JSON.stringify({
                event: { title: errorMsg },
                stacktrace: stack,
                culprit: source ?? "browser",
                timestamp: new Date().toISOString(),
                environment: import.meta.env.MODE ?? "production",
                userAgent: navigator.userAgent,
            }),
            // Best-effort delivery — don't keep the page alive waiting
            keepalive: true,
        });
    } catch (e) {
        // Telemetry must never crash the app
        console.error("[SovereignNerve] delivery failed:", e);
    }
};

/**
 * Install window-level listeners for uncaught errors and unhandled promise
 * rejections.  Call once at application boot.
 */
export const initSovereignNerve = (): void => {
    // ── Synchronous JS errors ────────────────────────────────────────────────
    window.addEventListener("error", (event: ErrorEvent) => {
        const msg = event.message ?? "Uncaught Error";
        const stack = event.error?.stack ?? `${event.filename}:${event.lineno}:${event.colno}`;
        console.error("[SovereignNerve] Uncaught error:", msg);
        sendCrashReport(msg, stack, event.filename ?? undefined);
    });

    // ── Unhandled Promise rejections ─────────────────────────────────────────
    window.addEventListener("unhandledrejection", (event: PromiseRejectionEvent) => {
        const reason = event.reason;
        const msg =
            reason instanceof Error
                ? reason.message
                : reason?.message ?? String(reason) ?? "Unhandled Promise Rejection";
        const stack =
            reason instanceof Error ? (reason.stack ?? "No stack trace") : "No stack trace";
        console.error("[SovereignNerve] Unhandled rejection:", msg);
        sendCrashReport(msg, stack, "promise");
    });

    if (import.meta.env.DEV) {
        console.info(
            "[SovereignNerve] Initialised — crash reports → " + TELEMETRY_ENDPOINT,
        );
    }
};
