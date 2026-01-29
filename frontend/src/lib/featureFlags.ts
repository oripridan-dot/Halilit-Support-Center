/**
 * Feature Flags Configuration
 * Controls feature rollout and A/B testing
 * 
 * Path: frontend/src/lib/featureFlags.ts
 */

export interface FeatureFlags {
  ENABLE_3D_SLOTS: boolean;
  LAZY_LOAD_3D: boolean;
  FALLBACK_TO_2D_ON_ERROR: boolean;
  SHOW_3D_LOADING_SPINNER: boolean;
  ENABLE_3D_ON_MOBILE: boolean;
}

/**
 * Get feature flags from environment variables or defaults
 * Environment variables take precedence
 */
export const FEATURE_FLAGS: FeatureFlags = {
  // Enable 3D slots globally
  ENABLE_3D_SLOTS: import.meta.env.VITE_3D_SLOTS === "true",

  // Load 3D environments on-demand (hover/interaction)
  // When false, loads immediately (full preload mode)
  LAZY_LOAD_3D: import.meta.env.VITE_3D_LAZY !== "false",

  // Fallback to 2D if 3D rendering fails
  FALLBACK_TO_2D_ON_ERROR: import.meta.env.VITE_3D_FALLBACK !== "false",

  // Show loading spinner while 3D initializes
  SHOW_3D_LOADING_SPINNER: import.meta.env.VITE_3D_SPINNER !== "false",

  // Enable 3D on mobile devices (may impact performance)
  ENABLE_3D_ON_MOBILE: import.meta.env.VITE_3D_MOBILE === "true",
};

/**
 * Check if a feature is enabled
 */
export const isFeatureEnabled = (feature: keyof FeatureFlags): boolean => {
  return FEATURE_FLAGS[feature];
};

/**
 * Log current feature flag state (for debugging)
 */
export const logFeatureFlags = (): void => {
  console.group("🚩 Feature Flags");
  Object.entries(FEATURE_FLAGS).forEach(([key, value]) => {
    console.log(`  ${key}: ${value ? "✓ ON" : "✗ OFF"}`);
  });
  console.groupEnd();
};

/**
 * Default flags for different deployment environments
 */
export const ENVIRONMENT_PRESETS = {
  development: {
    ENABLE_3D_SLOTS: false, // Off by default in dev
    LAZY_LOAD_3D: true,
    FALLBACK_TO_2D_ON_ERROR: true,
    SHOW_3D_LOADING_SPINNER: true,
    ENABLE_3D_ON_MOBILE: false,
  } as FeatureFlags,

  staging: {
    ENABLE_3D_SLOTS: false, // Off initially
    LAZY_LOAD_3D: true,
    FALLBACK_TO_2D_ON_ERROR: true,
    SHOW_3D_LOADING_SPINNER: true,
    ENABLE_3D_ON_MOBILE: false,
  } as FeatureFlags,

  production: {
    ENABLE_3D_SLOTS: false, // Off for safe rollout
    LAZY_LOAD_3D: true,
    FALLBACK_TO_2D_ON_ERROR: true,
    SHOW_3D_LOADING_SPINNER: true,
    ENABLE_3D_ON_MOBILE: false,
  } as FeatureFlags,
};

/**
 * Rollout percentages (for canary deployments)
 * Value between 0-100 representing % of users to show feature
 */
export const ROLLOUT_PERCENTAGES = {
  ENABLE_3D_SLOTS: 0, // 0% initially, increment gradually
  // Week 1: 0%, Week 2: 10%, Week 3: 50%, Week 4: 100%
};

/**
 * Check if user should see feature based on rollout percentage
 * Uses user ID hash for consistent experience
 */
export const shouldEnableFeatureForUser = (
  featureName: keyof typeof ROLLOUT_PERCENTAGES,
  userId?: string
): boolean => {
  if (!isFeatureEnabled(featureName as keyof FeatureFlags)) {
    return false;
  }

  const percentage = ROLLOUT_PERCENTAGES[featureName];
  if (percentage === 100) return true;
  if (percentage === 0) return false;

  // Use userId or random value for consistent hashing
  const hashValue = userId ? hashString(userId) : Math.random() * 100;
  return hashValue % 100 < percentage;
};

/**
 * Simple hash function for user ID
 */
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

// Log flags in development
if (import.meta.env.DEV) {
  // Uncomment to see flags on app load:
  // logFeatureFlags();
}
