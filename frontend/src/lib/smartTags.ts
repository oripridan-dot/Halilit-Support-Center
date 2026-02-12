/**
 * Smart Tags Engine v1.0
 * 
 * Generates intelligent, content-based sub-division tags for products
 * within a spectrum. Tags are extracted from product names, specs, brands,
 * and features to provide meaningful filtering options.
 * 
 * Examples:
 *   Electric Guitars → "Strat Shape", "LP Shape", "7 String", "Left-handed", "Set"
 *   Synthesizers → "Analog", "Digital", "Polyphonic", "Desktop", "61 Keys"
 *   Studio Monitors → "5\"", "8\"", "Active", "Powered"
 */

import type { ConductorProduct } from '../hooks/useConductorCatalog';

export interface SmartTag {
    id: string;
    label: string;
    count: number;
    /** product IDs that match this tag */
    matchedIds: Set<string>;
}

// ---------------------------------------------------------------------------
// SPECTRUM-SPECIFIC TAG RULES
// Each rule: [regex or keyword test, tag label]
// ---------------------------------------------------------------------------

interface TagRule {
    test: (p: ConductorProduct) => boolean;
    label: string;
    /** Optional group key to prevent overlapping tags */
    group?: string;
}

const text = (p: ConductorProduct): string =>
    `${p.name} ${p.description_short} ${p.description} ${Object.values(p.specs || {}).join(' ')} ${(p.features || []).join(' ')}`.toLowerCase();

const nameLC = (p: ConductorProduct): string => (p.name || '').toLowerCase();

// Helper: check if name/specs contain any keyword
const hasAny = (p: ConductorProduct, ...keywords: string[]) => {
    const t = text(p);
    return keywords.some(k => t.includes(k.toLowerCase()));
};

const specVal = (p: ConductorProduct, key: string): string => {
    const specs = p.specs || {};
    const val = specs[key] || specs[key.toLowerCase()] || '';
    return String(val).toLowerCase();
};

// ---------------------------------------------------------------------------
// PER-SPECTRUM TAG RULE DEFINITIONS
// ---------------------------------------------------------------------------

