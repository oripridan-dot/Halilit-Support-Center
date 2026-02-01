import React, { useState } from "react";
import { ChevronDown, ChevronUp, Info } from "lucide-react";
import { Product } from "../types";
import ProductSpecs from "./ProductSpecs";

interface ProductDetailPanelProps {
  product: Product;
  className?: string;
}

/**
 * ProductDetailPanel Component
 * Complete product information display with:
 * - Technical specifications
 * - Pricing and availability
 * - Real-world insights (pros/cons/tips)
 * - Quality tier and scoring
 */
export const ProductDetailPanel: React.FC<ProductDetailPanelProps> = ({
  product,
  className = "",
}) => {
  const [expandedSections, setExpandedSections] = useState<
    Record<string, boolean>
  >({
    specs: true,
    insights: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Check if product has minimal required data
  if (!product || !product.name) {
    return (
      <div className={`bg-slate-50 rounded-lg p-8 text-center ${className}`}>
        <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <p className="text-slate-500 text-sm">
          Limited data available for this product
        </p>
      </div>
    );
  }

  const specs = product.specs || {};
  const pros = product.pros || [];
  const cons = product.cons || [];
  const tips = product.expert_tips || [];

  const tierColors: Record<string, string> = {
    diamond: "bg-blue-600",
    gold: "bg-amber-600",
    silver: "bg-slate-500",
    bronze: "bg-orange-700",
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-slate-50 rounded-lg border border-blue-200 p-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          {product.name}
        </h2>
        <p className="text-slate-600 mb-4">
          {product.description_full ||
            product.description_short ||
            "Product details"}
        </p>

        {/* Quality Tier Badge */}
        <div className="flex items-center gap-3 mb-4">
          <span
            className={`inline-block px-3 py-1 rounded-full text-xs font-semibold text-white ${
              tierColors[product.tier || "bronze"] || "bg-slate-400"
            }`}
          >
            {(product.tier || "unknown").toUpperCase()}
          </span>
          <span className="text-sm text-slate-600">
            Quality Score: {product.tier_score || 0}/100
          </span>
        </div>

        {/* Quick Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              Brand ID
            </p>
            <p className="text-sm font-bold text-slate-900">
              {product.brand_id || "N/A"}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              Category
            </p>
            <p className="text-sm font-bold text-slate-900">
              {product.category}
            </p>
          </div>
          {product.price && (
            <div>
              <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
                Price
              </p>
              <p className="text-sm font-bold text-slate-900">
                {product.currency} {product.price.toLocaleString()}
              </p>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              Stock Status
            </p>
            <p className="text-sm font-mono text-slate-700">
              {product.stock_status || "unknown"}
            </p>
          </div>
        </div>
      </div>

      {/* Specifications */}
      {Object.keys(specs).length > 0 && (
        <div>
          <button
            onClick={() => toggleSection("specs")}
            className="w-full text-left mb-2"
          >
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
              <h3 className="font-semibold text-slate-900">
                Technical Specifications
              </h3>
              {expandedSections.specs ? (
                <ChevronUp className="w-5 h-5 text-slate-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-600" />
              )}
            </div>
          </button>
          {expandedSections.specs && (
            <ProductSpecs specs={specs} category={product.category} />
          )}
        </div>
      )}

      {/* Real-World Insights */}
      {(pros && pros.length > 0) ||
      (cons && cons.length > 0) ||
      (tips && tips.length > 0) ? (
        <div className="bg-white rounded-lg border border-slate-200">
          <button
            onClick={() => toggleSection("insights")}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors border-b border-slate-200"
          >
            <h3 className="font-semibold text-slate-900">
              Real-World Insights
            </h3>
            {expandedSections.insights ? (
              <ChevronUp className="w-5 h-5 text-slate-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-slate-600" />
            )}
          </button>
          {expandedSections.insights && (
            <div className="p-6 space-y-6">
              {/* Pros */}
              {pros && pros.length > 0 && (
                <div>
                  <h4 className="font-semibold text-green-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">✅</span> Strengths
                  </h4>
                  <ul className="space-y-2">
                    {pros.map((pro, idx) => (
                      <li
                        key={idx}
                        className="text-sm text-slate-700 pl-6 border-l-2 border-green-300"
                      >
                        {pro}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Cons */}
              {cons && cons.length > 0 && (
                <div>
                  <h4 className="font-semibold text-amber-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">⚠️</span> Considerations
                  </h4>
                  <ul className="space-y-2">
                    {cons.map((con, idx) => (
                      <li
                        key={idx}
                        className="text-sm text-slate-700 pl-6 border-l-2 border-amber-300"
                      >
                        {con}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Expert Tips */}
              {tips && tips.length > 0 && (
                <div>
                  <h4 className="font-semibold text-blue-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">💡</span> Expert Tips
                  </h4>
                  <ul className="space-y-2">
                    {tips.map((tip, idx) => (
                      <li
                        key={idx}
                        className="text-sm text-slate-700 pl-6 border-l-2 border-blue-300"
                      >
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      ) : null}

      {/* Footer */}
      <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
        <p className="text-xs text-slate-500 text-center">
          Data synced at:{" "}
          {product.synced_at
            ? new Date(product.synced_at).toLocaleDateString()
            : "N/A"}
        </p>
      </div>
    </div>
  );
};

export default ProductDetailPanel;
