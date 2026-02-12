import React from "react";
import { ArrowLeft, ChevronRight } from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";

/**
 * Breadcrumbs — shows the user's position in the navigation hierarchy.
 * Galaxy > Spectrum > Product
 */
export const Breadcrumbs: React.FC = () => {
  const { currentView, activeTribeId, activeSubcategoryId, goToGalaxy } =
    useNavigationStore();

  // Only show breadcrumbs when not on Galaxy
  if (currentView === "GALAXY") return null;

  const crumbs: Array<{ label: string; onClick?: () => void }> = [
    { label: "Galaxies", onClick: goToGalaxy },
  ];

  if (activeTribeId) {
    const galaxyLabel = activeTribeId.replace(/-/g, " ");
    if (currentView === "SPECTRUM") {
      crumbs.push({ label: galaxyLabel });
    } else {
      crumbs.push({ label: galaxyLabel, onClick: goToGalaxy });
    }
  }

  if (activeSubcategoryId && currentView !== "SPECTRUM") {
    const spectrumLabel = activeSubcategoryId.replace(/-/g, " ");
    crumbs.push({ label: spectrumLabel });
  }

  if (currentView === "PRODUCT_PAGE") {
    crumbs.push({ label: "Product Details" });
  }

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-xs">
      <button
        onClick={goToGalaxy}
        className="p-1 rounded hover:bg-zinc-800/50 text-zinc-500 hover:text-zinc-300 transition-colors"
        aria-label="Back"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
      </button>
      {crumbs.map((crumb, i) => (
        <React.Fragment key={i}>
          {i > 0 && <ChevronRight className="w-3 h-3 text-zinc-700" />}
          {crumb.onClick && i < crumbs.length - 1 ? (
            <button
              onClick={crumb.onClick}
              className="text-zinc-500 hover:text-zinc-300 transition-colors capitalize hover:underline underline-offset-2"
            >
              {crumb.label}
            </button>
          ) : (
            <span className="text-zinc-300 font-medium capitalize">
              {crumb.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};
