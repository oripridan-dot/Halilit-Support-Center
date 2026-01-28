/**
 * 3D Environment System - Utility Functions
 * Helper functions for 3D operations and data processing
 */

import type { Vector3, Color, BoundingBox, LoadProgress } from './environment3d.types';

/**
 * Convert hex color string to RGB color object
 * @param hex - Hex color string (e.g., '#FF0000' or 'FF0000')
 * @returns RGB color object with values 0-1
 */
export function hexToRGB(hex: string): Color {
    const cleaned = hex.replace('#', '');
    const bigint = parseInt(cleaned, 16);
    return {
        r: ((bigint >> 16) & 255) / 255,
        g: ((bigint >> 8) & 255) / 255,
        b: (bigint & 255) / 255
    };
}

/**
 * Convert RGB color object to hex string
 * @param color - RGB color object with values 0-1
 * @returns Hex color string with '#' prefix
 */
export function rgbToHex(color: Color): string {
    const r = Math.round(color.r * 255);
    const g = Math.round(color.g * 255);
    const b = Math.round(color.b * 255);
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
}

/**
 * Interpolate between two Vector3 positions
 * @param start - Start position
 * @param end - End position
 * @param t - Interpolation factor 0-1
 * @returns Interpolated position
 */
export function lerpVector3(start: Vector3, end: Vector3, t: number): Vector3 {
    return {
        x: start.x + (end.x - start.x) * t,
        y: start.y + (end.y - start.y) * t,
        z: start.z + (end.z - start.z) * t
    };
}

/**
 * Interpolate between two colors
 * @param start - Start color
 * @param end - End color
 * @param t - Interpolation factor 0-1
 * @returns Interpolated color
 */
export function lerpColor(start: Color, end: Color, t: number): Color {
    return {
        r: start.r + (end.r - start.r) * t,
        g: start.g + (end.g - start.g) * t,
        b: start.b + (end.b - start.b) * t,
        a: start.a !== undefined && end.a !== undefined
            ? start.a + (end.a - start.a) * t
            : undefined
    };
}

/**
 * Calculate distance between two Vector3 points
 * @param a - First point
 * @param b - Second point
 * @returns Euclidean distance
 */
export function distanceVector3(a: Vector3, b: Vector3): number {
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dz = b.z - a.z;
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
}

/**
 * Normalize a Vector3 to unit length
 * @param v - Vector to normalize
 * @returns Normalized vector
 */
export function normalizeVector3(v: Vector3): Vector3 {
    const length = Math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (length === 0) return { x: 0, y: 0, z: 0 };
    return {
        x: v.x / length,
        y: v.y / length,
        z: v.z / length
    };
}

/**
 * Check if a point is inside a bounding box
 * @param point - Point to check
 * @param box - Bounding box
 * @returns True if point is inside box
 */
export function isPointInBox(point: Vector3, box: BoundingBox): boolean {
    return (
        point.x >= box.min.x && point.x <= box.max.x &&
        point.y >= box.min.y && point.y <= box.max.y &&
        point.z >= box.min.z && point.z <= box.max.z
    );
}

/**
 * Calculate bounding box center
 * @param box - Bounding box
 * @returns Center point
 */
export function getBoundingBoxCenter(box: BoundingBox): Vector3 {
    return {
        x: (box.min.x + box.max.x) / 2,
        y: (box.min.y + box.max.y) / 2,
        z: (box.min.z + box.max.z) / 2
    };
}

/**
 * Calculate bounding box size
 * @param box - Bounding box
 * @returns Size vector
 */
export function getBoundingBoxSize(box: BoundingBox): Vector3 {
    return {
        x: box.max.x - box.min.x,
        y: box.max.y - box.min.y,
        z: box.max.z - box.min.z
    };
}

/**
 * Format bytes to human-readable string
 * @param bytes - Number of bytes
 * @param decimals - Decimal places
 * @returns Formatted string (e.g., '2.5 MB')
 */
export function formatBytes(bytes: number, decimals: number = 2): string {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Format milliseconds to human-readable duration
 * @param ms - Milliseconds
 * @returns Formatted string (e.g., '2.5s' or '1m 30s')
 */
export function formatDuration(ms: number): string {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;

    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
}

/**
 * Calculate estimated time remaining for loading
 * @param progress - Current load progress
 * @returns Estimated ms remaining or null if can't calculate
 */
export function estimateTimeRemaining(progress: LoadProgress): number | null {
    if (!progress.elapsed || progress.percentage === 0) return null;

    const totalTime = (progress.elapsed / progress.percentage) * 100;
    return Math.max(0, totalTime - progress.elapsed);
}

/**
 * Clamp a value between min and max
 * @param value - Value to clamp
 * @param min - Minimum value
 * @param max - Maximum value
 * @returns Clamped value
 */
export function clamp(value: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, value));
}

/**
 * Map a value from one range to another
 * @param value - Input value
 * @param inMin - Input range minimum
 * @param inMax - Input range maximum
 * @param outMin - Output range minimum
 * @param outMax - Output range maximum
 * @returns Mapped value
 */
export function mapRange(
    value: number,
    inMin: number,
    inMax: number,
    outMin: number,
    outMax: number
): number {
    return ((value - inMin) * (outMax - outMin)) / (inMax - inMin) + outMin;
}

