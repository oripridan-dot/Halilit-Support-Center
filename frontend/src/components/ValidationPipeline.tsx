import React, { useMemo } from "react";
import {
  CheckCircle2,
  Circle,
  AlertCircle,
  ArrowRight,
  Zap,
  ShoppingCart,
  Users,
  CheckSquare,
  Package,
} from "lucide-react";
import { BaseComponentProps } from "../types/componentUtils";

interface ValidationStep {
  status: "complete" | "partial" | "pending" | "failed";
  timestamp?: string;
  data_quality?: number;
  issues?: string[];
  sources_used?: string[];
}

interface ValidationPipelineProps extends BaseComponentProps {
  pipeline?: Record<string, ValidationStep>;
  score?: number;
}

interface StepDefinition {
  key: string;
  number: number;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  color: string;
}

/**
 * ValidationPipeline Component
 *
 * Visualizes the 5-step refinery process:
 * Official → Commercial → Context → Validation → Published
 *
 * Features:
 * - Step status visualization
 * - Trust score display
 * - Data quality indicators
 * - Source attribution
 */
export const ValidationPipeline: React.FC<ValidationPipelineProps> = ({
  pipeline,
  score = 0,
  className = "",
}) => {
  // Memoize step definitions
  const steps = useMemo<StepDefinition[]>(
    () => [
      {
        key: "step1_official",
        number: 1,
        title: "Official Data",
        subtitle: "Manufacturer specs & media",
        icon: <Zap className="w-5 h-5" />,
        color: "bg-blue-100 text-blue-700 border-blue-300",
      },
      {
        key: "step2_commercial",
        number: 2,
        title: "Commercial",
        subtitle: "Pricing & availability",
        icon: <ShoppingCart className="w-5 h-5" />,
        color: "bg-purple-100 text-purple-700 border-purple-300",
      },
      {
        key: "step3_context",
        number: 3,
        title: "Context",
        subtitle: "Real-world feedback",
        icon: <Users className="w-5 h-5" />,
        color: "bg-green-100 text-green-700 border-green-300",
      },
      {
        key: "step4_cross_validation",
        number: 4,
        title: "Validation",
        subtitle: "Cross-check & scoring",
        icon: <CheckSquare className="w-5 h-5" />,
        color: "bg-amber-100 text-amber-700 border-amber-300",
      },
      {
        key: "step5_published",
        number: 5,
        title: "Published",
        subtitle: "Ready for display",
        icon: <Package className="w-5 h-5" />,
        color: "bg-emerald-100 text-emerald-700 border-emerald-300",
      },
    ],
    [],
  );

  const getStepStatus = (key: string) => {
    if (!pipeline) return "pending";
    const step = pipeline[key];
    return step?.status || "pending";
  };

  const getStatusIcon = (status: string, color: string) => {
    switch (status) {
      case "complete":
        return <CheckCircle2 className={`w-6 h-6 ${color}`} />;
      case "partial":
        return <AlertCircle className={`w-6 h-6 ${color}`} />;
      case "failed":
        return <AlertCircle className="w-6 h-6 text-red-600" />;
      default:
        return <Circle className="w-6 h-6 text-slate-400" />;
    }
  };

  // Handle empty state
  if (!pipeline || Object.keys(pipeline).length === 0) {
    return (
      <div className={`bg-slate-50 rounded-lg p-8 text-center ${className}`}>
        <p className="text-slate-500 text-sm">No pipeline data available</p>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b border-slate-200">
        <h3 className="font-semibold text-slate-900 text-sm uppercase tracking-wider">
          Real-World Validation Process
        </h3>
        <p className="text-slate-500 text-xs mt-1">
          This product has been verified through our 5-step refinery pipeline
        </p>
      </div>

      {/* Score Summary */}
      {score > 0 && (
        <div className="bg-blue-50 border-b border-blue-200 px-6 py-3 flex items-center justify-between">
          <span className="text-sm font-medium text-blue-900">Trust Score</span>
          <div className="flex items-center gap-2">
            <div className="w-24 h-2 bg-blue-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full"
                style={{ width: `${score}%` }}
              />
            </div>
            <span className="font-bold text-blue-900 w-12 text-right">
              {score}%
            </span>
          </div>
        </div>
      )}

      {/* Pipeline Steps */}
      <div className="p-6">
        <div className="flex flex-col">
          {steps.map((step, idx) => {
            const status = getStepStatus(step.key);
            const stepData = pipeline ? pipeline[step.key] : null;

            return (
              <div key={step.key}>
                {/* Step */}
                <div className="flex items-start gap-4">
                  {/* Status Icon */}
                  <div className="flex-shrink-0 relative pt-0.5">
                    <div
                      className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${
                        status === "complete"
                          ? "bg-green-50 border-green-300"
                          : status === "partial"
                            ? "bg-amber-50 border-amber-300"
                            : status === "failed"
                              ? "bg-red-50 border-red-300"
                              : "bg-slate-50 border-slate-300"
                      }`}
                    >
                      {getStatusIcon(
                        status,
                        status === "complete"
                          ? "text-green-600"
                          : status === "partial"
                            ? "text-amber-600"
                            : status === "failed"
                              ? "text-red-600"
                              : "text-slate-400",
                      )}
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0 pb-6">
                    <div className="flex items-baseline gap-2 mb-1">
                      <h4 className="font-semibold text-slate-900 text-sm">
                        {step.title}
                      </h4>
                      <span
                        className={`inline-block px-2 py-1 rounded text-xs font-semibold uppercase tracking-wider ${
                          status === "complete"
                            ? "bg-green-100 text-green-700"
                            : status === "partial"
                              ? "bg-amber-100 text-amber-700"
                              : status === "failed"
                                ? "bg-red-100 text-red-700"
                                : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {status}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 mb-3">
                      {step.subtitle}
                    </p>

                    {/* Step Details */}
                    {stepData && (
                      <div className="space-y-2">
                        {stepData.data_quality !== undefined && (
                          <div className="flex items-center gap-2 text-xs">
                            <span className="text-slate-600">
                              Data Quality:
                            </span>
                            <div className="w-16 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                              <div
                                className={`h-full rounded-full ${
                                  stepData.data_quality >= 80
                                    ? "bg-green-600"
                                    : stepData.data_quality >= 60
                                      ? "bg-amber-600"
                                      : "bg-red-600"
                                }`}
                                style={{ width: `${stepData.data_quality}%` }}
                              />
                            </div>
                            <span className="font-semibold text-slate-900">
                              {stepData.data_quality}%
                            </span>
                          </div>
                        )}

                        {stepData.sources_used &&
                          stepData.sources_used.length > 0 && (
                            <div className="text-xs">
                              <span className="text-slate-600">Sources: </span>
                              <span className="text-slate-900 font-medium">
                                {stepData.sources_used.join(", ")}
                              </span>
                            </div>
                          )}

                        {stepData.issues && stepData.issues.length > 0 && (
                          <div className="text-xs space-y-1">
                            {stepData.issues.map((issue, i) => (
                              <div
                                key={i}
                                className="flex gap-2 text-amber-700"
                              >
                                <span>⚠️</span>
                                <span>{issue}</span>
                              </div>
                            ))}
                          </div>
                        )}

                        {stepData.timestamp && (
                          <p className="text-xs text-slate-500">
                            {new Date(stepData.timestamp).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Arrow (if not last step) */}
                {idx < steps.length - 1 && (
                  <div className="flex justify-center -mb-3 relative z-0">
                    <ArrowRight className="w-5 h-5 text-slate-300 rotate-90" />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="bg-slate-50 border-t border-slate-200 px-6 py-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex items-center gap-2 text-xs">
          <CheckCircle2 className="w-4 h-4 text-green-600" />
          <span className="text-slate-600">Complete</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <AlertCircle className="w-4 h-4 text-amber-600" />
          <span className="text-slate-600">Partial</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <AlertCircle className="w-4 h-4 text-red-600" />
          <span className="text-slate-600">Failed</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <Circle className="w-4 h-4 text-slate-400" />
          <span className="text-slate-600">Pending</span>
        </div>
      </div>
    </div>
  );
};

export default ValidationPipeline;
