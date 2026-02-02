import React, { useMemo } from "react";
import { Zap, Gauge, Box, Layers } from "lucide-react";
import { BaseComponentProps } from "../types/componentUtils";

interface ProductSpecsProps extends BaseComponentProps {
  specs?: Record<string, any> | Array<{ name: string; value: any }>;
  category?: string;
}

/**
 * ProductSpecs Component
 *
 * Displays technical specifications in a clean, organized grid
 * with smart categorization and icon hints
 *
 * Features:
 * - Automatic spec categorization (power, frequency, dimensions, etc.)
 * - Icon hints for spec types
 * - Responsive grid layout
 * - Formatted value display
 */
export const ProductSpecs: React.FC<ProductSpecsProps> = ({
  specs,
  category = "STUDIO_MONITORS",
  className = "",
}) => {
  // Memoize category definitions
  const categories = useMemo(
    () => ({
      power: ["power", "watts", "wattage", "power_total_watts"],
      frequency: [
        "frequency",
        "hz",
        "frequency_response_low_hz",
        "frequency_response_high_hz",
      ],
      dimensions: [
        "dimensions",
        "size",
        "height",
        "width",
        "depth",
        "weight",
        "kg",
        "lb",
      ],
      materials: ["material", "finish", "color", "cabinet"],
      drivers: ["woofer", "tweeter", "midrange", "driver", "diaphragm"],
      other: [],
    }),
    [],
  );

  // Get icon for spec key - memoized
  const getIcon = useMemo(
    () => (key: string) => {
      const lower = key.toLowerCase();
      if (categories.power.some((p) => lower.includes(p)))
        return <Zap className="w-4 h-4" />;
      if (categories.frequency.some((p) => lower.includes(p)))
        return <Gauge className="w-4 h-4" />;
      if (categories.dimensions.some((p) => lower.includes(p)))
        return <Box className="w-4 h-4" />;
      if (categories.drivers.some((p) => lower.includes(p)))
        return <Layers className="w-4 h-4" />;
      return null;
    },
    [categories],
  );

  // Format value display - pure function
  const formatValue = (value: any): string => {
    if (typeof value === "boolean") return value ? "Yes" : "No";
    if (typeof value === "object") return JSON.stringify(value);
    if (typeof value === "number" && value > 1000)
      return value.toLocaleString();
    return String(value);
  };

  // Format key display - pure function
  const formatKey = (key: string): string => {
    return key
      .replace(/_/g, " ")
      .replace(/([A-Z])/g, " $1")
      .trim()
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  };

  // Memoize entries processing
  const entries = useMemo<[string, any][]>(() => {
    if (
      !specs ||
      (Array.isArray(specs)
        ? specs.length === 0
        : Object.keys(specs).length === 0)
    ) {
      return [];
    }

    return Array.isArray(specs)
      ? specs.map((s): [string, any] => [s.name, s.value])
      : Object.entries(specs || {});
  }, [specs]);

  // Handle empty state
  if (entries.length === 0) {
    return (
      <div className={`bg-slate-50 rounded-lg p-6 text-center ${className}`}>
        <p className="text-slate-500 text-sm">No specifications available</p>
      </div>
    );
  }

  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 overflow-hidden ${className}`}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-3 border-b border-slate-200">
        <h3 className="font-semibold text-slate-900 text-sm uppercase tracking-wider">
          Technical Specifications
        </h3>
        <p className="text-slate-500 text-xs mt-1">
          {entries.length} specifications
        </p>
      </div>

      {/* Specs Grid */}
      <div className="divide-y divide-slate-200">
        {entries.map(([key, value], idx) => (
          <div
            key={idx}
            className="px-6 py-3 hover:bg-slate-50 transition-colors flex items-start justify-between gap-4"
          >
            <div className="flex items-start gap-2 flex-1 min-w-0">
              {getIcon(key) && (
                <div className="text-blue-600 mt-0.5 flex-shrink-0">
                  {getIcon(key)}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <dt className="font-medium text-slate-700 text-sm">
                  {formatKey(key)}
                </dt>
              </div>
            </div>
            <dd className="text-slate-900 font-semibold text-sm text-right flex-shrink-0">
              {formatValue(value)}
            </dd>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductSpecs;
