/**
 * Slot Background Mappings
 * Maps product categories to contextual background images for the Showcase Slot
 * and the ContextualResponse "Mini World" component.
 *
 * Performance: All images are static assets served from /assets/bg/.
 * The `overlayColor` field enables per-category tinting when reusing base images.
 *
 * Path: frontend/src/lib/slotBackgrounds.ts
 */

export interface BackgroundConfig {
    imageUrl: string;
    fallbackGradient: string;
    label: string;
    /** Optional CSS color to tint the overlay — lets reused images feel distinct */
    overlayColor?: string;
}

const BACKGROUNDS: Record<string, BackgroundConfig> = {
    // ─── GUITARS ───
    'electric-guitars': {
        imageUrl: '/assets/bg/stage-amps-blur.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a1a0a 0%, #1a0a00 50%, #4a3a2a 100%)',
        label: 'Stage & Amps',
    },
    'acoustic-guitars': {
        imageUrl: '/assets/bg/luthier-wood-shop.jpg',
        fallbackGradient: 'linear-gradient(135deg, #3a2a1a 0%, #2a1a0a 50%, #1a0a00 100%)',
        label: 'Luthier Workshop',
    },
    'bass-guitars': {
        imageUrl: '/assets/bg/bass-rig-dark.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a2a 0%, #0a0a1a 50%, #2a1a1a 100%)',
        label: 'Bass Rig',
    },

    // ─── DRUMS & PERCUSSION ───
    'drums': {
        imageUrl: '/assets/bg/drum-stage-lights.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a1a3a 0%, #1a0a2a 50%, #3a1a2a 100%)',
        label: 'Stage Lights',
    },
    'percussion': {
        imageUrl: '/assets/bg/drum-stage-lights.jpg',
        fallbackGradient: 'linear-gradient(135deg, #3a1a0a 0%, #2a0a0a 50%, #3a2a0a 100%)',
        label: 'Percussion Studio',
        overlayColor: '#3a1a0a',
    },

    // ─── KEYS ───
    'keys': {
        imageUrl: '/assets/bg/concert-hall.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a2a1a 100%)',
        label: 'Concert Hall',
    },
    'synth': {
        imageUrl: '/assets/bg/modular-synth-wall.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a2a 0%, #0a1a2a 50%, #1a0a1a 100%)',
        label: 'Modular Synth',
    },

    // ─── STUDIO & RECORDING ───
    'studio': {
        imageUrl: '/assets/bg/studio-mixing-desk.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a1a0a 100%)',
        label: 'Studio Desk',
    },
    'headphones': {
        imageUrl: '/assets/bg/studio-mixing-desk.jpg',
        fallbackGradient: 'linear-gradient(135deg, #0a1a2a 0%, #000000 50%, #1a2a3a 100%)',
        label: 'Listening Lounge',
        overlayColor: '#0a1a2a',
    },
    'vocal': {
        imageUrl: '/assets/bg/vocal-booth.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #1a1a2a 100%)',
        label: 'Vocal Booth',
    },

    // ─── LIVE & DJ ───
    'live': {
        imageUrl: '/assets/bg/outdoor-festival-crowd.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a0a0a 0%, #0a0a1a 50%, #2a1a1a 100%)',
        label: 'Festival Stage',
    },
    'dj': {
        imageUrl: '/assets/bg/outdoor-festival-crowd.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a0a2a 0%, #1a0a1a 50%, #3a0a3a 100%)',
        label: 'Club Booth',
        overlayColor: '#4a0a4a',
    },

    // ─── WIND & EDUCATION ───
    'wind': {
        imageUrl: '/assets/bg/concert-hall.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a2a 0%, #0a0a1a 50%, #1a1a1a 100%)',
        label: 'Concert Stage',
        overlayColor: '#1a1a2a',
    },
    'education': {
        imageUrl: '/assets/bg/general-store-blur.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a1a0a 0%, #1a1a1a 50%, #0a0a2a 100%)',
        label: 'Classroom',
        overlayColor: '#1a1a2a',
    },

    // ─── DEFAULT ───
    'default': {
        imageUrl: '/assets/bg/general-store-blur.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)',
        label: 'Showroom',
    },
};

/**
 * Get background configuration based on category
 * Returns both image URL and fallback gradient
 * 
 * Uses explicit mapping to ensure no "green default" leaks unless absolutely necessary.
 */
