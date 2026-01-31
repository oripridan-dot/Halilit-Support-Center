import React, { useState } from "react";
import { ChevronDown, ChevronUp, Info } from "lucide-react";
import { Product } from "../types";
import ProductSpecs from "./ProductSpecs";
import ConfidenceBadge from "./ConfidenceBadge";
import ValidationPipeline from "./ValidationPipeline";

interface ProductDetailPanelProps {
  product: Product;
  className?: string;
}

/**
 * ProductDetailPanel Component
 * Complete product information display with:
 * - Technical specifications
 * - Confidence badges and sources of truth
 * - Real-world validation process visualization
 * - Commercial details
 * - Expert tips and pros/cons
 */
export const ProductDetailPanel: React.FC<ProductDetailPanelProps> = ({
  product,
  className = "",
}) => {
  const [expandedSections, setExpandedSections] = useState<
    Record<string, boolean>
  >({
    specs: true,
    confidence: true,
    pipeline: true,
    realworld: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const pillData = product.pill_data;
  if (!pillData) {
    return (
      <div className={`bg-slate-50 rounded-lg p-8 text-center ${className}`}>
        <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
        <p className="text-slate-500 text-sm">
          Limited data available for this product
        </p>
      </div>
    );
  }

  const specs = pillData.specs || {};
  const uiMeta = pillData.ui_meta || {};
  const contextMeta = pillData.context_meta || {};
  const commercialMeta = pillData.commercial_meta || {};
  const pipeline = pillData.validation_pipeline || {};

  const confidenceScore = uiMeta.y_axis_score || 0;
  const badges = uiMeta.badges || [];
  const sourcesOfTruth = contextMeta.sources_of_truth || [];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-slate-50 rounded-lg border border-blue-200 p-6">
        <h2 className="text-2xl font-bold text-slate-900 mb-2">
          {product.name}
        </h2>
        <p className="text-slate-600 mb-4">
          {product.description || "Fully verified product"}
        </p>

        {/* Quick Info */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              Brand
            </p>
            <p className="text-sm font-bold text-slate-900">{product.brand}</p>
          </div>
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              Category
            </p>
            <p className="text-sm font-bold text-slate-900">
              {product.category}
            </p>
          </div>
          {commercialMeta.price && (
            <div>
              <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
                Price
              </p>
              <p className="text-sm font-bold text-slate-900">
                ₪{commercialMeta.price.toLocaleString()}
              </p>
            </div>
          )}
          <div>
            <p className="text-xs text-slate-600 uppercase tracking-wider font-semibold">
              SKU
            </p>
            <p className="text-sm font-mono text-slate-700">
              {product.sku || "N/A"}
            </p>
          </div>
        </div>
      </div>

      {/* Confidence & Sources */}
      <div className="bg-white rounded-lg border border-slate-200">
        <button
          onClick={() => toggleSection("confidence")}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors border-b border-slate-200"
        >
          <h3 className="font-semibold text-slate-900">Verification & Trust</h3>
          {expandedSections.confidence ? (
            <ChevronUp className="w-5 h-5 text-slate-600" />
          ) : (
            <ChevronDown className="w-5 h-5 text-slate-600" />
          )}
        </button>
        {expandedSections.confidence && (
          <div className="p-6">
            <ConfidenceBadge
              score={confidenceScore}
              badges={badges}
              sourcesOfTruth={sourcesOfTruth}
              showDetailed={true}
            />
          </div>
        )}
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

      {/* Validation Pipeline */}
      {Object.keys(pipeline).length > 0 && (
        <div>
          <button
            onClick={() => toggleSection("pipeline")}
            className="w-full text-left mb-2"
          >
            <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200 hover:bg-slate-50 transition-colors">
              <h3 className="font-semibold text-slate-900">
                Validation Process
              </h3>
              {expandedSections.pipeline ? (
                <ChevronUp className="w-5 h-5 text-slate-600" />
              ) : (
                <ChevronDown className="w-5 h-5 text-slate-600" />
              )}
            </div>
          </button>
          {expandedSections.pipeline && (
            <ValidationPipeline pipeline={pipeline} score={confidenceScore} />
          )}
        </div>
      )}

      {/* Real-World Insights */}
      {(contextMeta.pros && contextMeta.pros.length > 0) ||
      (contextMeta.cons && contextMeta.cons.length > 0) ||
      (contextMeta.tips && contextMeta.tips.length > 0) ? (
        <div className="bg-white rounded-lg border border-slate-200">
          <button
            onClick={() => toggleSection("realworld")}
            className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors border-b border-slate-200"
          >
            <h3 className="font-semibold text-slate-900">
              Real-World Insights
            </h3>
            {expandedSections.realworld ? (
              <ChevronUp className="w-5 h-5 text-slate-600" />
            ) : (
              <ChevronDown className="w-5 h-5 text-slate-600" />
            )}
          </button>
          {expandedSections.realworld && (
            <div className="p-6 space-y-6">
              {/* Pros */}
              {contextMeta.pros && contextMeta.pros.length > 0 && (
                <div>
                  <h4 className="font-semibold text-green-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">✅</span> Strengths
                  </h4>
                  <ul className="space-y-2">
                    {contextMeta.pros.map((pro, idx) => (
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
              {contextMeta.cons && contextMeta.cons.length > 0 && (
                <div>
                  <h4 className="font-semibold text-amber-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">⚠️</span> Considerations
                  </h4>
                  <ul className="space-y-2">
                    {contextMeta.cons.map((con, idx) => (
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
              {contextMeta.tips && contextMeta.tips.length > 0 && (
                <div>
                  <h4 className="font-semibold text-blue-900 text-sm mb-3 flex items-center gap-2">
                    <span className="text-lg">💡</span> Expert Tips
                  </h4>
                  <ul className="space-y-2">
                    {contextMeta.tips.map((tip, idx) => (
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
          This product data has been verified through our complete 5-step
          refinery pipeline. Last verified:{" "}
          {new Date(
            pipeline.step5_published?.timestamp || Date.now(),
          ).toLocaleDateString()}
        </p>
      </div>
    </div>
  );
};

export default ProductDetailPanel;
