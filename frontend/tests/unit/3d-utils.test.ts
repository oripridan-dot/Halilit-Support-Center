/**
 * Unit Tests for 3D Utility Functions
 * Tests color conversion, vector math, and helper functions
 */

import { describe, it, expect } from 'vitest';
import {
    hexToRGB,
    rgbToHex,
    lerpVector3,
    lerpColor,
    distanceVector3,
    normalizeVector3,
    isPointInBox,
    getBoundingBoxCenter,
    getBoundingBoxSize,
    formatBytes,
    formatDuration,
    clamp,
    mapRange,
    easing,
    detectWebGLSupport,
    calculateLuminance,
    isColorLight,
    getContrastColor
} from '@/lib/3d/utils';
import type { Vector3, Color, BoundingBox } from '@/lib/3d/environment3d.types';

describe('Color Conversion', () => {
    it('converts hex to RGB correctly', () => {
        expect(hexToRGB('#FF0000')).toEqual({ r: 1, g: 0, b: 0 });
        expect(hexToRGB('#00FF00')).toEqual({ r: 0, g: 1, b: 0 });
        expect(hexToRGB('#0000FF')).toEqual({ r: 0, g: 0, b: 1 });
        expect(hexToRGB('#FFFFFF')).toEqual({ r: 1, g: 1, b: 1 });
        expect(hexToRGB('#000000')).toEqual({ r: 0, g: 0, b: 0 });
    });

    it('handles hex without # prefix', () => {
        expect(hexToRGB('FF0000')).toEqual({ r: 1, g: 0, b: 0 });
    });

    it('converts RGB to hex correctly', () => {
        expect(rgbToHex({ r: 1, g: 0, b: 0 })).toBe('#ff0000');
        expect(rgbToHex({ r: 0, g: 1, b: 0 })).toBe('#00ff00');
        expect(rgbToHex({ r: 0, g: 0, b: 1 })).toBe('#0000ff');
        expect(rgbToHex({ r: 1, g: 1, b: 1 })).toBe('#ffffff');
        expect(rgbToHex({ r: 0, g: 0, b: 0 })).toBe('#000000');
    });

    it('handles fractional RGB values', () => {
        expect(rgbToHex({ r: 0.5, g: 0.5, b: 0.5 })).toBe('#808080');
    });
});

describe('Vector Math', () => {
    it('interpolates between vectors', () => {
        const start: Vector3 = { x: 0, y: 0, z: 0 };
        const end: Vector3 = { x: 10, y: 10, z: 10 };

        expect(lerpVector3(start, end, 0)).toEqual({ x: 0, y: 0, z: 0 });
        expect(lerpVector3(start, end, 0.5)).toEqual({ x: 5, y: 5, z: 5 });
        expect(lerpVector3(start, end, 1)).toEqual({ x: 10, y: 10, z: 10 });
    });

    it('calculates distance correctly', () => {
        const a: Vector3 = { x: 0, y: 0, z: 0 };
        const b: Vector3 = { x: 3, y: 4, z: 0 };

        expect(distanceVector3(a, b)).toBe(5);
    });

    it('normalizes vectors', () => {
        const v: Vector3 = { x: 3, y: 4, z: 0 };
        const normalized = normalizeVector3(v);

        expect(normalized.x).toBeCloseTo(0.6);
        expect(normalized.y).toBeCloseTo(0.8);
        expect(normalized.z).toBe(0);
    });

    it('handles zero vector normalization', () => {
        const zero: Vector3 = { x: 0, y: 0, z: 0 };
        expect(normalizeVector3(zero)).toEqual({ x: 0, y: 0, z: 0 });
    });
});

describe('Color Interpolation', () => {
    it('interpolates between colors', () => {
        const red: Color = { r: 1, g: 0, b: 0 };
        const blue: Color = { r: 0, g: 0, b: 1 };

        const mid = lerpColor(red, blue, 0.5);
        expect(mid.r).toBe(0.5);
        expect(mid.g).toBe(0);
        expect(mid.b).toBe(0.5);
    });

    it('handles alpha channel', () => {
        const transparent: Color = { r: 1, g: 1, b: 1, a: 0 };
        const opaque: Color = { r: 1, g: 1, b: 1, a: 1 };

        const mid = lerpColor(transparent, opaque, 0.5);
        expect(mid.a).toBe(0.5);
    });
});

describe('Bounding Box Operations', () => {
    const box: BoundingBox = {
        min: { x: -5, y: -5, z: -5 },
        max: { x: 5, y: 5, z: 5 }
    };

    it('checks if point is inside box', () => {
        expect(isPointInBox({ x: 0, y: 0, z: 0 }, box)).toBe(true);
        expect(isPointInBox({ x: 6, y: 0, z: 0 }, box)).toBe(false);
        expect(isPointInBox({ x: -5, y: -5, z: -5 }, box)).toBe(true);
        expect(isPointInBox({ x: 5, y: 5, z: 5 }, box)).toBe(true);
    });

    it('calculates box center', () => {
        expect(getBoundingBoxCenter(box)).toEqual({ x: 0, y: 0, z: 0 });
    });

    it('calculates box size', () => {
        expect(getBoundingBoxSize(box)).toEqual({ x: 10, y: 10, z: 10 });
    });
});

