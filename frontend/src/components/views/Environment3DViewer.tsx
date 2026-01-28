/**
 * Environment3DViewer - React Component
 * Seamless integration of 3D environments into the Halilit Support Center UI
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { Environment3DRenderer } from './Environment3DRenderer';
import type { Environment3D, LoadProgress, PerformanceMetrics } from './environment3d.types';
import { getEnvironmentBySubcategory } from './environment-config';

// ============================================================================
// TYPES
// ============================================================================

interface Environment3DViewerProps {
  subcategoryId: string;
  brandIds?: string[];  // Filter products by brands
  autoRotate?: boolean;
  onProductClick?: (productData: any) => void;
  onLoadComplete?: () => void;
  onLoadError?: (error: Error) => void;
  className?: string;
  showPerformanceStats?: boolean;
}

interface ViewerState {
  isLoading: boolean;
  loadProgress: number;
  isInitialized: boolean;
  error: Error | null;
  performanceMetrics: PerformanceMetrics | null;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const Environment3DViewer: React.FC<Environment3DViewerProps> = ({
  subcategoryId,
  brandIds,
  autoRotate = false,
  onProductClick,
  onLoadComplete,
  onLoadError,
  className = '',
  showPerformanceStats = false
}) => {
  // Refs
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<Environment3DRenderer | null>(null);

  // State
  const [state, setState] = useState<ViewerState>({
    isLoading: true,
    loadProgress: 0,
    isInitialized: false,
    error: null,
    performanceMetrics: null
  });

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  useEffect(() => {
    if (!containerRef.current) return;

    // Get environment configuration
    const environment = getEnvironmentBySubcategory(subcategoryId);
    if (!environment) {
      const error = new Error(`Environment not found for subcategory: ${subcategoryId}`);
      setState(prev => ({ ...prev, error, isLoading: false }));
      onLoadError?.(error);
      return;
    }

    // Filter environment by brands if specified
    const filteredEnvironment = brandIds 
      ? filterEnvironmentByBrands(environment, brandIds)
      : environment;

    // Create renderer
    const renderer = new Environment3DRenderer(containerRef.current, filteredEnvironment);
    rendererRef.current = renderer;

    // Initialize with progress tracking
    renderer.initialize((progress) => {
      setState(prev => ({
        ...prev,
        loadProgress: progress.percentage
      }));
    })
      .then(() => {
        setState(prev => ({
          ...prev,
          isLoading: false,
          isInitialized: true,
          error: null
        }));
        
        renderer.startAnimation();
        onLoadComplete?.();
      })
      .catch((error) => {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: error as Error
        }));
        onLoadError?.(error as Error);
      });

    // Setup product click listener
    const handleProductClick = (event: CustomEvent) => {
      onProductClick?.(event.detail);
    };
    window.addEventListener('environment3d:product-click', handleProductClick as EventListener);

    // Performance monitoring (if enabled)
    let perfInterval: number | undefined;
    if (showPerformanceStats) {
      perfInterval = window.setInterval(() => {
        if (renderer) {
          setState(prev => ({
            ...prev,
            performanceMetrics: renderer.getPerformanceMetrics()
          }));
        }
      }, 1000);
    }

    // Cleanup
    return () => {
      window.removeEventListener('environment3d:product-click', handleProductClick as EventListener);
      if (perfInterval) clearInterval(perfInterval);
      renderer.dispose();
    };
  }, [subcategoryId, brandIds, onProductClick, onLoadComplete, onLoadError, showPerformanceStats]);

  // ============================================================================
  // CAMERA CONTROLS
  // ============================================================================

  const setCameraPreset = useCallback((presetName: string) => {
    rendererRef.current?.setCameraPreset(presetName);
  }, []);

  const focusOnProduct = useCallback((productId: string) => {
    rendererRef.current?.focusOnProduct(productId);
  }, []);

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className={`environment-3d-viewer ${className}`} style={{ position: 'relative', width: '100%', height: '100%' }}>
      {/* 3D Canvas Container */}
      <div
        ref={containerRef}
        className="environment-3d-canvas"
        style={{
          width: '100%',
          height: '100%',
          position: 'absolute',
          top: 0,
          left: 0
        }}
      />

      {/* Loading Overlay */}
      {state.isLoading && (
        <div className="environment-3d-loading" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0, 0, 0, 0.8)',
          zIndex: 10
        }}>
          <div style={{ color: 'white', fontSize: '1.5rem', marginBottom: '1rem' }}>
            Loading Environment...
          </div>
          <div style={{
            width: '300px',
            height: '4px',
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '2px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${state.loadProgress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #4F46E5, #7C3AED)',
              transition: 'width 0.3s ease'
            }} />
          </div>
          <div style={{ color: 'rgba(255, 255, 255, 0.7)', marginTop: '0.5rem', fontSize: '0.875rem' }}>
            {Math.round(state.loadProgress)}%
          </div>
        </div>
      )}

      {/* Error Overlay */}
      {state.error && (
        <div className="environment-3d-error" style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(0, 0, 0, 0.9)',
          zIndex: 10,
          padding: '2rem'
        }}>
          <div style={{ color: '#EF4444', fontSize: '1.5rem', marginBottom: '1rem' }}>
            Failed to Load Environment
          </div>
          <div style={{ color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', maxWidth: '500px' }}>
            {state.error.message}
          </div>
        </div>
      )}

      {/* Performance Stats */}
      {showPerformanceStats && state.performanceMetrics && (
        <div className="environment-3d-stats" style={{
          position: 'absolute',
          top: '1rem',
          right: '1rem',
          background: 'rgba(0, 0, 0, 0.7)',
          color: 'white',
          padding: '1rem',
          borderRadius: '0.5rem',
          fontFamily: 'monospace',
          fontSize: '0.75rem',
          zIndex: 5,
          minWidth: '200px'
        }}>
          <div>FPS: {Math.round(state.performanceMetrics.currentFPS)}</div>
          <div>Polygons: {state.performanceMetrics.polyCount.toLocaleString()}</div>
          <div>Draw Calls: {state.performanceMetrics.drawCalls}</div>
          <div>Textures: {state.performanceMetrics.textureMemory}</div>
          <div>Load Time: {state.performanceMetrics.loadTime.toFixed(2)}s</div>
        </div>
      )}

      {/* Camera Presets (Example UI) */}
      {state.isInitialized && (
        <div className="environment-3d-controls" style={{
          position: 'absolute',
          bottom: '1rem',
          left: '50%',
          transform: 'translateX(-50%)',
          display: 'flex',
          gap: '0.5rem',
          zIndex: 5
        }}>
          <button
            onClick={() => setCameraPreset('default')}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(0, 0, 0, 0.7)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Default View
          </button>
          <button
            onClick={() => setCameraPreset('wide')}
            style={{
              padding: '0.5rem 1rem',
              background: 'rgba(0, 0, 0, 0.7)',
              color: 'white',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '0.25rem',
              cursor: 'pointer',
              fontSize: '0.875rem'
            }}
          >
            Wide View
          </button>
        </div>
      )}
    </div>
  );
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Filter environment to only show products from specified brands
 */
