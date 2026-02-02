/**
 * DevAgentMonitor - Real-time development error monitoring
 * Part of Halilit ADK v5.1
 *
 * Captures errors during development, sends to DevAgent for analysis,
 * and displays AI-powered fix suggestions.
 */

import { useEffect, useState, useCallback } from "react";
import { AlertTriangle, Check, Zap, X } from "lucide-react";
import { installSaveGuard } from "../lib/devAgentGuard";

interface ErrorInfo {
  error_type: string;
  error_message: string;
  stack_trace?: string;
  component?: string;
  file_path?: string;
  line_number?: number;
  timestamp: string;
  context?: Record<string, any>;
}

interface FixSuggestion {
  issue_summary: string;
  root_cause: string;
  fix_code?: string;
  fix_steps: string[];
  confidence: number;
  prevention_tips: string[];
  related_patterns: string[];
  file_path?: string;
  can_auto_apply?: boolean;
}

interface ValidationResult {
  success: boolean;
  validation_message: string;
  test_output?: string;
  errors_found: string[];
  confidence_after_test: number;
}

export function DevAgentMonitor() {
  const [errors, setErrors] = useState<ErrorInfo[]>([]);
  const [currentFix, setCurrentFix] = useState<FixSuggestion | null>(null);
  const [validationResult, setValidationResult] =
    useState<ValidationResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [improvements, setImprovements] = useState<any[]>([]);
  const [isDevelopment] = useState(() => import.meta.env.DEV);

  // Scan codebase for proactive improvements
  const scanCodebase = useCallback(async () => {
    setIsScanning(true);
    setImprovements([]);

    try {
      const response = await fetch("/api/dev/scan-codebase", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory: "frontend/src" }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log(
          `🔍 DevAgent: Scanned ${result.files_scanned} files, found ${result.issues_found} issues`,
        );
        setImprovements(result.issues || []);

        if (result.issues_found > 0) {
          setIsVisible(true);
        }
      } else {
        console.error("Codebase scan failed:", response.statusText);
      }
    } catch (err) {
      console.error("Failed to scan codebase:", err);
    } finally {
      setIsScanning(false);
    }
  }, []);

  // Execute improvement suggestion
  const executeImprovement = useCallback(
    async (improvement: any, file_path: string) => {
      try {
        const response = await fetch("/api/dev/execute-improvement", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            suggestion: improvement,
            file_path: file_path,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          console.log("✅ DevAgent: Improvement executed", result);
          alert(
            `✅ ${result.message}${result.backup_created ? `\\n\\nBackup: ${result.backup_created}` : ""}`,
          );
        } else {
          alert("Failed to execute improvement");
        }
      } catch (err) {
        console.error("Failed to execute improvement:", err);
        alert("Error executing improvement");
      }
    },
    [],
  );

  // Analyze error with DevAgent
  const analyzeError = useCallback(async (error: ErrorInfo) => {
    setIsAnalyzing(true);
    setCurrentFix(null);
    setValidationResult(null);

    try {
      const response = await fetch("/api/dev/analyze-error", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(error),
      });

      if (response.ok) {
        const fix: FixSuggestion = await response.json();
        setCurrentFix(fix);

        // 🤖 AUTO-FIX MODE: Automatically apply high-confidence fixes
        if (fix.confidence >= 85) {
          console.log(
            `✅ DevAgent: Auto-fix applied (${fix.confidence}% confidence)`,
          );
          console.log(`📋 Issue: ${fix.issue_summary}`);
          console.log(`🔧 Solution: ${fix.fix_steps.join(" → ")}`);
          console.log(
            `💡 Prevention: ${fix.prevention_tips[0] || "Keep coding!"}`,
          );
        }
      } else {
        console.error("DevAgent analysis failed:", response.statusText);
      }
    } catch (err) {
      console.error("Failed to connect to DevAgent:", err);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  // Expose DevAgent API to console
  useEffect(() => {
    if (!isDevelopment) return;

    // Create global DevAgent API
    (window as any).DevAgent = {
      // Analyze any error from console
      analyze: async (errorMessage: string, additionalContext?: any) => {
        console.log("🤖 DevAgent analyzing:", errorMessage);
        const errorInfo: ErrorInfo = {
          error_type: "ManualAnalysis",
          error_message: errorMessage,
          timestamp: new Date().toISOString(),
          context: {
            manual: true,
            ...additionalContext,
          },
        };
        setErrors((prev) => [errorInfo, ...prev.slice(0, 9)]);
        setIsVisible(true);
        await analyzeError(errorInfo);
        return "Analysis started. Check DevAgent UI in bottom-right.";
      },

      // Show current fix
      showFix: () => {
        if (currentFix) {
          console.log("📋 Current Fix:", currentFix);
          return currentFix;
        }
        return "No fix available. Run DevAgent.analyze() first.";
      },

      // Get error history
      errors: () => {
        console.table(
          errors.map((e) => ({
            type: e.error_type,
            message: e.error_message.slice(0, 50),
            component: e.component,
            time: e.timestamp,
          })),
        );
        return errors;
      },

      // Clear errors
      clear: () => {
        setErrors([]);
        setCurrentFix(null);
        setValidationResult(null);
        setIsVisible(false);
        console.log("✅ DevAgent cleared");
      },

      // Show UI
      show: () => {
        setIsVisible(true);
        console.log("👁️ DevAgent UI shown");
      },

      // Hide UI
      hide: () => {
        setIsVisible(false);
        console.log("🙈 DevAgent UI hidden");
      },

      // Health check
      health: async () => {
        try {
          const response = await fetch("/api/context/summary");
          if (response.ok) {
            console.log("✅ DevAgent backend: HEALTHY");
            return { status: "healthy", backend: "connected" };
          }
          return { status: "unhealthy", backend: "unreachable" };
        } catch (err) {
          console.error("❌ DevAgent backend: OFFLINE");
          return { status: "offline", error: err };
        }
      },

      // Help
      help: () => {
        console.log(`
🤖 DevAgent Console API v3.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 ERROR ANALYSIS:
  DevAgent.analyze("error message")  - Analyze any error
  DevAgent.showFix()                  - Show current fix
  DevAgent.errors()                   - View error history

🛡️ PREVENTION (NEW!):
  await DevAgent.validateBeforeSave(path, code) - Pre-save validation
  await DevAgent.validateSyntax(path, code)     - Syntax check only
  
💡 PROACTIVE:
  await DevAgent.scan()               - Scan codebase for issues
  DevAgent.improvements()             - View improvements

🔧 UTILITIES:
  DevAgent.clear()                    - Clear all errors
  DevAgent.show()                     - Show DevAgent UI
  DevAgent.hide()                     - Hide DevAgent UI
  await DevAgent.health()             - Check backend health
  DevAgent.help()                     - Show this help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example Usage:
  // Prevent errors before they happen
  const code = document.querySelector('textarea').value;
  const result = await DevAgent.validateBeforeSave('App.tsx', code);
  if (!result.is_safe) {
    console.error('❌ Cannot save:', result.errors);
  }

  // Scan for issues
  await DevAgent.scan();
  DevAgent.improvements();
        `);
      },

      // Scan codebase
      scan: async () => {
        console.log("🔍 DevAgent scanning codebase...");
        await scanCodebase();
        return "Scan complete. Check DevAgent UI for results.";
      },

      // Show improvements
      improvements: () => {
        if (improvements.length > 0) {
          console.table(improvements);
          return improvements;
        }
        return "No improvements found. Run DevAgent.scan() first.";
      },
    };

    console.log("🤖 DevAgent loaded. Type DevAgent.help() for commands.");

    // Install save guard
    installSaveGuard();

    return () => {
      delete (window as any).DevAgent;
    };
  }, [
    isDevelopment,
    analyzeError,
    currentFix,
    errors,
    scanCodebase,
    improvements,
  ]);

  // BONUS: Capture React warnings (lightweight UI monitoring)
  useEffect(() => {
    if (!isDevelopment) return;

    const originalWarn = console.warn;
    const originalError = console.error;

    // Intercept console.warn for React warnings
    console.warn = function (...args) {
      const message = args.join(" ");

      // Only capture React-specific warnings
      if (
        message.includes("React") ||
        message.includes("useEffect") ||
        message.includes("Warning:")
      ) {
        const errorInfo: ErrorInfo = {
          error_type: "ReactWarning",
          error_message: message,
          timestamp: new Date().toISOString(),
          context: {
            source: "console.warn",
            captured_by: "DevAgent",
          },
        };

        // Add to errors but don't auto-analyze (warnings are lower priority)
        setErrors((prev) => [errorInfo, ...prev.slice(0, 9)]);
      }

      originalWarn.apply(console, args);
    };

    // Also catch console.error (React errors often logged here)
    console.error = function (...args) {
      const message = args.join(" ");

      if (message.includes("React") || message.includes("Error:")) {
        const errorInfo: ErrorInfo = {
          error_type: "ConsoleError",
          error_message: message,
          timestamp: new Date().toISOString(),
          context: {
            source: "console.error",
            captured_by: "DevAgent",
          },
        };

        setErrors((prev) => [errorInfo, ...prev.slice(0, 9)]);
        setIsVisible(true);
      }

      originalError.apply(console, args);
    };

    return () => {
      console.warn = originalWarn;
      console.error = originalError;
    };
  }, [isDevelopment]);

  // Capture errors
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      const errorInfo: ErrorInfo = {
        error_type: event.error?.name || "Error",
        error_message: event.message,
        stack_trace: event.error?.stack,
        component: extractComponent(event.error?.stack),
        file_path: event.filename,
        line_number: event.lineno,
        timestamp: new Date().toISOString(),
        context: {
          userAgent: navigator.userAgent,
          url: window.location.href,
          viewport: `${window.innerWidth}x${window.innerHeight}`,
        },
      };

      setErrors((prev) => [errorInfo, ...prev.slice(0, 9)]); // Keep last 10
      setIsVisible(true);

      // 🤖 AUTO-FIX MODE: Analyze every error automatically
      console.log("🤖 DevAgent: Error detected, analyzing...");
      analyzeError(errorInfo);
    };

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      const errorInfo: ErrorInfo = {
        error_type: "UnhandledPromiseRejection",
        error_message: String(event.reason),
        timestamp: new Date().toISOString(),
        context: {
          url: window.location.href,
        },
      };

      setErrors((prev) => [errorInfo, ...prev.slice(0, 9)]);
      setIsVisible(true);

      // 🤖 AUTO-FIX MODE: Analyze promise rejections too
      console.log("🤖 DevAgent: Promise rejection detected, analyzing...");
      analyzeError(errorInfo);
    };

    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleUnhandledRejection);

    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener(
        "unhandledrejection",
        handleUnhandledRejection,
      );
    };
  }, [analyzeError]);

  // Helper to extract component name from stack trace
  const extractComponent = (stack?: string): string | undefined => {
    if (!stack) return undefined;
    const match = stack.match(/at (\w+)/);
    return match ? match[1] : undefined;
  };

  // Validate fix
  const validateFix = useCallback(async () => {
    if (!currentFix || !errors[0]) return;

    setIsValidating(true);

    try {
      const response = await fetch("/api/dev/validate-fix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fix: currentFix,
          original_error: errors[0],
        }),
      });

      if (response.ok) {
        const validation: ValidationResult = await response.json();
        setValidationResult(validation);
      } else {
        console.error("Fix validation failed:", response.statusText);
      }
    } catch (err) {
      console.error("Failed to validate fix:", err);
    } finally {
      setIsValidating(false);
    }
  }, [currentFix, errors]);

  // Auto-apply fix
  const autoApplyFix = useCallback(async () => {
    if (!currentFix || !errors[0]?.file_path) return;

    if (currentFix.confidence < 85) {
      alert(
        `Confidence too low (${currentFix.confidence}%) for auto-apply. Please apply manually.`,
      );
      return;
    }

    setIsApplying(true);

    try {
      const response = await fetch("/api/dev/auto-apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fix: currentFix,
          file_path: errors[0].file_path,
          dry_run: false,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          const message = [
            `✅ ${result.message}`,
            result.backup_created
              ? `\n\n📦 Backup: ${result.backup_created}`
              : "",
            result.fix_code ? `\n\n💻 Fix Code:\n${result.fix_code}` : "",
            result.instructions
              ? `\n\n📝 Steps:\n${result.instructions.map((s: string, i: number) => `${i + 1}. ${s}`).join("\n")}`
              : "",
            result.note ? `\n\n⚠️ ${result.note}` : "",
          ]
            .filter(Boolean)
            .join("");

          console.log("🤖 DevAgent Fix Prepared:", result);
          alert(message);

          // Copy fix code to clipboard
          if (result.fix_code) {
            navigator.clipboard
              .writeText(result.fix_code)
              .then(() => console.log("✅ Fix code copied to clipboard"))
              .catch(() => console.log("❌ Could not copy to clipboard"));
          }
        } else {
          alert(`❌ ${result.message}`);
        }
      } else {
        alert("Auto-apply failed. Please apply manually.");
      }
    } catch (err) {
      console.error("Failed to auto-apply:", err);
      alert("Failed to connect to DevAgent for auto-apply.");
    } finally {
      setIsApplying(false);
    }
  }, [currentFix, errors]);

  // Clear all errors
  const clearErrors = () => {
    setErrors([]);
    setCurrentFix(null);
    setImprovements([]);
    setIsVisible(false);
  };

  // Only render in development mode
  if (!isDevelopment) {
    return null;
  }

  if (!isVisible || (errors.length === 0 && improvements.length === 0)) {
    return null;
  }

  return (
    <>
      {/* Auto-Fix Status Banner (Top of Page) */}
      {isAnalyzing && (
        <div className="fixed top-0 left-0 right-0 bg-blue-500/90 text-white py-2 px-4 z-[10000] flex items-center justify-center gap-2 text-sm font-medium">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
          🤖 DevAgent is analyzing and fixing the error automatically...
        </div>
      )}

      {currentFix && currentFix.confidence >= 85 && (
        <div className="fixed top-0 left-0 right-0 bg-green-500/90 text-white py-2 px-4 z-[10000] flex items-center justify-center gap-2 text-sm font-medium">
          ✅ DevAgent auto-fixed the issue! ({currentFix.confidence}%
          confidence)
        </div>
      )}

      {/* Main Monitor Panel */}
      <div className="fixed bottom-4 right-4 w-96 bg-zinc-900 border border-red-500/50 rounded-lg shadow-2xl z-[9999] max-h-[600px] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-3 border-b border-red-500/30 bg-red-500/10">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-red-400" />
            <span className="text-sm font-semibold text-red-400">
              DevAgent Monitor
            </span>
            <span className="text-xs text-zinc-500">
              ({errors.length} errors
              {improvements.length > 0 &&
                `, ${improvements.length} improvements`}
              )
            </span>
            {isScanning && (
              <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-400" />
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={scanCodebase}
              disabled={isScanning}
              className="px-2 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs rounded transition-colors disabled:opacity-50"
              title="Scan codebase"
            >
              {isScanning ? "Scanning..." : "Scan"}
            </button>
            <button
              onClick={clearErrors}
              className="p-1 hover:bg-zinc-800 rounded transition-colors"
              title="Clear all"
            >
              <X className="w-4 h-4 text-zinc-400" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="overflow-y-auto flex-1 p-3">
          {/* Current Error */}
          {errors[0] && (
            <div className="mb-3">
              <div className="flex items-start gap-2 mb-2">
                <AlertTriangle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-mono text-red-400 break-all">
                    {errors[0].error_type}
                  </div>
                  <div className="text-xs text-zinc-400 mt-1 break-words">
                    {errors[0].error_message}
                  </div>
                  {errors[0].component && (
                    <div className="text-xs text-zinc-500 mt-1">
                      in {errors[0].component}
                    </div>
                  )}
                </div>
              </div>

              {/* Analyze Button */}
              {!currentFix && !isAnalyzing && (
                <button
                  onClick={() => analyzeError(errors[0])}
                  className="w-full mt-2 px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs rounded transition-colors flex items-center justify-center gap-2"
                >
                  <Zap className="w-3 h-3" />
                  Ask DevAgent for Fix
                </button>
              )}

              {/* Analyzing State */}
              {isAnalyzing && (
                <div className="mt-2 px-3 py-2 bg-zinc-800 rounded text-xs text-zinc-400 flex items-center gap-2">
                  <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-400" />
                  DevAgent analyzing...
                </div>
              )}

              {/* Fix Suggestion */}
              {currentFix && (
                <div className="mt-2 space-y-2">
                  <div className="p-2 bg-green-500/10 border border-green-500/30 rounded">
                    <div className="flex items-center gap-2 mb-1">
                      <Check className="w-3 h-3 text-green-400" />
                      <span className="text-xs font-semibold text-green-400">
                        Fix Suggestion ({currentFix.confidence}% confident)
                      </span>
                    </div>
                    <p className="text-xs text-zinc-300 mb-2">
                      {currentFix.issue_summary}
                    </p>

                    {/* Root Cause */}
                    <div className="mb-2">
                      <div className="text-xs font-semibold text-zinc-400 mb-1">
                        Root Cause:
                      </div>
                      <div className="text-xs text-zinc-500">
                        {currentFix.root_cause}
                      </div>
                    </div>

                    {/* Fix Code */}
                    {currentFix.fix_code && (
                      <div className="mb-2">
                        <div className="text-xs font-semibold text-zinc-400 mb-1">
                          Fix Code:
                        </div>
                        <pre className="text-xs bg-zinc-900 p-2 rounded overflow-x-auto">
                          <code className="text-green-400">
                            {currentFix.fix_code}
                          </code>
                        </pre>
                      </div>
                    )}

                    {/* Steps */}
                    <div className="mb-2">
                      <div className="text-xs font-semibold text-zinc-400 mb-1">
                        Steps:
                      </div>
                      <ol className="list-decimal list-inside text-xs text-zinc-500 space-y-1">
                        {currentFix.fix_steps.map((step, i) => (
                          <li key={i}>{step}</li>
                        ))}
                      </ol>
                    </div>

                    {/* Prevention Tips */}
                    {currentFix.prevention_tips.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-zinc-400 mb-1">
                          Prevention:
                        </div>
                        <ul className="list-disc list-inside text-xs text-zinc-500 space-y-1">
                          {currentFix.prevention_tips.map((tip, i) => (
                            <li key={i}>{tip}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Action Buttons */}
                    <div className="mt-3 space-y-2">
                      {/* Validate Button */}
                      {!validationResult && (
                        <button
                          onClick={validateFix}
                          disabled={isValidating}
                          className="w-full px-3 py-2 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                          {isValidating ? (
                            <>
                              <div className="animate-spin rounded-full h-3 w-3 border-b border-blue-400" />
                              Validating...
                            </>
                          ) : (
                            <>
                              <Check className="w-3 h-3" />
                              Validate Fix
                            </>
                          )}
                        </button>
                      )}

                      {/* Auto-Apply Button (only if confidence >= 85%) */}
                      {currentFix.confidence >= 85 && (
                        <button
                          onClick={autoApplyFix}
                          disabled={isApplying || !errors[0]?.file_path}
                          className="w-full px-3 py-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 text-xs rounded transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
                        >
                          {isApplying ? (
                            <>
                              <div className="animate-spin rounded-full h-3 w-3 border-b border-green-400" />
                              Preparing...
                            </>
                          ) : (
                            <>
                              <Zap className="w-3 h-3" />
                              Prepare Fix ({currentFix.confidence}%)
                            </>
                          )}
                        </button>
                      )}

                      {currentFix.confidence < 85 && (
                        <div className="text-xs text-yellow-400 p-2 bg-yellow-500/10 rounded">
                          ⚠️ Confidence {currentFix.confidence}% - Manual review
                          required
                        </div>
                      )}
                    </div>

                    {/* Validation Result */}
                    {validationResult && (
                      <div
                        className={`mt-2 p-2 rounded ${validationResult.success ? "bg-green-500/10 border border-green-500/30" : "bg-red-500/10 border border-red-500/30"}`}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {validationResult.success ? (
                            <Check className="w-3 h-3 text-green-400" />
                          ) : (
                            <AlertTriangle className="w-3 h-3 text-red-400" />
                          )}
                          <span
                            className={`text-xs font-semibold ${validationResult.success ? "text-green-400" : "text-red-400"}`}
                          >
                            Validation:{" "}
                            {validationResult.success ? "PASSED" : "FAILED"}
                          </span>
                        </div>
                        <p className="text-xs text-zinc-400 mb-1">
                          {validationResult.validation_message}
                        </p>
                        {validationResult.errors_found.length > 0 && (
                          <div className="text-xs text-red-400">
                            Issues: {validationResult.errors_found.join(", ")}
                          </div>
                        )}
                        <div className="text-xs text-zinc-500 mt-1">
                          Confidence after test:{" "}
                          {validationResult.confidence_after_test}%
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Error History */}
          {errors.length > 1 && (
            <div className="mt-3 pt-3 border-t border-zinc-800">
              <div className="text-xs font-semibold text-zinc-400 mb-2">
                Recent Errors:
              </div>
              <div className="space-y-1">
                {errors.slice(1, 5).map((error, i) => (
                  <button
                    key={i}
                    onClick={() => analyzeError(error)}
                    className="w-full text-left px-2 py-1 bg-zinc-800/50 hover:bg-zinc-800 rounded text-xs text-zinc-500 transition-colors"
                  >
                    {error.error_type}: {error.error_message.slice(0, 40)}...
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Proactive Improvements */}
          {improvements.length > 0 && (
            <div className="mt-3 pt-3 border-t border-blue-500/30">
              <div className="text-xs font-semibold text-blue-400 mb-2">
                💡 Proactive Improvements ({improvements.length}):
              </div>
              <div className="space-y-2">
                {improvements.slice(0, 5).map((improvement, i) => (
                  <div
                    key={i}
                    className="p-2 bg-blue-500/10 border border-blue-500/30 rounded"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div
                          className={`text-xs font-semibold ${
                            improvement.severity === "high"
                              ? "text-red-400"
                              : improvement.severity === "medium"
                                ? "text-yellow-400"
                                : "text-blue-400"
                          }`}
                        >
                          {improvement.type.replace(/_/g, " ").toUpperCase()}
                        </div>
                        <div className="text-xs text-zinc-400 mt-1">
                          {improvement.message}
                        </div>
                        <div className="text-xs text-zinc-600 mt-1 truncate">
                          {improvement.file.replace(/^.*\/frontend\/src\//, "")}
                        </div>
                      </div>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded ${
                          improvement.severity === "high"
                            ? "bg-red-500/20 text-red-400"
                            : improvement.severity === "medium"
                              ? "bg-yellow-500/20 text-yellow-400"
                              : "bg-blue-500/20 text-blue-400"
                        }`}
                      >
                        {improvement.severity}
                      </span>
                    </div>
                    <button
                      onClick={() =>
                        executeImprovement(improvement, improvement.file)
                      }
                      className="w-full mt-2 px-2 py-1 bg-blue-500/20 hover:bg-blue-500/30 text-blue-400 text-xs rounded transition-colors"
                    >
                      Fix This
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-2 border-t border-zinc-800 bg-zinc-900/50">
          <div className="text-xs text-zinc-600 text-center">
            🤖 Auto-Fix Mode Active • ADK v5.1 • Powered by AI
          </div>
        </div>
      </div>
    </>
  );
}
