import { motion } from "framer-motion";
import {
  LayoutGrid,
} from "lucide-react";
import { useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";
import { CategorySlot, type SlotScene } from "./galaxy/CategorySlot";

// --- ADAPTATION LAYER: Map Universal Categories to "Galaxy" shape ---
const galaxy = UNIVERSAL_CATEGORIES.map(cat => ({
  id: cat.id,
  name: cat.label,
  icon: cat.iconName,
  color: cat.color,
  children: cat.spectrum.map(sub => ({
    id: sub.id,
    name: sub.label,
    image: sub.image // Use the correct image path mapped in UNIVERSAL_CATEGORIES
  }))
}));

// SCENE REGISTRY: Defines the physical environment and lighting physics for each miniature world.
// All slots have uniform base structure - differences only in brand colors
// KEYS MUST MATCH: ${galaxy_id}-${spectrum_id}
const SLOT_SCENES: Record<string, SlotScene> = {
  // --- 🎹 KEYS SECTOR (keys-production) ---
  "keys-production-synthesizers": {
    themeColors: ["#ff8c00", "#00d2d3"],
    sceneType: "STUDIO",
    vibe: "ANALOG_LAB_SYNTHESIS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "keys-production-stage-pianos": {
    themeColors: ["#d90429", "#ffffff"],
    sceneType: "STAGE",
    vibe: "GRAND_CONCERT_HALL",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "keys-production-midi-controllers": {
    themeColors: ["#ffffff", "#2ecc71"],
    sceneType: "STUDIO",
    vibe: "DATA_CONTROL_INTERFACE",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "keys-production-grooveboxes": {
    themeColors: ["#0984e3", "#2f3640"],
    sceneType: "BOOTH",
    vibe: "PRODUCTION_COCKPIT",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "keys-production-eurorack": {
    themeColors: ["#e1b12c", "#a4b0be"], 
    sceneType: "WALL",
    vibe: "MODULAR_PATCH_BAY",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "keys-production-keys-accessories": {
    themeColors: ["#7f8c8d", "#666666"],
    sceneType: "VOID",
    vibe: "STANDS_AND_PEDALS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // --- 🎸 GUITARS SECTOR (guitars-bass) ---
  "guitars-bass-electric-guitars": {
    themeColors: ["#2ed573", "#ff6348"],
    sceneType: "WALL",
    vibe: "CUSTOM_SHOP_DISPLAY",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "guitars-bass-guitar-amps": {
    themeColors: ["#e1b12c", "#555555"],
    sceneType: "WALL",
    vibe: "THE_AMP_VAULT",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "guitars-bass-guitar-pedals": {
    themeColors: ["#3742fa", "#ff00ff"],
    sceneType: "WALL",
    vibe: "PEDALBOARD_MATRIX",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "guitars-bass-acoustic-guitars": {
    themeColors: ["#e67e22", "#f5f6fa"],
    sceneType: "STAGE",
    vibe: "ROYAL_CONCERT_HALL",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "guitars-bass-bass-guitars": {
    themeColors: ["#1e3a8a", "#7c3aed"],
    sceneType: "STUDIO",
    vibe: "LOW_END_CHAMBER",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "guitars-bass-folk-instruments": {
    themeColors: ["#d35400", "#f39c12"], 
    sceneType: "BOOTH",
    vibe: "TRADITIONAL_CORNER",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
   "guitars-bass-guitar-accessories": {
    themeColors: ["#95a5a6", "#666666"], 
    sceneType: "VOID",
    vibe: "STRINGS_ADAPTERS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // --- 🥁 DRUMS SECTOR (drums-percussion) ---
  "drums-percussion-electronic-drums": {
    themeColors: ["#e67e22", "#2d3436"],
    sceneType: "STUDIO",
    vibe: "INDUSTRIAL_RHYTHM_CAGE",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-acoustic-drums": {
    themeColors: ["#e1b12c", "#dcdde1"],
    sceneType: "STUDIO",
    vibe: "WOOD_AND_CHROME_SESSION",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-percussion": {
    themeColors: ["#d4af37", "#8b4513"],
    sceneType: "STAGE",
    vibe: "WORLD_PERCUSSION_STAGE",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-cymbals": {
    themeColors: ["#f1c40f", "#bdc3c7"],
    sceneType: "WALL",
    vibe: "CYMBAL_VAULT",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-snares": {
    themeColors: ["#ecf0f1", "#95a5a6"],
    sceneType: "BOOTH",
    vibe: "SNARE_WORKSHOP",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-sticks-heads": {
    themeColors: ["#e67e22", "#ecf0f1"],
    sceneType: "VOID",
    vibe: "STICK_ROOM",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "drums-percussion-drum-hardware": {
    themeColors: ["#bdc3c7", "#7f8c8d"],
    sceneType: "VOID",
    vibe: "HARDWARE_SECTOR",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // --- 🎙️ STUDIO SECTOR (studio-recording) ---
  "studio-recording-audio-interfaces": {
    themeColors: ["#ffa502", "#ffffff"],
    sceneType: "STUDIO",
    vibe: "BEDROOM_PRODUCER_SETUP",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "studio-recording-studio-monitors": {
    themeColors: ["#f9ca24", "#1e272e"],
    sceneType: "STUDIO",
    vibe: "ACOUSTICALLY_TREATED_CORNER",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "studio-recording-outboard-gear": {
    themeColors: ["#ff4757", "#2f3542"],
    sceneType: "STUDIO",
    vibe: "MASTER_CONTROL_A",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "studio-recording-studio-microphones": {
    themeColors: ["#c0c0c0", "#ffd700"],
    sceneType: "STUDIO",
    vibe: "VOCAL_BOOTH_SILENCE",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
   "studio-recording-software-plugins": {
    themeColors: ["#8e44ad", "#2980b9"], 
    sceneType: "VOID",
    vibe: "DIGITAL_REALM",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "studio-recording-studio-accessories": {
    themeColors: ["#7f8c8d", "#666666"],
    sceneType: "VOID",
    vibe: "CABLING_ISOLATION",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // --- 🔊 LIVE SOUND SECTOR (live-dj) ---
  "live-dj-pa-systems": {
    themeColors: ["#00a8ff", "#2f3640"],
    sceneType: "STAGE",
    vibe: "MAIN_STAGE_ARENA",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "live-dj-live-mixers": {
    themeColors: ["#3498db", "#2c3e50"],
    sceneType: "BOOTH",
    vibe: "FOH_COMMAND_CENTER",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "live-dj-dj-equipment": {
    themeColors: ["#0984e3", "#ff3f34"],
    sceneType: "BOOTH",
    vibe: "UNDERGROUND_CLUB_BOOTH",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "live-dj-lighting": {
    themeColors: ["#e056fd", "#f1c40f"], 
    sceneType: "STAGE",
    vibe: "LIGHT_RIG",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "live-dj-live-mics": {
    themeColors: ["#95a5a6", "#34495e"], 
    sceneType: "STAGE",
    vibe: "WIRELESS_SYSTEMS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
   "live-dj-live-accessories": {
    themeColors: ["#7f8c8d", "#666666"], 
    sceneType: "VOID",
    vibe: "STAGE_ESSENTIALS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // --- 🔧 UTILITY SECTOR (accessories-utility) ---
  "accessories-utility-cables": {
    themeColors: ["#e74c3c", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "CONNECTIVITY",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
 "accessories-utility-stands": {
    themeColors: ["#95a5a6", "#34495e"], 
    sceneType: "VOID",
    vibe: "SUPPORT_SYSTEMS",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
  "accessories-utility-cases-bags": {
    themeColors: ["#34495e", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "PROTECTION",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },
   "accessories-utility-power-supplies": {
    themeColors: ["#f1c40f", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "POWER_GRID",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  },

  // FALLBACK
  "default": { 
    themeColors: ["#a4b0be", "#666666"], 
    sceneType: "VOID", 
    vibe: "ARCHIVED_ASSET",
    floorMat: "radial-gradient(ellipse at bottom, transparent 0%, transparent 70%)",
    bgMat: "linear-gradient(180deg, #0a0a0a 0%, #000000 100%)"
  }
};

export const GalaxyDashboard = () => {
  const { goToSpectrum } = useNavigationStore();

  // Directly handle navigation to a subcategory
  const onSlotClick = (mainId: string, subId: string) => {
    goToSpectrum(mainId, subId, []);
  };

  return (
    <div className="flex h-full bg-[#050505] text-white overflow-hidden relative flex-col">
      
      {/* ------------------------------------------------------------------
          HEADER: ULTRA COMPACT
         ------------------------------------------------------------------ */}
      <header className="h-14 flex items-center px-6 bg-gradient-to-b from-transparent to-black/20 z-10 border-b border-zinc-900/50 shrink-0">
        <div className="flex items-center gap-3">
           <LayoutGrid className="w-6 h-6 text-zinc-500" />
           <h1 className="text-zinc-100 font-bold tracking-tight text-3xl">GALAXIES</h1>
        </div>
      </header>

      {/* ------------------------------------------------------------------
          MAIN CONTENT: 6 SECTOR CARDS GRID (FIXED SCREEN)
         ------------------------------------------------------------------ */}
      <div className="flex-1 p-6 min-h-0 w-full h-full text-[10px]">
        {/* Force 2 rows, 3 columns, fitting height */}
        <div className="grid grid-cols-3 grid-rows-2 gap-6 h-full w-full max-w-[1920px] mx-auto">
          
          {galaxy.map((sector) => (
            <div 
                key={sector.id} 
                className="bg-[#0a0a0a] rounded-xl border border-zinc-800/60 overflow-hidden flex flex-col shadow-2xl min-h-0"
            >
              {/* Sector Header */}
              <div className="px-4 py-3 border-b border-zinc-800/60 bg-[#0f0f0f] flex items-center gap-3 shrink-0 h-12">
                <div 
                    className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold shadow-lg shrink-0"
                     style={{ backgroundColor: sector.color, color: '#fff' }}
                >
                    {/* Icon placeholder */}
                    <span>
                      {sector.icon === "Guitar" ? '🎸' : 
                       sector.icon === "Music" ? '🥁' :
                       sector.icon === "Piano" ? '🎹' : 
                       sector.icon === "Mic2" ? '🎙️' :
                       sector.icon === "Speaker" ? '🔊' : '🔌'}
                    </span>
                </div>
                <h2 className="font-bold uppercase tracking-tight text-zinc-100 text-sm truncate">{sector.name}</h2>
              </div>

              {/* Tiny Slots Grid - Autosizing to fit */}
              <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start overflow-hidden">
                {sector.children.map((sub) => {
                    const fullId = `${sector.id}-${sub.id}`;
                    // Use the newly corrected keys in SLOT_SCENES
                    const scene = SLOT_SCENES[fullId] || SLOT_SCENES["default"];
                    
                    return (
                        <CategorySlot
                            key={sub.id}
                            id={sub.id}
                            name={sub.name}
                            image={sub.image}
                            scene={scene}
                            onClick={() => onSlotClick(sector.id, sub.id)}
                        />
                    );
                })}
              </div>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
};