function filterEnvironmentByBrands(
  environment: Environment3D,
  brandIds: string[]
): Environment3D {
  const filtered = { ...environment };

  // Filter hero layer elements
  filtered.scene.layers.hero.elements = environment.scene.layers.hero.elements.filter(
    element => {
      if (!element.metadata.brandId) return true;
      return brandIds.includes(element.metadata.brandId);
    }
  );

  // Filter brand colors
  filtered.brandColors.brands = environment.brandColors.brands.filter(
    brand => brandIds.includes(brand.id)
  );

  // Filter brand lights
  filtered.lighting.brandLights = environment.lighting.brandLights.filter(
    light => brandIds.includes(light.brandId)
  );

  return filtered;
}

// ============================================================================
// HOOK FOR PROGRAMMATIC CONTROL
// ============================================================================

export interface Environment3DControls {
  setCameraPreset: (presetName: string) => void;
  focusOnProduct: (productId: string) => void;
  getPerformanceMetrics: () => PerformanceMetrics | null;
}

export function useEnvironment3D(
  viewerRef: React.RefObject<Environment3DViewer>
): Environment3DControls {
  const setCameraPreset = useCallback((presetName: string) => {
    // Access internal renderer through ref (would need to expose this)
    console.log('Set camera preset:', presetName);
  }, [viewerRef]);

  const focusOnProduct = useCallback((productId: string) => {
    console.log('Focus on product:', productId);
  }, [viewerRef]);

  const getPerformanceMetrics = useCallback(() => {
    return null;
  }, [viewerRef]);

  return {
    setCameraPreset,
    focusOnProduct,
    getPerformanceMetrics
  };
}

// ============================================================================
// EXAMPLE USAGE IN GALAXY DASHBOARD
// ============================================================================

export const Example_GalaxyDashboardIntegration: React.FC = () => {
  const [selectedSubcategory, setSelectedSubcategory] = useState<string>('electric-guitars');
  const [selectedBrands, setSelectedBrands] = useState<string[]>(['fender', 'gibson']);

  const handleProductClick = (productData: any) => {
    console.log('Product clicked:', productData);
    // Open product detail modal, navigate to product page, etc.
  };

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      {/* Left Panel - Category Selection */}
      <div style={{ width: '300px', background: '#111', padding: '1rem' }}>
        <h2 style={{ color: 'white', marginBottom: '1rem' }}>Categories</h2>
        <button 
          onClick={() => setSelectedSubcategory('electric-guitars')}
          style={{ 
            width: '100%', 
            padding: '0.75rem', 
            marginBottom: '0.5rem',
            background: selectedSubcategory === 'electric-guitars' ? '#4F46E5' : '#222',
            color: 'white',
            border: 'none',
            borderRadius: '0.25rem',
            cursor: 'pointer'
          }}
        >
          Electric Guitars
        </button>
        <button 
          onClick={() => setSelectedSubcategory('acoustic-guitars')}
          style={{ 
            width: '100%', 
            padding: '0.75rem',
            background: selectedSubcategory === 'acoustic-guitars' ? '#4F46E5' : '#222',
            color: 'white',
            border: 'none',
            borderRadius: '0.25rem',
            cursor: 'pointer'
          }}
        >
          Acoustic Guitars
        </button>
      </div>

      {/* Main Panel - 3D Environment */}
      <div style={{ flex: 1, background: '#000' }}>
        <Environment3DViewer
          subcategoryId={selectedSubcategory}
          brandIds={selectedBrands}
          onProductClick={handleProductClick}
          showPerformanceStats={true}
        />
      </div>
    </div>
  );
};
