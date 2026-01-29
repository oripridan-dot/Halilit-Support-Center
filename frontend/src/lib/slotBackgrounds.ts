/**
 * Slot Background Mappings
 * Maps product categories to contextual background images for the Showcase Slot component.
 * Includes fallback gradients for when images are not yet available.
 * 
 * Path: frontend/src/lib/slotBackgrounds.ts
 */

export interface BackgroundConfig {
    imageUrl: string;
    fallbackGradient: string;
    label: string;
}

const BACKGROUNDS: Record<string, BackgroundConfig> = {
    // Electric Guitars - Stage & Amps
    'electric-guitars': {
        imageUrl: '/assets/bg/stage-amps-blur.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a1a0a 0%, #1a0a00 50%, #4a3a2a 100%)',
        label: 'Stage & Amps',
    },
    // Acoustic Guitars - Luthier Workshop
    'acoustic-guitars': {
        imageUrl: '/assets/bg/luthier-wood-shop.jpg',
        fallbackGradient: 'linear-gradient(135deg, #3a2a1a 0%, #2a1a0a 50%, #1a0a00 100%)',
        label: 'Luthier Workshop',
    },
    // Bass Guitars - Dark Rig
    'bass-guitars': {
        imageUrl: '/assets/bg/bass-rig-dark.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a2a 0%, #0a0a1a 50%, #2a1a1a 100%)',
        label: 'Bass Rig',
    },
    // Drums - Stage Lights
    'drums': {
        imageUrl: '/assets/bg/drum-stage-lights.jpg',
        fallbackGradient: 'linear-gradient(135deg, #2a1a3a 0%, #1a0a2a 50%, #3a1a2a 100%)',
        label: 'Stage Lights',
    },
    // Piano & Keys - Concert Hall
    'keys': {
        imageUrl: '/assets/bg/concert-hall.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a2a1a 100%)',
        label: 'Concert Hall',
    },
    // Synthesizers - Modular Wall
    'synth': {
        imageUrl: '/assets/bg/modular-synth-wall.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a2a 0%, #0a1a2a 50%, #1a0a1a 100%)',
        label: 'Modular Synth',
    },
    // Studio & Recording - Mixing Desk
    'studio': {
        imageUrl: '/assets/bg/studio-mixing-desk.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #2a1a0a 100%)',
        label: 'Studio Desk',
    },
    // Microphones - Vocal Booth
    'vocal': {
        imageUrl: '/assets/bg/vocal-booth.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 50%, #1a1a2a 100%)',
        label: 'Vocal Booth',
    },
    // PA & Live Sound - Festival
    'live': {
        imageUrl: '/assets/bg/outdoor-festival-crowd.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a0a0a 0%, #0a0a1a 50%, #2a1a1a 100%)',
        label: 'Festival Stage',
    },
    // Default fallback
    'default': {
        imageUrl: '/assets/bg/general-store-blur.jpg',
        fallbackGradient: 'linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%)',
        label: 'General Store',
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
            return BACKGROUNDS['acoustic-guitars'];

        case 'bass-guitars':
            return BACKGROUNDS['bass-guitars'];

        // --- DRUMS ---
        case 'acoustic-drums':
        case 'electronic-drums':
        case 'cymbals':
        case 'snares':
        case 'sticks-heads':
        case 'percussion':
        case 'drum-hardware':
            return BACKGROUNDS['drums'];

        // --- KEYS ---
        case 'stage-pianos':
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

        case 'studio-microphones':
        case 'studio-accessories':
        case 'live-mics':
            return BACKGROUNDS['vocal'];

        // --- LIVE ---
        case 'pa-systems':
        case 'live-mixers':
        case 'dj-equipment':
        case 'lighting':
        case 'live-accessories':
            return BACKGROUNDS['live'];

        // --- UTILITY ---
        case 'power-supplies':
            return BACKGROUNDS['electric-guitars']; // Power fits with amps/pedals

        case 'cables':
        case 'cases-bags':
        case 'stands':
            return BACKGROUNDS['default'];

        default:
            // 2. Fallback to fuzzy matching if exact ID not found
            const cat = categoryId.toLowerCase();

            if (cat.includes('guitar')) return BACKGROUNDS['electric-guitars'];
            if (cat.includes('bass')) return BACKGROUNDS['bass-guitars'];
            if (cat.includes('drum') || cat.includes('percussion')) return BACKGROUNDS['drums'];
            if (cat.includes('piano') || cat.includes('keys')) return BACKGROUNDS['keys'];
            if (cat.includes('synth')) return BACKGROUNDS['synth'];
            if (cat.includes('studio') || cat.includes('monitor')) return BACKGROUNDS['studio'];
            if (cat.includes('mic')) return BACKGROUNDS['vocal'];
            if (cat.includes('pa') || cat.includes('live')) return BACKGROUNDS['live'];

            return BACKGROUNDS['default'];
    }
};

