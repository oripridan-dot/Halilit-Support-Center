/**
 * 3D Environment System - Main Export File
 * Centralized exports for the Halilit 3D visualization system
 * @module 3d
 */

// Core renderer
export { Environment3DRenderer } from './Environment3DRenderer';

// Asset generation
export { assetGenerator, AssetType } from './asset-generator';
export type { ProceduralAssetGenerator } from './asset-generator';

// Type definitions
export type * from './environment3d.types';

// Environment configurations
export {
    ELECTRIC_GUITARS_ENV,
    ACOUSTIC_GUITARS_ENV,
    getEnvironmentBySubcategory,
    getAllEnvironments,
    getEnvironmentsByCategory
} from './environment-config';

// Utility functions
export * from './utils';

// Constants
export * from './constants';
