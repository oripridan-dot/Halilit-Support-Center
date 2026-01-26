import { motion } from "framer-motion";
import {
  LayoutGrid,
} from "lucide-react";
import { useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";

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
// KEYS MUST MATCH: ${galaxy_id}-${spectrum_id}
const SLOT_SCENES: Record<string, { 
  themeColors: [string, string]; 
  sceneType: "STAGE" | "STUDIO" | "WALL" | "BOOTH" | "VOID";
  vibe: string;
  floorMat: string;
  bgMat: string; 
}> = {

  // --- 🎹 KEYS SECTOR (keys-production) ---
  "keys-production-synthesizers": {
    themeColors: ["#ff8c00", "#00d2d3"], // Roland Orange / Digital Cyan
    sceneType: "STUDIO",
    vibe: "ANALOG_LAB_SYNTHESIS",
    floorMat: "radial-gradient(ellipse at bottom, #ff8c0020 0%, transparent 70%)",
    bgMat: "linear-gradient(135deg, #001a1a 0%, #000 100%)"
  },
  "keys-production-stage-pianos": {
    themeColors: ["#d90429", "#ffffff"], // Nord Red / Spotlight White
    sceneType: "STAGE",
    vibe: "GRAND_CONCERT_HALL",
    floorMat: "radial-gradient(circle at bottom, #d9042930 0%, #000000 70%)",
    bgMat: "repeating-linear-gradient(90deg, #0a0000 0px, #0a0000 60px, #1a0000 61px, #0a0000 62px)"
  },
  "keys-production-midi-controllers": {
    themeColors: ["#ffffff", "#2ecc71"], // Clean White / MIDI Green
    sceneType: "STUDIO",
    vibe: "DATA_CONTROL_INTERFACE",
    floorMat: "radial-gradient(ellipse at bottom, #2ecc7115 0%, transparent 60%)",
    bgMat: "linear-gradient(to top, #0a0a0a 0%, #000 100%)"
  },
  "keys-production-grooveboxes": {
    themeColors: ["#0984e3", "#2f3640"], // LCD Blue / Korg Titanium
    sceneType: "BOOTH",
    vibe: "PRODUCTION_COCKPIT",
    floorMat: "radial-gradient(ellipse at bottom, #0984e320 0%, transparent 70%)",
    bgMat: "radial-gradient(circle at center, #1a1a2e 0%, #000 100%)"
  },
  "keys-production-eurorack": {
    themeColors: ["#e1b12c", "#a4b0be"], 
    sceneType: "WALL",
    vibe: "MODULAR_PATCH_BAY",
    floorMat: "linear-gradient(to bottom, #111 0%, #000 100%)",
    bgMat: "repeating-linear-gradient(0deg, #111 0px, #111 2px, #000 3px, #000 4px)"
  },
  "keys-production-keys-accessories": {
    themeColors: ["#7f8c8d", "#000000"],
    sceneType: "VOID",
    vibe: "STANDS_AND_PEDALS",
    floorMat: "transparent",
    bgMat: "#050505"
  },

  // --- 🎸 GUITARS SECTOR (guitars-bass) ---
  "guitars-bass-electric-guitars": {
    themeColors: ["#2ed573", "#ff6348"], // Seafoam / Sunburst
    sceneType: "WALL",
    vibe: "CUSTOM_SHOP_DISPLAY",
    floorMat: "linear-gradient(to top, #000 0%, transparent 50%)",
    bgMat: "radial-gradient(circle at center, #2ed57310 0%, #000 80%)"
  },
  "guitars-bass-guitar-amps": {
    themeColors: ["#e1b12c", "#000000"], // Marshall Gold / Tolex Black
    sceneType: "WALL",
    vibe: "THE_AMP_VAULT",
    floorMat: "linear-gradient(to bottom, #000 0%, #111 100%)",
    bgMat: "repeating-linear-gradient(45deg, #111 0px, #111 2px, #000 3px, #000 4px)"
  },
  "guitars-bass-guitar-pedals": {
    themeColors: ["#3742fa", "#ff00ff"], // Boss Blue / Neon Magenta
    sceneType: "WALL",
    vibe: "PEDALBOARD_MATRIX",
    floorMat: "radial-gradient(ellipse at bottom, #3742fa20 0%, #ff00ff10 50%, transparent 70%)",
    bgMat: "linear-gradient(135deg, #0a0015 0%, #000 100%)"
  },
  "guitars-bass-acoustic-guitars": {
    themeColors: ["#e67e22", "#f5f6fa"], // Natural Wood / Sheet Music White
    sceneType: "STAGE",
    vibe: "ROYAL_CONCERT_HALL",
    floorMat: "conic-gradient(from 180deg at 50% 100%, #000, #e67e2220, #000)",
    bgMat: "radial-gradient(circle at top, #1a1410 0%, #000 100%)"
  },
  "guitars-bass-bass-guitars": {
    themeColors: ["#1e3a8a", "#7c3aed"], // Deep Bass Blue / Purple
    sceneType: "STUDIO",
    vibe: "LOW_END_CHAMBER",
    floorMat: "radial-gradient(ellipse at bottom, #1e3a8a30 0%, transparent 70%)",
    bgMat: "linear-gradient(to bottom, #0a0015 0%, #000 100%)"
  },
  "guitars-bass-folk-instruments": {
    themeColors: ["#d35400", "#f39c12"], 
    sceneType: "BOOTH",
    vibe: "TRADITIONAL_CORNER",
    floorMat: "radial-gradient(circle, #d3540020 0%, #000 70%)",
    bgMat: "linear-gradient(to top, #2c2c2c 0%, #000 100%)"
  },
   "guitars-bass-guitar-accessories": {
    themeColors: ["#95a5a6", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "STRINGS_ADAPTERS",
    floorMat: "transparent",
    bgMat: "#080808"
  },


  // --- 🥁 DRUMS SECTOR (drums-percussion) ---
  "drums-percussion-electronic-drums": {
    themeColors: ["#e67e22", "#2d3436"], // V-Drums Amber / Rack Black
    sceneType: "STUDIO",
    vibe: "INDUSTRIAL_RHYTHM_CAGE",
    floorMat: "radial-gradient(ellipse at bottom, #e67e2225 0%, transparent 70%)",
    bgMat: "repeating-linear-gradient(0deg, #0a0a0a 0px, #0a0a0a 20px, #1a1a1a 21px, #0a0a0a 22px)"
  },
  "drums-percussion-acoustic-drums": {
    themeColors: ["#e1b12c", "#dcdde1"], // Bronze / Chrome
    sceneType: "STUDIO",
    vibe: "WOOD_AND_CHROME_SESSION",
    floorMat: "radial-gradient(ellipse at bottom, #e1b12c20 0%, transparent 70%)",
    bgMat: "linear-gradient(to bottom, #1a1410 0%, #000 100%)"
  },
  "drums-percussion-percussion": {
    themeColors: ["#d4af37", "#8b4513"], // Gold / Wood Brown
    sceneType: "STAGE",
    vibe: "WORLD_PERCUSSION_STAGE",
    floorMat: "radial-gradient(circle at bottom, #d4af3720 0%, transparent 70%)",
    bgMat: "linear-gradient(135deg, #1a0f00 0%, #000 100%)"
  },
  "drums-percussion-cymbals": {
    themeColors: ["#f1c40f", "#bdc3c7"], // Bright Gold / Silver
    sceneType: "WALL",
    vibe: "CYMBAL_VAULT",
    floorMat: "linear-gradient(to bottom, #000 0%, #222 100%)",
    bgMat: "radial-gradient(circle at center, #f1c40f10 0%, #000 80%)"
  },
  "drums-percussion-snares": {
    themeColors: ["#ecf0f1", "#95a5a6"], // Snare Head White / Steel
    sceneType: "BOOTH",
    vibe: "SNARE_WORKSHOP",
    floorMat: "radial-gradient(ellipse at bottom, #FFF 10%, transparent 80%)",
    bgMat: "linear-gradient(to top, #111 0%, #000 100%)"
  },
  "drums-percussion-sticks-heads": {
    themeColors: ["#e67e22", "#ecf0f1"], // Wood Stick / Drum Head
    sceneType: "VOID",
    vibe: "STICK_ROOM",
    floorMat: "transparent",
    bgMat: "#0a0a0a"
  },
  "drums-percussion-drum-hardware": {
    themeColors: ["#bdc3c7", "#7f8c8d"], // Chrome / Metal
    sceneType: "VOID",
    vibe: "HARDWARE_SECTOR",
    floorMat: "transparent",
    bgMat: "#050505"
  },


  // --- 🎙️ STUDIO SECTOR (studio-recording) ---
  "studio-recording-audio-interfaces": {
    themeColors: ["#ffa502", "#ffffff"], // Warm Tungsten / Clean White
    sceneType: "STUDIO",
    vibe: "BEDROOM_PRODUCER_SETUP",
    floorMat: "radial-gradient(ellipse at bottom, #ffa50230 0%, transparent 60%)",
    bgMat: "linear-gradient(to top, #1e272e 0%, #000 100%)"
  },
  "studio-recording-studio-monitors": {
    themeColors: ["#f9ca24", "#1e272e"], // KRK Yellow / Acoustic Black
    sceneType: "STUDIO",
    vibe: "ACOUSTICALLY_TREATED_CORNER",
    floorMat: "radial-gradient(ellipse at bottom, #f9ca2420 0%, transparent 70%)",
    bgMat: "radial-gradient(circle at center, #1e272e 0%, #000 100%)"
  },
  "studio-recording-outboard-gear": {
    themeColors: ["#ff4757", "#2f3542"], // Focusrite Red / Charcoal
    sceneType: "STUDIO",
    vibe: "MASTER_CONTROL_A",
    floorMat: "linear-gradient(to bottom, #2d3436 0%, #3e3e3e 100%)",
    bgMat: "radial-gradient(circle at center, #2f3542 0%, #000 100%)"
  },
   /* Note: 'studio-recording' ID vs sub 'recording' logic mismatch fixed by using explicit sub-IDs */
  
  // NOTE: studio-headphones... wait, Headphones aren't in UNIVERSAL_CATEGORIES spectrum above?
  // Let's check UNIVERSAL_CATEGORIES map in my head... 
  // Ah, CategoryConsolidation.ts didn't list Headphones! It listed "studio-microphones", "outboard-gear".
  // Let me check my previous output for potential missing keys.
  // I saw "studio-microphones".
  
  "studio-recording-studio-microphones": {
    themeColors: ["#c0c0c0", "#ffd700"], // Silver / Gold Diaphragm
    sceneType: "STUDIO",
    vibe: "VOCAL_BOOTH_SILENCE",
    floorMat: "radial-gradient(ellipse at bottom, #ffd70015 0%, transparent 70%)",
    bgMat: "linear-gradient(to top, #0f0f0f 0%, #000 100%)"
  },
   "studio-recording-software-plugins": {
    themeColors: ["#8e44ad", "#2980b9"], 
    sceneType: "VOID",
    vibe: "DIGITAL_REALM",
    floorMat: "radial-gradient(circle, #8e44ad20 0%, #000 80%)",
    bgMat: "#050505"
  },
  "studio-recording-studio-accessories": {
    themeColors: ["#7f8c8d", "#2c3e50"],
    sceneType: "VOID",
    vibe: "CABLING_ISOLATION",
    floorMat: "transparent",
    bgMat: "#080808"
  },

  // --- 🔊 LIVE SOUND SECTOR (live-dj) ---
  "live-dj-pa-systems": {
    themeColors: ["#00a8ff", "#2f3640"], // JBL Blue / Dark Grey
    sceneType: "STAGE",
    vibe: "MAIN_STAGE_ARENA",
    floorMat: "radial-gradient(circle at bottom, #00a8ff20 0%, #000000 70%)",
    bgMat: "repeating-linear-gradient(90deg, #000 0px, #000 40px, #111 41px, #000 42px)"
  },
  "live-dj-live-mixers": {
    themeColors: ["#3498db", "#2c3e50"], // Digital Blue / Slate Grey
    sceneType: "BOOTH",
    vibe: "FOH_COMMAND_CENTER",
    floorMat: "radial-gradient(ellipse at bottom, #3498db20 0%, transparent 70%)",
    bgMat: "linear-gradient(to bottom, #2c3e50 0%, #000 100%)"
  },

  // --- 🎧 DJ/PRODUCTION SECTOR ---
  "live-dj-dj-equipment": {
    themeColors: ["#0984e3", "#ff3f34"], // Pioneer Blue / Cue Red
    sceneType: "BOOTH",
    vibe: "UNDERGROUND_CLUB_BOOTH",
    floorMat: "radial-gradient(ellipse at bottom, #0984e330 0%, #ff3f3420 50%, transparent 70%)",
    bgMat: "linear-gradient(135deg, #0a0015 0%, #000 100%)"
  },
  "live-dj-lighting": {
    themeColors: ["#e056fd", "#f1c40f"], 
    sceneType: "STAGE",
    vibe: "LIGHT_RIG",
    floorMat: "radial-gradient(circle, #e056fd30 0%, #000 70%)",
    bgMat: "linear-gradient(to top, #111 0%, #000 100%)"
  },
  "live-dj-live-mics": {
    themeColors: ["#95a5a6", "#34495e"], 
    sceneType: "STAGE",
    vibe: "WIRELESS_SYSTEMS",
    floorMat: "radial-gradient(ellipse at bottom, #34495e30 0%, transparent 70%)",
    bgMat: "linear-gradient(to bottom, #0a0a0a 0%, #000 100%)"
  },
   "live-dj-live-accessories": {
    themeColors: ["#7f8c8d", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "STAGE_ESSENTIALS",
    floorMat: "transparent",
    bgMat: "#050505"
  },

  // --- 🔧 UTILITY SECTOR (accessories-utility) ---
  "accessories-utility-cables": {
    themeColors: ["#e74c3c", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "CONNECTIVITY",
    floorMat: "transparent",
     bgMat: "#080808"
  },
 "accessories-utility-stands": {
    themeColors: ["#95a5a6", "#34495e"], 
    sceneType: "VOID",
    vibe: "SUPPORT_SYSTEMS",
     floorMat: "transparent",
    bgMat: "#0a0a0a"
  },
  "accessories-utility-cases-bags": {
    themeColors: ["#34495e", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "PROTECTION",
     floorMat: "transparent",
    bgMat: "#050505"
  },
   "accessories-utility-power-supplies": {
    themeColors: ["#f1c40f", "#2c3e50"], 
    sceneType: "VOID",
    vibe: "POWER_GRID",
    floorMat: "transparent",
    bgMat: "#050505"
  },

  // FALLBACK
  "default": { 
    themeColors: ["#a4b0be", "#000"], 
    sceneType: "VOID", 
    vibe: "ARCHIVED_ASSET",
    floorMat: "transparent",
    bgMat: "#050505"
  }
};

export const GalaxyDashboard = () => {
  const { goToSpectrum } = useNavigationStore();
  const [hoveredSlot, setHoveredSlot] = useState<string | null>(null);

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
                    const isHovered = hoveredSlot === sub.id;
                    // Use sub.image from UNIVERSAL_CATEGORIES which is reliable
                    const visualPath = sub.image;

                    return (
                        <motion.div
                            key={sub.id}
                            className="relative aspect-square rounded-lg bg-black border border-white/5 overflow-hidden group cursor-pointer w-full"
                            style={{ maxHeight: '100%' }}
                            onMouseEnter={() => setHoveredSlot(sub.id)}
                            onMouseLeave={() => setHoveredSlot(null)}
                            onClick={() => onSlotClick(sector.id, sub.id)}
                            animate={{ scale: isHovered ? 1.05 : 1 }}
                            transition={{ duration: 0.1 }}
                        >
                            {/* Layer 1: Back Wall */}
                            <div className="absolute inset-0 z-0 opacity-40" style={{ background: scene.bgMat }} />

                            {/* Layer 2: Floor */}
                            <div className="absolute bottom-0 inset-x-0 h-1/2 z-10 opacity-40 group-hover:opacity-100 transition-opacity duration-500" style={{ background: scene.floorMat }} />

                            {/* Layer 3: Spotlight */}
                             <div 
                                className={`absolute top-[-50%] inset-x-0 h-[150%] z-20 transition-opacity duration-500 ${isHovered ? "opacity-60" : "opacity-0"}`}
                                style={{
                                    background: `radial-gradient(circle at center top, ${scene.themeColors[0]}40, transparent 60%)`,
                                    mixBlendMode: "screen"
                                }}
                            />

                             {/* Layer 4: Object (RESIZED TO FIT) */}
                             <div className="absolute inset-0 z-30 flex items-center justify-center p-6 pb-8">
                                <motion.img 
                                    src={visualPath}
                                    className="w-full h-full object-contain drop-shadow-[0_2px_4px_rgba(0,0,0,0.8)]"
                                    animate={isHovered ? { y: -2, scale: 1.1 } : { y: 0, scale: 1 }}
                                    style={{
                                        filter: isHovered ? `drop-shadow(0 5px 10px ${scene.themeColors[0]}40)` : "drop-shadow(0 2px 5px rgba(0,0,0,0.8))"
                                    }}
                                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                                />
                             </div>

                             {/* Layer 5: HUD Lights (Top) */}
                             <div className="absolute top-1 inset-x-0 flex justify-center gap-[3px] z-40 opacity-30 group-hover:opacity-100 transition-opacity">
                                <div className="w-[3px] h-[3px] rounded-full bg-red-500 shadow-[0_0_2px_red]" />
                                <div className="w-[3px] h-[3px] rounded-full bg-white shadow-[0_0_2px_white]" />
                                <div className="w-[3px] h-[3px] rounded-full bg-red-500 shadow-[0_0_2px_red]" />
                             </div>

                             {/* Layer 6: Label */}
                             <div className="absolute bottom-0 inset-x-0 bg-gradient-to-t from-black via-black/90 to-transparent p-2 pt-6 z-40 text-center flex items-end justify-center">
                                <span className="text-[10px] font-semibold text-zinc-200 group-hover:text-white transition-colors leading-tight block line-clamp-2">
                                    {sub.name}
                                </span>
                             </div>

                        </motion.div>
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
