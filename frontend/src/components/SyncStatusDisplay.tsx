/**
 * SyncStatusDisplay Component
 * Shows real-time sync progress and status updates
 */

import React, { useState } from "react";
import { useSyncUpdates, useProgressTracker } from "../hooks/useSyncUpdates";

export interface SyncStatusDisplayProps {
  onSyncComplete?: (result: any) => void;
  showHistory?: boolean;
}

export const SyncStatusDisplay: React.FC<SyncStatusDisplayProps> = ({
  onSyncComplete,
  showHistory = true,
}) => {
  const { syncProduct, syncBatch, progress, isLoading, error, status } =
    useSyncUpdates();
  const { trackProgress } = useProgressTracker();
  const [showDetails, setShowDetails] = useState(false);

  const handleSyncClick = async (testProduct?: any) => {
    const product = testProduct || {
      product_id: "test-sync-001",
      product_name: "Nord Piano 6",
      brand: "Nord",
      category: "Digital Piano",
      status: "APPROVED",
      risk_score: 15,
    };

    await syncProduct(product, (event) => {
      trackProgress(event);
      console.log("Sync event:", event);
    });

    if (status === "completed") {
      onSyncComplete?.(product);
    }
  };

  return (
    <div className="w-full bg-slate-900 rounded-lg border border-slate-700 p-6 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`w-3 h-3 rounded-full ${
              isLoading
                ? "bg-blue-500 animate-pulse"
                : status === "completed"
                  ? "bg-green-500"
                  : status === "error"
                    ? "bg-red-500"
                    : "bg-slate-500"
            }`}
          />
          <h3 className="text-lg font-semibold text-white">Sync Status</h3>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-slate-400 hover:text-blue-400 transition"
        >
          {showDetails ? "Hide" : "Show"} Details
        </button>
      </div>

      {/* Status Badge */}
      <div className="flex gap-2 items-center">
        <span className="text-sm text-slate-400">Status:</span>
        <span
          className={`px-3 py-1 rounded-full text-xs font-semibold ${
            status === "completed"
              ? "bg-green-900 text-green-200"
              : status === "syncing"
                ? "bg-blue-900 text-blue-200"
                : status === "error"
                  ? "bg-red-900 text-red-200"
                  : "bg-slate-800 text-slate-400"
          }`}
        >
          {status.toUpperCase()}
        </span>
      </div>

      {/* Progress Bar (if syncing) */}
      {isLoading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">{progress.currentPhase}</span>
            <span className="text-slate-400">
              {Math.round(progress.percentComplete)}%
            </span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-blue-500 h-full rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress.percentComplete}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="bg-red-900/20 border border-red-700 rounded p-3 text-red-200 text-sm">
          <span className="font-semibold">Error: </span>
          {error}
        </div>
      )}

      {/* Details Section */}
      {showDetails && (
        <div className="bg-slate-800 rounded p-4 space-y-3 max-h-64 overflow-y-auto">
          <h4 className="text-sm font-semibold text-white">Events</h4>
          {progress.events.length === 0 ? (
            <p className="text-xs text-slate-500">No events yet</p>
          ) : (
            progress.events.map((event, idx) => (
              <div
                key={idx}
                className="text-xs text-slate-300 border-l-2 border-slate-600 pl-2 py-1"
              >
                <div className="font-mono text-slate-400">
                  [{new Date(event.timestamp).toLocaleTimeString()}]
                </div>
                <div className="text-slate-300">
                  {event.type}: {event.product_name || event.message || ""}
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2 pt-2">
        <button
          onClick={() => handleSyncClick()}
          disabled={isLoading}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold py-2 px-4 rounded transition"
        >
          {isLoading ? "🔄 Syncing..." : "▶ Test Sync"}
        </button>
        <button
          onClick={() => setShowDetails(false)}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded transition text-sm font-semibold"
        >
          Clear
        </button>
      </div>

      {/* Info Text */}
      <p className="text-xs text-slate-500 text-center pt-2">
        {status === "completed"
          ? `✅ Synced ${progress.currentProduct}/${progress.totalProducts} products`
          : status === "syncing"
            ? `⏳ Syncing... ${progress.currentProduct}/${progress.totalProducts}`
            : `Ready to sync products to frontend`}
      </p>
    </div>
  );
};

export default SyncStatusDisplay;
