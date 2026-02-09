// frontend/src/components/LearningFeed.tsx
import React from "react";
import { useProductStore } from "../store/productStore";

export const LearningFeed = () => {
  const insights = useProductStore((state) => state.learningInsights);

  if (insights.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-slate-900/95 backdrop-blur-md border border-blue-500/30 rounded-lg shadow-2xl p-4 z-50 transition-all duration-300 transform translate-y-0">
      <h3 className="text-blue-400 text-xs font-bold uppercase mb-3 flex items-center gap-2 border-b border-blue-500/20 pb-2">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
        </span>
        Live Learning Engine
      </h3>
      <div className="space-y-3 max-h-60 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-blue-500/20 scrollbar-track-transparent">
        {insights.map((item, i) => (
          <div
            key={i}
            className="text-xs group animate-in fade-in slide-in-from-right-8 duration-500"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="flex justify-between items-start mb-1 text-xs text-zinc-600 font-mono">
              <span>{item.timestamp}</span>
              <span className="text-blue-400/80">{item.brand}</span>
            </div>
            <p className="text-zinc-300 italic border-l-2 border-blue-500/30 pl-2 leading-relaxed">
              "{item.insight}"
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