/**
 * Easing functions for animations
 */
export const easing = {
    linear: (t: number) => t,
    easeIn: (t: number) => t * t,
    easeOut: (t: number) => t * (2 - t),
    easeInOut: (t: number) => (t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t),
    easeInCubic: (t: number) => t * t * t,
    easeOutCubic: (t: number) => (--t) * t * t + 1,
    easeInOutCubic: (t: number) =>
        t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1,
    elastic: (t: number) => {
        if (t === 0 || t === 1) return t;
        const p = 0.3;
        const s = p / 4;
        return Math.pow(2, -10 * t) * Math.sin(((t - s) * (2 * Math.PI)) / p) + 1;
    },
    bounce: (t: number) => {
        if (t < 1 / 2.75) {
            return 7.5625 * t * t;
        } else if (t < 2 / 2.75) {
            return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
        } else if (t < 2.5 / 2.75) {
            return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
        } else {
            return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
        }
    }
};

/**
 * Detect WebGL support and capabilities
 * @returns Object with WebGL support info
 */
export function detectWebGLSupport(): {
    webgl: boolean;
    webgl2: boolean;
    maxTextureSize: number;
    maxVertexTextures: number;
    maxTextureUnits: number;
    precision: 'highp' | 'mediump' | 'lowp' | 'unknown';
} {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl2');
        const gl1 = canvas.getContext('webgl');

        if (!gl1 && !gl) {
            return {
                webgl: false,
                webgl2: false,
                maxTextureSize: 0,
                maxVertexTextures: 0,
                maxTextureUnits: 0,
                precision: 'unknown'
            };
        }

        const context = gl || gl1;
        const shaderPrecision = context?.getShaderPrecisionFormat(
            context.FRAGMENT_SHADER,
            context.HIGH_FLOAT
        );

        return {
            webgl: !!gl1,
            webgl2: !!gl,
            maxTextureSize: context?.getParameter(context.MAX_TEXTURE_SIZE) ?? 0,
            maxVertexTextures: context?.getParameter(context.MAX_VERTEX_TEXTURE_IMAGE_UNITS) ?? 0,
            maxTextureUnits: context?.getParameter(context.MAX_TEXTURE_IMAGE_UNITS) ?? 0,
            precision: shaderPrecision?.precision ?
                (shaderPrecision.precision >= 23 ? 'highp' :
                    shaderPrecision.precision >= 10 ? 'mediump' : 'lowp') :
                'unknown'
        };
    } catch (error) {
        return {
            webgl: false,
            webgl2: false,
            maxTextureSize: 0,
            maxVertexTextures: 0,
            maxTextureUnits: 0,
            precision: 'unknown'
        };
    }
}

/**
 * Detect device performance tier
 * @returns Performance tier: 'high' | 'medium' | 'low'
 */
export function detectPerformanceTier(): 'high' | 'medium' | 'low' {
    const webgl = detectWebGLSupport();

    // Check for high-end indicators
    const isHighEnd =
        webgl.webgl2 &&
        webgl.maxTextureSize >= 8192 &&
        webgl.precision === 'highp' &&
        navigator.hardwareConcurrency >= 8;

    // Check for low-end indicators
    const isLowEnd =
        !webgl.webgl2 ||
        webgl.maxTextureSize < 4096 ||
        navigator.hardwareConcurrency < 4;

    if (isHighEnd) return 'high';
    if (isLowEnd) return 'low';
    return 'medium';
}

/**
 * Generate a unique ID
 * @param prefix - Optional prefix for the ID
 * @returns Unique string ID
 */
export function generateId(prefix: string = 'id'): string {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Debounce a function
 * @param fn - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
    fn: T,
    delay: number
): (...args: Parameters<T>) => void {
    let timeoutId: ReturnType<typeof setTimeout>;
    return (...args: Parameters<T>) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
    };
}

/**
 * Throttle a function
 * @param fn - Function to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: unknown[]) => unknown>(
    fn: T,
    limit: number
): (...args: Parameters<T>) => void {
    let inThrottle: boolean;
    return (...args: Parameters<T>) => {
        if (!inThrottle) {
            fn(...args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}

/**
 * Deep clone an object (simple implementation)
 * @param obj - Object to clone
 * @returns Cloned object
 */
export function deepClone<T>(obj: T): T {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Calculate luminance of a color (perceived brightness)
 * @param color - RGB color
 * @returns Luminance value 0-1
 */
export function calculateLuminance(color: Color): number {
    // Using relative luminance formula (ITU-R BT.709)
    return 0.2126 * color.r + 0.7152 * color.g + 0.0722 * color.b;
}

/**
 * Determine if a color is light or dark
 * @param color - RGB color
 * @returns 'light' or 'dark'
 */
export function isColorLight(color: Color): boolean {
    return calculateLuminance(color) > 0.5;
}

/**
 * Get contrasting text color for a background color
 * @param backgroundColor - Background color
 * @returns Black or white color for text
 */
export function getContrastColor(backgroundColor: Color): Color {
    return isColorLight(backgroundColor)
        ? { r: 0, g: 0, b: 0 } // Black text for light backgrounds
        : { r: 1, g: 1, b: 1 }; // White text for dark backgrounds
}
