// frontend/src/lib/brandColors.ts

export const BRAND_COLORS: Record<string, string> = {
  // --- SYNTHS & KEYS ---
  nord: "#E1181F", // Iconic Nord Red
  moog: "#222222", // Industrial Black/Wood
  roland: "#FF6600", // Roland Orange
  korg: "#005AC2", // Korg Blue
  yamaha: "#4C2684", // Yamaha Violet/Blue
  arturia: "#2C3E50", // Deep Slate
  sequential: "#F1C40F", // Vintage Gold
  "teenage engineering": "#888888", // Minimalist Grey

  // --- GUITARS ---
  fender: "#C41230", // Candy Apple Red
  gibson: "#F39C12", // Goldtop Gold
  ibanez: "#990000", // Deep Red
  prs: "#660066", // Purple/Burst
  esp: "#111111", // Metal Black
  taylor: "#8B4513", // Saddle Brown
  martin: "#D2691E", // Natural Wood

  // --- DRUMS ---
  pearl: "#2980B9", // Cool Blue
  tama: "#27AE60", // Emerald
  dw: "#C0392B", // Dark Red
  "roland-vdrums": "#E67E22", // V-Drums Orange
  alesis: "#8E44AD", // Purple

  // --- PRO AUDIO ---
  "allen-heath": "#D32F2F", // A&H Red
  rcf: "#E67E22", // RCF Orange accent
  shure: "#2ECC71", // Green (Mic Grille vibe)
  sennheiser: "#2C3E50", // Tech Grey
  neumann: "#3498DB", // Neumann Blue badge
  ssl: "#BDC3C7", // Console Silver
  "universal-audio": "#7F8C8D", // Hardware Silver/Grey
  focusrite: "#34495E", // Blue/Grey
};

export const getBrandColor = (brandId: string): string => {
  if (!brandId) return "#333333";
  const normalized = brandId.toLowerCase().replace(/[^a-z0-9]/g, "-");
  // Partial match fallback (e.g. "roland-corp" -> "roland")
  const key = Object.keys(BRAND_COLORS).find((k) => normalized.includes(k));
  return key ? BRAND_COLORS[key] : "#333333";
};