export const getContextBackground = (categoryId: string): BackgroundConfig => {
    // 1. Explicit ID Mapping (Primary Strategy)
    switch (categoryId) {
        // --- GUITARS ---
        case 'electric-guitars':
        case 'guitar-amps':
        case 'guitar-pedals':
            return BACKGROUNDS['electric-guitars'];

        case 'acoustic-guitars':
        case 'folk-instruments':
        case 'guitar-accessories':
        case 'ukuleles':
            return BACKGROUNDS['acoustic-guitars'];

        case 'bass-guitars':
            return BACKGROUNDS['bass-guitars'];

        // --- DRUMS & PERCUSSION ---
        case 'acoustic-drums':
        case 'electronic-drums':
        case 'cymbals':
        case 'snares':
        case 'sticks-heads':
        case 'drum-hardware':
            return BACKGROUNDS['drums'];

        case 'percussion':
        case 'hand-percussion':
        case 'bongos':
        case 'cajons':
        case 'congas':
        case 'shakers':
        case 'tambourines':
            return BACKGROUNDS['percussion'];

        // --- KEYS ---
        case 'stage-pianos':
        case 'digital-pianos':
        case 'keys-accessories':
            return BACKGROUNDS['keys'];

        case 'synthesizers':
        case 'midi-controllers':
        case 'grooveboxes':
        case 'eurorack':
            return BACKGROUNDS['synth'];

        // --- STUDIO ---
        case 'audio-interfaces':
        case 'studio-monitors':
        case 'outboard-gear':
        case 'software-plugins':
            return BACKGROUNDS['studio'];

        case 'headphones':
        case 'in-ear-monitors':
            return BACKGROUNDS['headphones'];

        case 'studio-microphones':
        case 'studio-accessories':
        case 'live-mics':
            return BACKGROUNDS['vocal'];

        // --- LIVE & DJ ---
        case 'pa-systems':
        case 'live-mixers':
        case 'lighting':
        case 'live-accessories':
        case 'wireless-systems':
            return BACKGROUNDS['live'];

        case 'dj-equipment':
        case 'dj-controllers':
        case 'turntables':
            return BACKGROUNDS['dj'];

        // --- WIND & EDUCATION ---
        case 'wind-instruments':
        case 'brass':
        case 'woodwind':
        case 'harmonicas':
        case 'recorders':
            return BACKGROUNDS['wind'];

        case 'education':
        case 'classroom':
        case 'orff-instruments':
        case 'boomwhackers':
            return BACKGROUNDS['education'];

        // --- UTILITY ---
        case 'power-supplies':
            return BACKGROUNDS['electric-guitars'];

        case 'cables':
        case 'cases-bags':
        case 'stands':
            return BACKGROUNDS['default'];

        default: {
            // 2. Fallback to fuzzy matching if exact ID not found
            const cat = categoryId.toLowerCase();

            // DJ/Controller (before generic "controller" match)
            if (cat.includes('dj') || (cat.includes('controller') && !cat.includes('midi'))) return BACKGROUNDS['dj'];
            // Headphones
            if (cat.includes('headphone') || cat.includes('in-ear')) return BACKGROUNDS['headphones'];
            // Percussion (warm tint)
            if (cat.includes('percussion') || cat.includes('bongo') || cat.includes('cajon') || cat.includes('shaker')) return BACKGROUNDS['percussion'];
            // Wind
            if (cat.includes('wind') || cat.includes('brass') || cat.includes('woodwind') || cat.includes('harmonica') || cat.includes('recorder')) return BACKGROUNDS['wind'];
            // Education
            if (cat.includes('education') || cat.includes('classroom') || cat.includes('orff') || cat.includes('boomwhack')) return BACKGROUNDS['education'];

            // Broad categories
            if (cat.includes('guitar')) return BACKGROUNDS['electric-guitars'];
            if (cat.includes('bass')) return BACKGROUNDS['bass-guitars'];
            if (cat.includes('drum') || cat.includes('cymbal')) return BACKGROUNDS['drums'];
            if (cat.includes('piano') || cat.includes('keys')) return BACKGROUNDS['keys'];
            if (cat.includes('synth') || cat.includes('eurorack') || cat.includes('keyboard')) return BACKGROUNDS['synth'];
            if (cat.includes('studio') || cat.includes('monitor') || cat.includes('interface')) return BACKGROUNDS['studio'];
            if (cat.includes('mic') || cat.includes('vocal')) return BACKGROUNDS['vocal'];
            if (cat.includes('pa') || cat.includes('live') || cat.includes('mixer') || cat.includes('speaker') || cat.includes('wireless')) return BACKGROUNDS['live'];

            return BACKGROUNDS['default'];
        }
    }
};

