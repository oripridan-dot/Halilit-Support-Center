/**
 * Three.js 3D Environment Component
 * React wrapper for 3D product visualization
 *
 * Path: frontend/src/components/views/ThreeDEnvironment.tsx
 *
 * Usage:
 *   <ThreeDEnvironment
 *     product={product}
 *     autoRotate={true}
 *     onLoaded={() => console.log('ready')}
 *   />
 */

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { ThreeSceneManager } from "../../lib/threeSceneManager";
import { ProductModelLoader } from "../../lib/productModelLoader";

export interface ThreeDEnvironmentProps {
  /** Product data object */
  product: {
    id: string;
    name?: string;
    category?: string;
    main_category?: string;
    brand?: string;
    brand_color?: string;
    [key: string]: any;
  };
  /** Brand color override */
  brandColor?: string;
  /** Container width */
  width?: number;
  /** Container height */
  height?: number;
  /** Auto-rotate the model */
  autoRotate?: boolean;
  /** Rotation speed (radians per frame) */
  rotationSpeed?: number;
  /** Include ground plane */
  showGround?: boolean;
  /** Callback when ready */
  onLoaded?: () => void;
  /** CSS class name */
  className?: string;
}

/**
 * ThreeDEnvironment Component
 * Renders a 3D product model with theatrical lighting
 */
export const ThreeDEnvironment: React.FC<ThreeDEnvironmentProps> = ({
  product,
  brandColor = "#888888",
  width = 800,
  height = 600,
  autoRotate = true,
  rotationSpeed = 0.005,
  showGround = true,
  onLoaded,
  className = "",
}) => {
  // === REFS ===
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneManagerRef = useRef<ThreeSceneManager | null>(null);
  const modelLoaderRef = useRef<ProductModelLoader | null>(null);
  const productMeshRef = useRef<THREE.Mesh | null>(null);
  const rotationRefRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // === STATE ===
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // === INITIALIZATION ===
  useEffect(() => {
    if (!containerRef.current) {
      setError("Container not found");
      return;
    }

    const initScene = async () => {
      try {
        // Create scene manager
        const sceneManager = new ThreeSceneManager(
          containerRef.current!,
          width,
          height,
        );
        sceneManagerRef.current = sceneManager;

        // Create model loader
        const modelLoader = new ProductModelLoader(sceneManager);
        modelLoaderRef.current = modelLoader;

        // Add ground plane if requested
        if (showGround) {
          const ground = modelLoader.createGroundPlane(20, 0x1a1a2e);
          sceneManager.addObject(ground);
        }

        // Load product model
        const model = await modelLoader.loadProductModel(product.id, product);
        sceneManager.addObject(model.mesh);
        productMeshRef.current = model.mesh;

        setIsLoading(false);
        onLoaded?.();

        console.log(
          `✅ ThreeDEnvironment ready: ${product.name || product.id}`,
        );
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        setError(errorMsg);
        console.error("❌ ThreeDEnvironment failed:", err);
      }
    };

    initScene();

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
    };
  }, [product.id, width, height, showGround, onLoaded]);

  // === AUTO-ROTATE ===
  useEffect(() => {
    if (!autoRotate || !productMeshRef.current) return;

    // Clear existing rotation if any
    if (rotationRefRef.current) {
      clearInterval(rotationRefRef.current);
    }

    // Setup rotation loop
    rotationRefRef.current = setInterval(() => {
      if (productMeshRef.current) {
        productMeshRef.current.rotation.y += rotationSpeed;
      }
    }, 16); // ~60fps

    return () => {
      if (rotationRefRef.current) {
        clearInterval(rotationRefRef.current);
      }
    };
  }, [autoRotate, rotationSpeed]);

  // === WINDOW RESIZE ===
  useEffect(() => {
    const handleResize = () => {
      if (!containerRef.current || !sceneManagerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      sceneManagerRef.current.resize(rect.width, rect.height);
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // === RENDER ===
  return (
    <div
      ref={containerRef}
      className={`relative w-full bg-slate-950 rounded-lg overflow-hidden ${className}`}
      style={{
        width: width ? `${width}px` : "100%",
        height: height ? `${height}px` : "100%",
        minHeight: "300px",
      }}
    >
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="text-center">
            <div className="inline-block">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <p className="text-white text-sm mt-3">Loading 3D model...</p>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-950/50 backdrop-blur-sm">
          <div className="text-center px-4">
            <p className="text-red-200 text-sm">⚠️ Failed to load 3D model</p>
            <p className="text-red-100 text-xs mt-2 opacity-75">{error}</p>
          </div>
        </div>
      )}

      {/* Info Overlay (Bottom) */}
      {!isLoading && !error && (
        <div className="absolute bottom-4 left-4 right-4 text-xs text-slate-300 pointer-events-none">
          <p className="opacity-50">{product.name || "Product"}</p>
        </div>
      )}

      {/* Help Text */}
      {!isLoading && !error && (
        <div className="absolute top-4 left-4 text-xs text-slate-400 pointer-events-none">
          <p className="opacity-50">Drag to rotate • Scroll to zoom</p>
        </div>
      )}
    </div>
  );
};

// Export displayName for debugging
ThreeDEnvironment.displayName = "ThreeDEnvironment";