const SPECTRUM_TAG_RULES: Record<string, TagRule[]> = {
    'electric-guitars': [
        { test: p => hasAny(p, 'strat', 'stratocaster', 'st-'), label: 'Strat Type', group: 'shape' },
        { test: p => hasAny(p, 'telecaster', 'tele', 'tl-'), label: 'Tele Type', group: 'shape' },
        { test: p => hasAny(p, 'les paul', 'lp ', 'lp-', 'single cut', 'singlecut'), label: 'LP Type', group: 'shape' },
        { test: p => hasAny(p, 'sg ', 'sg-', 'double cut'), label: 'SG Type', group: 'shape' },
        { test: p => hasAny(p, 'hollow', 'semi-hollow', 'semi hollow'), label: 'Hollow Body', group: 'shape' },
        { test: p => hasAny(p, 'v shape', 'flying v', 'explorer', 'superstrat', 'shred'), label: 'Modern Shape', group: 'shape' },
        { test: p => hasAny(p, '7 string', '7-string', 'seven string'), label: '7 String', group: 'strings' },
        { test: p => hasAny(p, '8 string', '8-string', 'eight string'), label: '8 String', group: 'strings' },
        { test: p => hasAny(p, '12 string', '12-string', 'twelve string'), label: '12 String', group: 'strings' },
        { test: p => hasAny(p, 'left', 'lefty', 'left-hand', 'lh ', 'שמאלית'), label: 'Left-Handed' },
        { test: p => hasAny(p, 'set ', 'pack ', 'ערכת', 'kit ', 'starter', 'bundle'), label: 'Starter Set' },
        { test: p => hasAny(p, 'floyd', 'tremolo', 'whammy', 'trem'), label: 'Tremolo' },
        { test: p => hasAny(p, 'active', 'emg', 'fishman fluence'), label: 'Active Pickups' },
        { test: p => p.price > 0 && p.price < 2000, label: 'Under ₪2,000', group: 'price' },
        { test: p => p.price >= 2000 && p.price <= 5000, label: '₪2K-5K', group: 'price' },
        { test: p => p.price > 5000, label: 'Over ₪5,000', group: 'price' },
    ],
    'acoustic-guitars': [
        { test: p => hasAny(p, 'dreadnought', 'dread'), label: 'Dreadnought', group: 'shape' },
        { test: p => hasAny(p, 'concert', '000', 'om '), label: 'Concert/OM', group: 'shape' },
        { test: p => hasAny(p, 'jumbo'), label: 'Jumbo', group: 'shape' },
        { test: p => hasAny(p, 'parlor', 'parlour', 'travel', 'mini'), label: 'Travel/Parlor', group: 'shape' },
        { test: p => hasAny(p, 'classical', 'nylon', 'קלאסית'), label: 'Classical/Nylon' },
        { test: p => hasAny(p, 'cutaway', 'cut away', 'ce ', 'electro'), label: 'Cutaway/Electric' },
        { test: p => hasAny(p, '12 string', '12-string'), label: '12 String' },
        { test: p => hasAny(p, 'set ', 'pack ', 'ערכת', 'kit ', 'starter'), label: 'Starter Set' },
        { test: p => hasAny(p, 'left', 'lefty', 'שמאלית'), label: 'Left-Handed' },
    ],
    'bass-guitars': [
        { test: p => hasAny(p, '4 string', '4-string', 'four string') || (!hasAny(p, '5 string', '5-string', '6 string', '6-string') && hasAny(p, 'bass')), label: '4 String', group: 'strings' },
        { test: p => hasAny(p, '5 string', '5-string', 'five string'), label: '5 String', group: 'strings' },
        { test: p => hasAny(p, '6 string', '6-string', 'six string'), label: '6 String', group: 'strings' },
        { test: p => hasAny(p, 'fretless'), label: 'Fretless' },
        { test: p => hasAny(p, 'active'), label: 'Active Electronics' },
        { test: p => hasAny(p, 'acoustic bass', 'acoustic-electric bass'), label: 'Acoustic Bass' },
        { test: p => hasAny(p, 'set ', 'pack ', 'ערכת', 'starter'), label: 'Starter Set' },
    ],
    'guitar-amps': [
        { test: p => hasAny(p, 'combo'), label: 'Combo', group: 'type' },
        { test: p => hasAny(p, 'head', 'amp head'), label: 'Amp Head', group: 'type' },
        { test: p => hasAny(p, 'cabinet', 'cab ', 'speaker'), label: 'Cabinet', group: 'type' },
        { test: p => hasAny(p, 'tube', 'valve', 'el34', '6l6', '12ax7'), label: 'Tube/Valve' },
        { test: p => hasAny(p, 'solid state', 'transistor', 'solid-state'), label: 'Solid State' },
        { test: p => hasAny(p, 'modeling', 'digital', 'modelling'), label: 'Modeling/Digital' },
        { test: p => hasAny(p, 'bass amp', 'bass combo'), label: 'Bass Amp' },
        { test: p => hasAny(p, 'practice', '10w', '15w', '20w', 'mini'), label: 'Practice Size' },
    ],
    'guitar-pedals': [
        { test: p => hasAny(p, 'overdrive', 'od-', 'tube screamer'), label: 'Overdrive', group: 'effect' },
        { test: p => hasAny(p, 'distortion', 'fuzz', 'big muff', 'rat'), label: 'Distortion/Fuzz', group: 'effect' },
        { test: p => hasAny(p, 'delay', 'echo'), label: 'Delay', group: 'effect' },
        { test: p => hasAny(p, 'reverb', 'hall', 'spring'), label: 'Reverb', group: 'effect' },
        { test: p => hasAny(p, 'chorus', 'flanger', 'phaser', 'modulation', 'tremolo', 'vibrato'), label: 'Modulation', group: 'effect' },
        { test: p => hasAny(p, 'wah', 'cry baby', 'expression'), label: 'Wah/Expression', group: 'effect' },
        { test: p => hasAny(p, 'multi', 'multi-fx', 'multi-effect', 'processor'), label: 'Multi-FX', group: 'effect' },
        { test: p => hasAny(p, 'looper', 'loop'), label: 'Looper', group: 'effect' },
        { test: p => hasAny(p, 'tuner', 'chromatic'), label: 'Tuner' },
        { test: p => hasAny(p, 'compressor', 'comp'), label: 'Compressor', group: 'effect' },
        { test: p => hasAny(p, 'power supply', 'power', 'adapter'), label: 'Power Supply' },
        { test: p => hasAny(p, 'pedalboard', 'board'), label: 'Pedalboard' },
    ],
    'synthesizers': [
        { test: p => hasAny(p, 'analog', 'analogue'), label: 'Analog' },
        { test: p => hasAny(p, 'digital', 'fm ', 'wavetable'), label: 'Digital/FM' },
        { test: p => hasAny(p, 'modular', 'eurorack', 'module'), label: 'Modular' },
        { test: p => hasAny(p, 'desktop', 'tabletop', 'module'), label: 'Desktop' },
        { test: p => hasAny(p, '61 key', '61-key', '61 מקשים'), label: '61 Keys', group: 'keys' },
        { test: p => hasAny(p, '88 key', '88-key', '88 מקשים'), label: '88 Keys', group: 'keys' },
        { test: p => hasAny(p, '49 key', '49-key'), label: '49 Keys', group: 'keys' },
        { test: p => hasAny(p, '25 key', '25-key', '37 key', '37-key'), label: 'Mini Keys', group: 'keys' },
        { test: p => hasAny(p, 'vocoder', 'vocal'), label: 'Vocoder' },
        { test: p => hasAny(p, 'stand', 'pedal', 'case', 'bag', 'cover', 'dust', 'soft case', 'hard case'), label: 'Accessories' },
    ],
    'stage-pianos': [
        { test: p => hasAny(p, '88 key', '88-key', '88 מקשים', 'hammer', 'weighted'), label: '88 Keys/Weighted', group: 'keys' },
        { test: p => hasAny(p, '73 key', '73-key', '76 key', '76-key'), label: '73-76 Keys', group: 'keys' },
        { test: p => hasAny(p, '61 key', '61-key'), label: '61 Keys', group: 'keys' },
        { test: p => hasAny(p, 'portable', 'stage'), label: 'Stage/Portable' },
        { test: p => hasAny(p, 'organ', 'drawbar'), label: 'With Organ' },
        { test: p => hasAny(p, 'stand', 'pedal', 'case', 'bag', 'cover'), label: 'Accessories' },
    ],
    'midi-controllers': [
        { test: p => hasAny(p, '25 key', '25-key'), label: '25 Keys', group: 'keys' },
        { test: p => hasAny(p, '49 key', '49-key'), label: '49 Keys', group: 'keys' },
        { test: p => hasAny(p, '61 key', '61-key'), label: '61 Keys', group: 'keys' },
        { test: p => hasAny(p, 'pad', 'drum pad', 'finger drum'), label: 'Pad Controller' },
        { test: p => hasAny(p, 'fader', 'mixer', 'knob', 'control surface'), label: 'Fader/Knob' },
        { test: p => hasAny(p, 'wind', 'breath'), label: 'Wind Controller' },
    ],
    'audio-interfaces': [
        { test: p => hasAny(p, '2 in', '2-in', '2x2', '1x1', '2i2', 'solo', 'one'), label: '1-2 Inputs', group: 'io' },
        { test: p => hasAny(p, '4 in', '4-in', '4x4', '4i4'), label: '4 Inputs', group: 'io' },
        { test: p => hasAny(p, '8 in', '8-in', '8x8', '8i8', '8-channel', 'adat'), label: '8+ Inputs', group: 'io' },
        { test: p => hasAny(p, 'usb-c', 'usb c', 'type-c', 'type c'), label: 'USB-C' },
        { test: p => hasAny(p, 'thunderbolt', 'tb3', 'tb4'), label: 'Thunderbolt' },
        { test: p => hasAny(p, 'portable', 'mobile', 'bus powered', 'bus-powered'), label: 'Portable' },
        { test: p => hasAny(p, 'dsp', 'processing', 'fx'), label: 'Built-in DSP' },
    ],
    'studio-monitors': [
        { test: p => hasAny(p, '3 inch', '3"', '3.5"', '4 inch', '4"', '4.5"', 'small'), label: '3-4"', group: 'size' },
        { test: p => hasAny(p, '5 inch', '5"', '5.25"'), label: '5"', group: 'size' },
        { test: p => hasAny(p, '6 inch', '6"', '6.5"'), label: '6"', group: 'size' },
        { test: p => hasAny(p, '7 inch', '7"', '8 inch', '8"'), label: '7-8"', group: 'size' },
        { test: p => hasAny(p, 'subwoofer', 'sub ', 'sub-'), label: 'Subwoofer' },
        { test: p => hasAny(p, 'headphone', 'headphones'), label: 'Headphones' },
        { test: p => hasAny(p, 'active', 'powered', 'bi-amp'), label: 'Active/Powered' },
    ],
    'studio-microphones': [
        { test: p => hasAny(p, 'condenser', 'large diaphragm', 'small diaphragm'), label: 'Condenser', group: 'type' },
        { test: p => hasAny(p, 'dynamic', 'sm57', 'sm58', 'sm7'), label: 'Dynamic', group: 'type' },
        { test: p => hasAny(p, 'ribbon'), label: 'Ribbon', group: 'type' },
        { test: p => hasAny(p, 'usb', 'podcast', 'streaming'), label: 'USB/Podcast' },
        { test: p => hasAny(p, 'shotgun', 'boom'), label: 'Shotgun' },
        { test: p => hasAny(p, 'lavalier', 'lav', 'clip', 'lapel'), label: 'Lavalier' },
        { test: p => hasAny(p, 'wireless', 'inalámbrico'), label: 'Wireless' },
        { test: p => hasAny(p, 'stereo', 'matched pair', 'pair'), label: 'Stereo/Pair' },
    ],
    'electronic-drums': [
        { test: p => hasAny(p, 'kit', 'set', 'ערכת', 'td-', 'dtx'), label: 'Full Kit', group: 'type' },
        { test: p => hasAny(p, 'pad', 'trigger', 'snare pad', 'tom pad'), label: 'Pad/Trigger', group: 'type' },
        { test: p => hasAny(p, 'cymbal', 'hi-hat', 'ride', 'crash'), label: 'E-Cymbal', group: 'type' },
        { test: p => hasAny(p, 'module', 'brain', 'sound module'), label: 'Module' },
        { test: p => hasAny(p, 'mesh', 'mesh head'), label: 'Mesh Head' },
        { test: p => hasAny(p, 'practice', 'portable', 'compact', 'tabletop'), label: 'Compact/Practice' },
    ],
    'acoustic-drums': [
        { test: p => hasAny(p, 'shell pack', 'kit', 'set', 'ערכת'), label: 'Shell Pack/Kit' },
        { test: p => hasAny(p, 'snare'), label: 'Snare Drum' },
        { test: p => hasAny(p, 'tom', 'floor tom'), label: 'Tom' },
        { test: p => hasAny(p, 'kick', 'bass drum'), label: 'Bass Drum' },
        { test: p => hasAny(p, 'maple'), label: 'Maple' },
        { test: p => hasAny(p, 'birch'), label: 'Birch' },
        { test: p => hasAny(p, 'poplar', 'basswood'), label: 'Poplar/Other' },
    ],
    'pa-systems': [
        { test: p => hasAny(p, 'powered', 'active'), label: 'Powered/Active', group: 'type' },
        { test: p => hasAny(p, 'passive'), label: 'Passive', group: 'type' },
        { test: p => hasAny(p, 'subwoofer', 'sub'), label: 'Subwoofer' },
        { test: p => hasAny(p, 'line array', 'column'), label: 'Line Array/Column' },
        { test: p => hasAny(p, 'portable', 'battery', 'rechargeable', 'bluetooth'), label: 'Portable/Battery' },
        { test: p => hasAny(p, '8"', '10"', '12"', '15"', 'inch'), label: 'Full-Size' },
    ],
    'live-mixers': [
        { test: p => hasAny(p, 'digital'), label: 'Digital', group: 'type' },
        { test: p => hasAny(p, 'analog', 'analogue'), label: 'Analog', group: 'type' },
        { test: p => hasAny(p, 'powered', 'power mixer'), label: 'Powered' },
        { test: p => hasAny(p, '4 channel', '6 channel', '8 channel', 'small'), label: 'Small (4-8ch)', group: 'size' },
        { test: p => hasAny(p, '12 channel', '16 channel', '24 channel', '32 channel'), label: 'Large (12+ch)', group: 'size' },
        { test: p => hasAny(p, 'usb', 'recording'), label: 'USB/Recording' },
    ],
    'dj-equipment': [
        { test: p => hasAny(p, 'controller'), label: 'DJ Controller', group: 'type' },
        { test: p => hasAny(p, 'turntable', 'vinyl'), label: 'Turntable', group: 'type' },
        { test: p => hasAny(p, 'mixer', 'dj mixer'), label: 'DJ Mixer', group: 'type' },
        { test: p => hasAny(p, 'headphone'), label: 'DJ Headphones' },
    ],
};

