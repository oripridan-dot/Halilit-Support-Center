import React, { useState, useCallback } from "react";
import {
  useCopilotSkills,
  useProgressTracker,
} from "../hooks/useCopilotSkills";

/**
 * SkillsFrameworkDashboard
 *
 * Interactive dashboard for executing and monitoring Skills Framework.
 * Allows users to run individual skills or full pipelines with progress tracking.
 */
export function SkillsFrameworkDashboard() {
  const {
    executeSkill,
    executePipeline,
    getAvailableSkills,
    status,
    isLoading,
    error,
  } = useCopilotSkills();
  const {
    progress,
    totalPhases,
    currentPhase,
    percentComplete,
    trackProgress,
    reset,
  } = useProgressTracker();

  const [availableSkills, setAvailableSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState("pipeline");
  const [testProduct, setTestProduct] = useState({
    halilit_id: "test-001",
    product_name: "Test Product",
    brand: "TestBrand",
    price_il: 5000,
  });
  const [executionResult, setExecutionResult] = useState(null);
  const [pipelineLog, setPipelineLog] = useState([]);

  // Load available skills on mount
  React.useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = useCallback(async () => {
    const result = await getAvailableSkills();
    if (result.skills) {
      setAvailableSkills(result.skills);
    }
  }, [getAvailableSkills]);

  const handleExecuteSingleSkill = async () => {
    const context = {
      raw_product: testProduct,
      brand: testProduct.brand,
    };

    const result = await executeSkill(selectedSkill, context);
    setExecutionResult(result);
  };

  const handleExecutePipeline = async () => {
    reset();
    setPipelineLog([]);

    const result = await executePipeline(
      testProduct,
      testProduct.brand,
      (event) => {
        trackProgress(event);
        setPipelineLog((prev) => [...prev, event]);
      },
    );

    setExecutionResult(result);
  };

  const getPhaseColor = (phaseNum) => {
    if (phaseNum < progress) return "text-green-500"; // Completed
    if (phaseNum === progress && currentPhase) return "text-blue-500"; // In progress
    return "text-gray-400"; // Not started
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6 bg-slate-900 rounded-lg border border-slate-700">
      <h2 className="text-2xl font-bold text-white mb-6">
        🎯 Skills Framework Dashboard
      </h2>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-900/30 border border-red-700 rounded text-red-200">
          ❌ {error}
        </div>
      )}

      {/* Test Product Configuration */}
      <div className="bg-slate-800 rounded p-4 mb-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">
          📦 Test Product
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-300 mb-2">
              Product Name
            </label>
            <input
              type="text"
              value={testProduct.product_name}
              onChange={(e) =>
                setTestProduct({ ...testProduct, product_name: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600"
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-2">Brand</label>
            <input
              type="text"
              value={testProduct.brand}
              onChange={(e) =>
                setTestProduct({ ...testProduct, brand: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600"
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-2">
              Halilit ID
            </label>
            <input
              type="text"
              value={testProduct.halilit_id}
              onChange={(e) =>
                setTestProduct({ ...testProduct, halilit_id: e.target.value })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600"
              disabled={isLoading}
            />
          </div>
          <div>
            <label className="block text-sm text-slate-300 mb-2">
              Price (NIS)
            </label>
            <input
              type="number"
              value={testProduct.price_il}
              onChange={(e) =>
                setTestProduct({
                  ...testProduct,
                  price_il: parseFloat(e.target.value),
                })
              }
              className="w-full px-3 py-2 bg-slate-700 text-white rounded border border-slate-600"
              disabled={isLoading}
            />
          </div>
        </div>
      </div>

      {/* Skill Selection */}
      <div className="bg-slate-800 rounded p-4 mb-6 border border-slate-700">
        <h3 className="text-lg font-semibold text-white mb-4">
          ⚙️ Select Operation
        </h3>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <button
            onClick={() => setSelectedSkill("pipeline")}
            className={`px-4 py-2 rounded transition ${
              selectedSkill === "pipeline"
                ? "bg-blue-600 text-white"
                : "bg-slate-700 text-slate-300 hover:bg-slate-600"
            }`}
            disabled={isLoading}
          >
            🚀 Full Pipeline (6 Phases)
          </button>
          {availableSkills.map((skill) => (
            <button
              key={skill.name}
              onClick={() => setSelectedSkill(skill.name)}
              className={`px-4 py-2 rounded text-sm transition ${
                selectedSkill === skill.name
                  ? "bg-blue-600 text-white"
                  : "bg-slate-700 text-slate-300 hover:bg-slate-600"
              }`}
              disabled={isLoading}
            >
              {skill.phase ? `${skill.phase}. ${skill.name}` : skill.name}
            </button>
          ))}
        </div>
        <button
          onClick={
            selectedSkill === "pipeline"
              ? handleExecutePipeline
              : handleExecuteSingleSkill
          }
          disabled={isLoading}
          className={`w-full px-4 py-3 rounded font-semibold transition ${
            isLoading
              ? "bg-slate-600 text-slate-400 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          {isLoading ? "⏳ Executing..." : `Execute ${selectedSkill}`}
        </button>
      </div>

      {/* Progress Tracker (for pipeline) */}
      {selectedSkill === "pipeline" && (
        <div className="bg-slate-800 rounded p-4 mb-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">
            📊 Pipeline Progress
          </h3>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-slate-300 mb-2">
              <span>Progress: {currentPhase || "Ready"}</span>
              <span>{percentComplete}%</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-full transition-all duration-300"
                style={{ width: `${percentComplete}%` }}
              />
            </div>
          </div>

          {/* Phase Status */}
          <div className="grid grid-cols-6 gap-2">
            {Array.from({ length: totalPhases }, (_, i) => i + 1).map(
              (phaseNum) => (
                <div key={phaseNum} className="text-center">
                  <div className={`text-2xl ${getPhaseColor(phaseNum)}`}>
                    {phaseNum < progress
                      ? "✅"
                      : phaseNum === progress
                        ? "🔄"
                        : "⭕"}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Phase {phaseNum}
                  </div>
                </div>
              ),
            )}
          </div>
        </div>
      )}

      {/* Execution Log */}
      {pipelineLog.length > 0 && (
        <div className="bg-slate-800 rounded p-4 mb-6 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">
            📋 Execution Log
          </h3>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {pipelineLog.map((event, idx) => (
              <div key={idx} className="text-xs text-slate-300 font-mono">
                <span className="text-slate-500">[{event.type}]</span>{" "}
                {event.phase_name && (
                  <span className="text-blue-400">{event.phase_name}</span>
                )}
                {event.status && (
                  <span className="text-green-400">{event.status}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Execution Result */}
      {executionResult && (
        <div className="bg-slate-800 rounded p-4 border border-slate-700">
          <h3 className="text-lg font-semibold text-white mb-4">📤 Result</h3>
          <pre className="bg-slate-900 p-3 rounded text-xs text-slate-300 overflow-x-auto max-h-48 overflow-y-auto">
            {JSON.stringify(executionResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Status Indicator */}
      <div className="mt-6 text-center text-sm text-slate-400">
        Status:{" "}
        <span
          className={status === "idle" ? "text-green-400" : "text-yellow-400"}
        >
          {status}
        </span>
      </div>
    </div>
  );
}

export default SkillsFrameworkDashboard;
