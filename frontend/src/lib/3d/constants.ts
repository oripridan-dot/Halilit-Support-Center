/**
 * 3D Environment System - Constants
 * Global constants for the 3D visualization system
 */

/**
 * Performance profiles for different hardware tiers
 */
export const PERFORMANCE_PROFILES = {
    HIGH: {
        targetFPS: 60,
        shadowQuality: 2048,
        enablePostProcessing: true,
        lodBias: 0,
        textureQuality: 'high' as const,
        enableReflections: true,
        enableSSAO: true,
        renderScale: 1.0
    },
    MEDIUM: {
        targetFPS: 45,
        shadowQuality: 1024,
        enablePostProcessing: true,
        lodBias: 0.5,
        textureQuality: 'medium' as const,
        enableReflections: true,
        enableSSAO: false,
        renderScale: 0.85
    },
    LOW: {
        targetFPS: 30,
        shadowQuality: 512,
        enablePostProcessing: false,
        lodBias: 1.0,
        textureQuality: 'low' as const,
        enableReflections: false,
        enableSSAO: false,
        renderScale: 0.7
    }
} as const;

/**
 * Default camera settings
 */
export const DEFAULT_CAMERA_CONFIG = {
    fov: 50,
    near: 0.1,
    far: 100,
    position: { x: 0, y: 1.6, z: 3 },
    target: { x: 0, y: 0, z: 0 }
} as const;

/**
 * Default lighting intensities
 */
export const DEFAULT_LIGHTING = {
    ambient: 0.4,
    directional: 1.0,
    brandAccent: 0.6,
    pointLight: 0.8
} as const;

/**
 * Asset loading configuration
 */
export const ASSET_CONFIG = {
    maxConcurrentLoads: 4,
    timeout: 30000, // 30 seconds
    retryAttempts: 3,
    retryDelay: 1000,
    dracoDecoderPath: '/draco/',
    ktx2TranscoderPath: '/basis/'
} as const;

/**
 * Interaction thresholds
 */
export const INTERACTION_CONFIG = {
    hoverDebounce: 50, // ms
    clickThreshold: 200, // ms max click duration
    doubleClickThreshold: 300, // ms between clicks
    dragThreshold: 5, // pixels before drag starts
    focusAnimationDuration: 800 // ms
} as const;

/**
 * Performance monitoring thresholds
 */
export const PERFORMANCE_THRESHOLDS = {
    criticalFPS: 20,
    warningFPS: 30,
    goodFPS: 55,
    maxMemoryMB: 500,
    maxDrawCalls: 100,
    maxPolyCount: 200000
} as const;

/**
 * Color space and rendering constants
 */
export const RENDERING_CONFIG = {
    toneMapping: 'ACESFilmic' as const,
    toneMappingExposure: 1.0,
    outputEncoding: 'sRGB' as const,
    shadowMapType: 'PCFSoft' as const,
    physicallyCorrectLights: true,
    gammaFactor: 2.2
} as const;

/**
 * Brand color mixing strategies
 */
export const COLOR_BLEND_MODES = {
    separated: 'Individual color zones with no blending',
    gradient: 'Smooth color gradient between brands',
    reflected: 'Colors visible only in reflections',
    spotlit: 'Dedicated colored spotlights per brand',
    zoned: 'Geographic zones with brand colors',
    ambient: 'Mixed into ambient lighting'
} as const;

/**
 * File size limits (bytes)
 */
export const ASSET_SIZE_LIMITS = {
    model: 10 * 1024 * 1024,      // 10 MB per model
    texture: 4 * 1024 * 1024,     // 4 MB per texture
    sound: 2 * 1024 * 1024,       // 2 MB per sound
    environment: 50 * 1024 * 1024 // 50 MB total per environment
} as const;

/**
 * Error messages
 */
export const ERROR_MESSAGES = {
    WEBGL_NOT_SUPPORTED: 'WebGL is not supported in this browser',
    WEBGL2_NOT_SUPPORTED: 'WebGL 2 is not supported in this browser',
    ENVIRONMENT_NOT_FOUND: 'Environment configuration not found',
    ASSET_LOAD_FAILED: 'Failed to load required assets',
    PERFORMANCE_CRITICAL: 'Performance has degraded significantly',
    MEMORY_LIMIT_EXCEEDED: 'Memory usage exceeds safe limits',
    INIT_FAILED: 'Failed to initialize 3D renderer'
} as const;

/**
 * Development mode settings
 */
export const DEV_CONFIG = {
    showStats: import.meta.env.DEV,
    showHelpers: import.meta.env.DEV,
    showBoundingBoxes: false,
    showNormals: false,
    showWireframe: false,
    showPerformanceWarnings: true,
    logAssetLoading: import.meta.env.DEV,
    enableHotReload: import.meta.env.DEV
} as const;