// ---------------------------------------------------------------------------
// GENERIC TAG RULES (applied to any spectrum without specific rules)
// ---------------------------------------------------------------------------

const GENERIC_RULES: TagRule[] = [
    { test: p => hasAny(p, 'set ', 'pack ', 'ערכת', 'bundle', 'kit'), label: 'Bundle/Set' },
    { test: p => hasAny(p, 'wireless', 'bluetooth', 'אלחוטי'), label: 'Wireless' },
    { test: p => hasAny(p, 'portable', 'compact', 'mini', 'נייד'), label: 'Portable' },
    { test: p => hasAny(p, 'professional', 'pro ', 'מקצועי'), label: 'Professional' },
    { test: p => p.price > 0, label: 'Has Price' },
    { test: p => hasAny(p, 'stand', 'case', 'bag', 'cover', 'pedal board', 'כיסוי', 'מעמד'), label: 'Accessories' },
];

// ---------------------------------------------------------------------------
// TAG GENERATION ENGINE
// ---------------------------------------------------------------------------

/**
 * Generate smart tags for a list of products in a spectrum.
 * Returns tags sorted by count descending, filtered to only include tags
 * that have at least 2 matching products (or 1 if total < 10).
 */
export function generateSmartTags(
    products: ConductorProduct[],
    spectrumId: string
): SmartTag[] {
    if (!products || products.length === 0) return [];

    // Get rules: specific first, then generic
    const rules = [
        ...(SPECTRUM_TAG_RULES[spectrumId] || []),
        ...GENERIC_RULES,
    ];

    // Evaluate all rules against all products
    const tagMap = new Map<string, SmartTag>();

    for (const rule of rules) {
        for (const product of products) {
            try {
                if (rule.test(product)) {
                    const existing = tagMap.get(rule.label);
                    if (existing) {
                        existing.count++;
                        existing.matchedIds.add(product.id);
                    } else {
                        tagMap.set(rule.label, {
                            id: rule.label.toLowerCase().replace(/[^a-z0-9]/g, '-'),
                            label: rule.label,
                            count: 1,
                            matchedIds: new Set([product.id]),
                        });
                    }
                }
            } catch {
                // Skip broken product entries
            }
        }
    }

    // Also generate brand tags if there are more than 2 brands
    const brandCounts = new Map<string, Set<string>>();
    for (const p of products) {
        const brand = p.brand;
        if (!brand) continue;
        if (!brandCounts.has(brand)) brandCounts.set(brand, new Set());
        brandCounts.get(brand)!.add(p.id);
    }

    // Don't add brand tags — brands are already shown as swim lanes
    // Only add "Has Image" tag since many products lack images
    const withImage = products.filter(p => p.image_url);
    if (withImage.length > 0 && withImage.length < products.length) {
        tagMap.set('With Image', {
            id: 'with-image',
            label: 'With Image',
            count: withImage.length,
            matchedIds: new Set(withImage.map(p => p.id)),
        });
    }

    // Minimum count threshold: at least 1 for small sets, 2 for larger
    const minCount = products.length < 10 ? 1 : 2;

    // Sort by count descending, filter out tiny tags
    return Array.from(tagMap.values())
        .filter(tag => tag.count >= minCount)
        .sort((a, b) => b.count - a.count)
        .slice(0, 12); // Max 12 tags to avoid UI clutter
}