describe('Formatting Utilities', () => {
    it('formats bytes correctly', () => {
        expect(formatBytes(0)).toBe('0 Bytes');
        expect(formatBytes(1024)).toBe('1 KB');
        expect(formatBytes(1024 * 1024)).toBe('1 MB');
        expect(formatBytes(1536 * 1024)).toBe('1.5 MB');
        expect(formatBytes(1024 * 1024 * 1024)).toBe('1 GB');
    });

    it('formats duration correctly', () => {
        expect(formatDuration(500)).toBe('500ms');
        expect(formatDuration(1500)).toBe('1.5s');
        expect(formatDuration(65000)).toBe('1m 5s');
        expect(formatDuration(125000)).toBe('2m 5s');
    });
});

describe('Math Utilities', () => {
    it('clamps values', () => {
        expect(clamp(5, 0, 10)).toBe(5);
        expect(clamp(-5, 0, 10)).toBe(0);
        expect(clamp(15, 0, 10)).toBe(10);
    });

    it('maps ranges', () => {
        expect(mapRange(5, 0, 10, 0, 100)).toBe(50);
        expect(mapRange(0, 0, 10, 0, 100)).toBe(0);
        expect(mapRange(10, 0, 10, 0, 100)).toBe(100);
        expect(mapRange(2.5, 0, 10, 0, 1)).toBeCloseTo(0.25);
    });
});

describe('Easing Functions', () => {
    it('linear easing works', () => {
        expect(easing.linear(0)).toBe(0);
        expect(easing.linear(0.5)).toBe(0.5);
        expect(easing.linear(1)).toBe(1);
    });

    it('easeIn is slower at start', () => {
        const mid = easing.easeIn(0.5);
        expect(mid).toBeLessThan(0.5);
    });

    it('easeOut is slower at end', () => {
        const mid = easing.easeOut(0.5);
        expect(mid).toBeGreaterThan(0.5);
    });

    it('easeInOut is symmetric', () => {
        const quarterIn = easing.easeInOut(0.25);
        const quarterOut = easing.easeInOut(0.75);
        expect(quarterIn).toBeCloseTo(1 - quarterOut);
    });
});

describe('WebGL Detection', () => {
    it('detects WebGL support', () => {
        const support = detectWebGLSupport();

        expect(typeof support.webgl).toBe('boolean');
        expect(typeof support.webgl2).toBe('boolean');
        expect(typeof support.maxTextureSize).toBe('number');
        expect(typeof support.precision).toBe('string');
    });

    it('returns valid precision values', () => {
        const support = detectWebGLSupport();
        const validPrecisions = ['highp', 'mediump', 'lowp', 'unknown'];
        expect(validPrecisions).toContain(support.precision);
    });
});

describe('Color Luminance', () => {
    it('calculates luminance correctly', () => {
        expect(calculateLuminance({ r: 0, g: 0, b: 0 })).toBe(0);
        expect(calculateLuminance({ r: 1, g: 1, b: 1 })).toBe(1);

        // Green should have higher luminance than red/blue
        const redLum = calculateLuminance({ r: 1, g: 0, b: 0 });
        const greenLum = calculateLuminance({ r: 0, g: 1, b: 0 });
        const blueLum = calculateLuminance({ r: 0, g: 0, b: 1 });

        expect(greenLum).toBeGreaterThan(redLum);
        expect(greenLum).toBeGreaterThan(blueLum);
    });

    it('identifies light colors', () => {
        expect(isColorLight({ r: 1, g: 1, b: 1 })).toBe(true);  // White
        expect(isColorLight({ r: 0, g: 0, b: 0 })).toBe(false); // Black
        expect(isColorLight({ r: 0.9, g: 0.9, b: 0.9 })).toBe(true);
        expect(isColorLight({ r: 0.1, g: 0.1, b: 0.1 })).toBe(false);
    });

    it('provides contrasting colors', () => {
        const whiteContrast = getContrastColor({ r: 1, g: 1, b: 1 });
        expect(whiteContrast.r).toBe(0); // Should return black for white bg

        const blackContrast = getContrastColor({ r: 0, g: 0, b: 0 });
        expect(blackContrast.r).toBe(1); // Should return white for black bg
    });
});

describe('Edge Cases', () => {
    it('handles negative values in clamp', () => {
        expect(clamp(-100, -50, 50)).toBe(-50);
    });

    it('handles very large numbers in formatBytes', () => {
        const result = formatBytes(Math.pow(1024, 3) * 1.5);
        expect(result).toContain('GB');
    });

    it('handles zero distance', () => {
        const a: Vector3 = { x: 0, y: 0, z: 0 };
        expect(distanceVector3(a, a)).toBe(0);
    });
});
