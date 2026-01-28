/**
 * useThreeDScene Hook
 * Custom React hook for 3D scene lifecycle management
 * 
 * Path: frontend/src/hooks/useThreeDScene.ts
 * 
 * Usage:
 *   const { isReady, sceneManager, modelLoader } = useThreeDScene(containerRef);
 *   
 *   // Load model
 *   const model = await modelLoader?.loadProductModel(id, data);
 *   sceneManager?.addObject(model.mesh);
 */

import { useEffect, useRef, useState } from 'react';
import { ThreeSceneManager } from '../lib/threeSceneManager';
import { ProductModelLoader } from '../lib/productModelLoader';
import * as THREE from 'three';

export interface UseThreeDSceneResult {
    isReady: boolean;
    isError: boolean;
    error: string | null;
    sceneManager: ThreeSceneManager | null;
    modelLoader: ProductModelLoader | null;
    resize: (width: number, height: number) => void;
    dispose: () => void;
}

export interface UseThreeDSceneOptions {
    width?: number;
    height?: number;
    backgroundColor?: number;
    autoInitialize?: boolean;
}

/**
 * Hook for managing Three.js scene lifecycle in React
 */
export function useThreeDScene(
    containerRef: React.RefObject<HTMLDivElement>,
    options: UseThreeDSceneOptions = {}
): UseThreeDSceneResult {
    const {
        width = 800,
        height = 600,
        backgroundColor = 0x0a0e27,
        autoInitialize = true
    } = options;

    // === STATE ===
    const [isReady, setIsReady] = useState(false);
    const [isError, setIsError] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // === REFS ===
    const sceneManagerRef = useRef<ThreeSceneManager | null>(null);
    const modelLoaderRef = useRef<ProductModelLoader | null>(null);

    // === INITIALIZATION ===
    useEffect(() => {
        if (!autoInitialize) return;
        if (!containerRef.current) {
            setError('Container ref is not set');
            setIsError(true);
            return;
        }

        try {
            // Create scene manager
            const sceneManager = new ThreeSceneManager(
                containerRef.current,
                width,
                height,
                { backgroundColor }
            );
            sceneManagerRef.current = sceneManager;

            // Create model loader
            const modelLoader = new ProductModelLoader(sceneManager);
            modelLoaderRef.current = modelLoader;

            setIsReady(true);
            console.log('✅ useThreeDScene initialized');
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Unknown initialization error';
            setError(errorMsg);
            setIsError(true);
            console.error('❌ useThreeDScene initialization failed:', err);
        }

        // === CLEANUP ===
        return () => {
            if (sceneManagerRef.current) {
                sceneManagerRef.current.dispose();
                sceneManagerRef.current = null;
            }
            if (modelLoaderRef.current) {
                modelLoaderRef.current.clearCache();
                modelLoaderRef.current = null;
            }
            setIsReady(false);
        };
    }, [width, height, backgroundColor, autoInitialize]);

    // === RESIZE HANDLER ===
    const resize = (newWidth: number, newHeight: number) => {
        if (!sceneManagerRef.current) {
            console.warn('Scene manager not initialized');
            return;
        }
        sceneManagerRef.current.resize(newWidth, newHeight);
    };

    // === DISPOSE HANDLER ===
    const dispose = () => {
        if (sceneManagerRef.current) {
            sceneManagerRef.current.dispose();
            sceneManagerRef.current = null;
        }
        if (modelLoaderRef.current) {
            modelLoaderRef.current.clearCache();
            modelLoaderRef.current = null;
        }
        setIsReady(false);
    };

    return {
        isReady,
        isError,
        error,
        sceneManager: sceneManagerRef.current,
        modelLoader: modelLoaderRef.current,
        resize,
        dispose
    };
}

/**
 * Hook for auto-rotating a mesh
 */
export function useAutoRotate(
    meshRef: React.MutableRefObject<THREE.Mesh | null>,
    enabled: boolean = true,
    speed: number = 0.005
) {
    useEffect(() => {
        if (!enabled || !meshRef.current) return;

        const interval = setInterval(() => {
            if (meshRef.current) {
                meshRef.current.rotation.y += speed;
            }
        }, 16); // ~60fps

        return () => clearInterval(interval);
    }, [enabled, speed]);
}

/**
 * Hook for handling window resize
 */
export function useWindowResize(
    callback: (width: number, height: number) => void
) {
    useEffect(() => {
        const handleResize = () => {
            const width = window.innerWidth;
            const height = window.innerHeight;
            callback(width, height);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [callback]);
}

/**
 * Hook for managing model loading and caching
 */
export function useProductModel(
    modelLoader: ProductModelLoader | null,
    productId: string,
    productData: any
) {
    const [model, setModel] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!modelLoader) {
            setError('Model loader not initialized');
            return;
        }

        (async () => {
            try {
                setIsLoading(true);
                const loadedModel = await modelLoader.loadProductModel(
                    productId,
                    productData
                );
                setModel(loadedModel);
                setError(null);
            } catch (err) {
                const errorMsg = err instanceof Error ? err.message : 'Failed to load model';
                setError(errorMsg);
                console.error('Model loading error:', err);
            } finally {
                setIsLoading(false);
            }
        })();
    }, [modelLoader, productId, productData]);

    return { model, isLoading, error };
}
