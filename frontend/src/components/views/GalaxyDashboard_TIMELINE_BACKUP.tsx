import React, { useEffect, useState } from "react";
import { CategorySlot } from "./galaxy/CategorySlot";
import { useNavigationStore } from "../../store/navigationStore";
import { 
  Guitar, 
  Drum, 
  Music, 
  Mic, 
  Volume2, 
  Radio 
} from "lucide-react";

interface CategoryData {
  id: string;
  name: string;
  subcategories?: string[];
  product_count?: number;
  icon?: React.ElementType;
  color?: string;
  image?: string;
}

// Define the main 6 categories (Galaxies/Tribes)
const MAIN_CATEGORIES: CategoryData[] = [
  {
    id: "guitars-bass",
    name: "Guitars & Bass",
    icon: Guitar,
    color: "#e11d48",
    image: "/assets/placeholders/guitars.jpg",
  },
  {
    id: "drums-percussion",
    name: "Drums & Percussion",
    icon: Drum,
    color: "#f59e0b",
    image: "/assets/placeholders/drums.jpg",
  },
  {
    id: "keys-production",
    name: "Keys & Production",
    icon: Music,
    color: "#8b5cf6",
    image: "/assets/placeholders/keys.jpg",
  },
  {
    id: "studio-recording",
    name: "Studio & Recording",
    icon: Mic,
    color: "#06b6d4",
    image: "/assets/placeholders/studio.jpg",
  },
  {
    id: "live-dj",
    name: "Live & DJ",
    icon: Radio,
    color: "#10b981",
    image: "/assets/placeholders/live.jpg",
  },
  {
    id: "accessories",
    name: "Accessories",
    icon: Volume2,
    color: "#6366f1",
    image: "/assets/placeholders/accessories.jpg",
  },
];

/**
 * GalaxyDashboard Component
 * 
 * The main landing view showing 6 category sectors (Galaxies/Tribes).
 * Each sector contains subcategory slots that navigate to SpectrumModule.
 * 
 * Layout: 2 rows × 3 columns grid
 */
export const GalaxyDashboard: React.FC = () => {
  const { goToSpectrum } = useNavigationStore();
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);

  // Load category counts from index.json
  useEffect(() => {
    const loadCounts = async () => {
      try {
        const response = await fetch("/data/search_index.json");
        if (!response.ok) throw new Error("Failed to load search index");
        
        const products = await response.json();
        
        // Count products by tribe_id/category
        const counts: Record<string, number> = {};
        products.forEach((product: any) => {
          const tribeId = product.tribe_id || product.category;
          if (tribeId) {
            counts[tribeId] = (counts[tribeId] || 0) + 1;
          }
        });
        
        setCategoryCounts(counts);
      } catch (error) {
        console.error("[GalaxyDashboard] Failed to load counts:", error);
      } finally {
        setLoading(false);
      }
    };

    loadCounts();
  }, []);

  const handleCategoryClick = (categoryId: string) => {
    // For now, navigate to spectrum with the category as both tribe and subcategory
    // This will be refined when we have actual subcategory data
    console.log(`[GalaxyDashboard] Navigating to ${categoryId}`);
    goToSpectrum(categoryId, categoryId, []);
  };

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-[#0a0a0a] text-zinc-500 font-mono">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-600 mx-auto mb-4" />
          <p>INITIALIZING GALAXY DASHBOARD...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full bg-[#0a0a0a] overflow-auto p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-white mb-2">
          Product Galaxy
        </h1>
        <p className="text-sm text-zinc-500 font-mono">
          Select a category to explore products
        </p>
      </div>

      {/* 2x3 Grid of Category Sectors */}
      <div className="grid grid-cols-3 gap-6 max-w-7xl mx-auto">
        {MAIN_CATEGORIES.map((category) => (
          <CategorySlot
            key={category.id}
            id={category.id}
            name={category.name}
            image={category.image || "/assets/placeholders/no-img.png"}
            fallbackGradient={`radial-gradient(circle at 50% 50%, ${category.color}40, transparent 70%)`}
            icon={category.icon}
            mainColor={category.color}
            count={categoryCounts[category.id] || 0}
            onClick={() => handleCategoryClick(category.id)}
          />
        ))}
      </div>

      {/* Stats Footer */}
      <div className="mt-12 text-center text-xs text-zinc-600 font-mono">
        <div className="flex items-center justify-center gap-8">
          <span>
            TOTAL CATEGORIES: {MAIN_CATEGORIES.length}
          </span>
          <span>
            TOTAL PRODUCTS:{" "}
            {Object.values(categoryCounts).reduce((a, b) => a + b, 0)}
          </span>
        </div>
      </div>
    </div>
  );
};
