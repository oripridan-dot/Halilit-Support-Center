/**
 * Hooks barrel — frontend/src/hooks/index.ts
 *
 * Re-exports all hooks from a single import path (`../../hooks`).
 * Also re-exports useNavigationStore from the store so view components
 * only need ONE import statement.
 */

export {
    useConductorCatalog,
    useProductsByGalaxy,
    useProductsBySpectrum,
    useProductRelationships,
    useProductFamily,
    useProductVariants,
    useConductorProductsByCategory,
    useSpectrumStar,
} from './useConductorCatalog';

export { useJITIntelligence } from './useJITIntelligence';
export type { JITPhase, JITIntelligenceState, VisualIntelData } from './useJITIntelligence';
export { useImageRefresh } from './useImageRefresh';
export { useDebounce } from './useDebounce';
export { useDebounceValue } from './useDebounceValue';
export { useValidateHeroImage } from './useValidateHeroImage';

// Re-export navigation store hook so views can also import it from here
export { useNavigationStore } from '../store/navigationStore';
