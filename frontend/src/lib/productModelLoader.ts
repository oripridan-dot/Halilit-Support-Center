/**
 * Product Model Loader
 * Converts product metadata into 3D models
 * 
 * Path: frontend/src/lib/productModelLoader.ts
 * 
 * Features:
 * - Procedural geometry generation based on category
 * - Material assignment from brand colors
 * - Model caching for performance
 * - Support for external glTF/FBX models (future)
 */

import * as THREE from 'three';
import { ThreeSceneManager } from './threeSceneManager';

export interface ProductModel {
    geometry: THREE.BufferGeometry;
    material: THREE.Material;
    mesh: THREE.Mesh;
}

interface BrandColorData {
    primary?: string;
    secondary?: string;
    accent?: string;
    metalness?: number;
    roughness?: number;
}

export class ProductModelLoader {
    private sceneManager: ThreeSceneManager;
    private modelCache: Map<string, ProductModel> = new Map();
    private brandColorCache: Map<string, BrandColorData> = new Map();

    constructor(sceneManager: ThreeSceneManager) {
        this.sceneManager = sceneManager;
        this.initializeBrandColors();
    }

    /**
     * Initialize brand color mapping from config
     */
    private initializeBrandColors() {
        // These match BRAND_THEMES in forge_backbone.py
        const themes = {
            roland: { primary: '#f89a1c', secondary: '#18181b', metalness: 0.8, roughness: 0.1 },
            boss: { primary: '#0055a4', secondary: '#0f172a', metalness: 0.6, roughness: 0.3 },
            nord: { primary: '#e31e24', secondary: '#450a0a', metalness: 0.7, roughness: 0.2 },
            moog: { primary: '#000000', secondary: '#5c4033', metalness: 0.4, roughness: 0.6 },
            'adam-audio': { primary: '#000000', secondary: '#1c1917', metalness: 0.5, roughness: 0.5 },
            'teenage-engineering': { primary: '#e5e5e5', secondary: '#ff4d00', metalness: 0.3, roughness: 0.7 },
            'universal-audio': { primary: '#1f2937', secondary: '#111827', metalness: 0.9, roughness: 0.05 },
            'akai-professional': { primary: '#ff0000', secondary: '#000000', metalness: 0.7, roughness: 0.2 },
            'warm-audio': { primary: '#ea580c', secondary: '#431407', metalness: 0.6, roughness: 0.3 },
            mackie: { primary: '#00a651', secondary: '#000000', metalness: 0.5, roughness: 0.4 }
        };

        Object.entries(themes).forEach(([brand, colors]) => {
            this.brandColorCache.set(brand, colors);
        });
    }

    /**
     * Load or create a 3D model for a product
     */
    public async loadProductModel(
        productId: string,
        productData: any
    ): Promise<ProductModel> {
        // === CACHE CHECK ===
        if (this.modelCache.has(productId)) {
            return this.modelCache.get(productId)!;
        }

        try {
            // === TRY: Load from external model file (glTF/FBX) ===
            // This will be implemented in next phase
            // For now, fall back to procedural geometry

            // === FALLBACK: Create procedural geometry ===
            const geometry = this.createGeometryForProduct(productData);
            const material = this.createMaterialForProduct(productData);
            const mesh = new THREE.Mesh(geometry, material);

            // === ENABLE SHADOWS ===
            mesh.castShadow = true;
            mesh.receiveShadow = true;

            // === CACHE MODEL ===
            const model: ProductModel = { geometry, material, mesh };
            this.modelCache.set(productId, model);

            console.log(`✅ Model loaded: ${productData.name || productId}`);
            return model;
        } catch (error) {
            console.error(`❌ Failed to load model for ${productId}:`, error);
            // Return a default fallback model
            return this.createFallbackModel();
        }
    }

    /**
     * Create procedural geometry based on category
     * This is a smart fallback that generates reasonable shapes
     */
    private createGeometryForProduct(productData: any): THREE.BufferGeometry {
        const category = (productData.category || productData.main_category || '').toLowerCase();
        const name = (productData.name || '').toLowerCase();

        // === KEYBOARDS / SYNTHS ===
        if (
            category.includes('keyboard') ||
            category.includes('synthesizer') ||
            category.includes('synth') ||
            category.includes('piano') ||
            category.includes('organ')
        ) {
            // 88-key piano proportions: 1500mm x 250mm x 150mm
            return new THREE.BoxGeometry(3.0, 0.5, 0.3);
        }

        // === DRUMS / PERCUSSION ===
        if (
            category.includes('drum') ||
            category.includes('percussion') ||
            category.includes('snare') ||
            category.includes('tom') ||
            category.includes('kick')
        ) {
            // Drum proportions: 400mm diameter x 250mm height
            return new THREE.CylinderGeometry(0.4, 0.4, 0.25, 32);
        }

        // === GUITARS / BASS ===
        if (
            category.includes('guitar') ||
            category.includes('bass') ||
            category.includes('stringed') ||
            category.includes('string') ||
            name.includes('strat') ||
            name.includes('telecaster') ||
            name.includes('les paul')
        ) {
            // Guitar proportions: 100mm x 1000mm x 50mm
            return new THREE.BoxGeometry(0.2, 1.0, 0.05);
        }

        // === SPEAKERS / MONITORS ===
        if (
            category.includes('speaker') ||
            category.includes('monitor') ||
            category.includes('studio') ||
            category.includes('audio')
        ) {
            // Studio monitor: 200mm x 250mm x 200mm
            return new THREE.BoxGeometry(0.4, 0.5, 0.4);
        }

        // === MICROPHONES ===
        if (category.includes('microphone') || category.includes('mic')) {
            // Mic: 50mm diameter x 150mm height
            const geometry = new THREE.CylinderGeometry(0.05, 0.06, 0.15, 16);
            return geometry;
        }

        // === CABLES / ACCESSORIES ===
        if (category.includes('cable') || category.includes('accessory')) {
            // Small box for generic accessories
            return new THREE.BoxGeometry(0.3, 0.2, 0.15);
        }

        // === DEFAULT: Generic Box ===
        return new THREE.BoxGeometry(1, 1, 1);
    }

    /**
     * Create material based on product brand and category
     */
    private createMaterialForProduct(productData: any): THREE.Material {
        const brandSlug = (productData.brand || '').toLowerCase().replace(/\s+/g, '-');
        const brandColor = this.brandColorCache.get(brandSlug);

        // Get primary color (hex string or default)
        let primaryColor: string | number = brandColor?.primary || '#888888';
        // Convert hex string to number if needed
        if (typeof primaryColor === 'string') {
            primaryColor = parseInt(primaryColor.replace('#', '0x'), 16);
        }

        // Material configuration
        const materialConfig = {
            color: primaryColor,
            metalness: brandColor?.metalness ?? 0.7,
            roughness: brandColor?.roughness ?? 0.2,
            emissive: 0x0a0e27,
            emissiveIntensity: 0.1,
            envMapIntensity: 1.0
        };

        const material = new THREE.MeshStandardMaterial(materialConfig);

        // Special handling for glossy/metallic brands
        if (brandSlug.includes('roland') || brandSlug.includes('universal')) {
            material.metalness = 0.85;
            material.roughness = 0.1;
        }

        // Special handling for matte/wood brands
        if (brandSlug.includes('moog') || brandSlug.includes('warm')) {
            material.metalness = 0.3;
            material.roughness = 0.8;
        }

        return material;
    }

    /**
     * Create a fallback model when loading fails
     */
    private createFallbackModel(): ProductModel {
        const geometry = new THREE.BoxGeometry(1, 1, 1);
        const material = new THREE.MeshStandardMaterial({
            color: 0x888888,
            metalness: 0.5,
            roughness: 0.5
        });
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        return { geometry, material, mesh };
    }

    /**
     * Remove a single model from cache and dispose
     */
    public removeModel(productId: string) {
        const model = this.modelCache.get(productId);
        if (model) {
            model.geometry.dispose();
            model.material.dispose();
            this.sceneManager.removeObject(model.mesh);
            this.modelCache.delete(productId);
            console.log(`🗑️  Model removed: ${productId}`);
        }
    }

    /**
     * Clear entire model cache (for memory management)
     */
    public clearCache() {
        this.modelCache.forEach((model) => {
            model.geometry.dispose();
            if (Array.isArray(model.material)) {
                model.material.forEach((mat) => mat.dispose());
            } else {
                model.material.dispose();
            }
        });
        this.modelCache.clear();
        console.log('🗑️  Model cache cleared');
    }

    /**
     * Get cache statistics
     */
    public getCacheStats() {
        return {
            modelCount: this.modelCache.size,
            brandColorsCount: this.brandColorCache.size
        };
    }

    /**
     * Pre-load models for multiple products (optimization)
     */
    public async preloadModels(productList: any[]): Promise<void> {
        const promises = productList.map((product) =>
            this.loadProductModel(product.id, product).catch((err) => {
                console.warn(`Failed to preload ${product.id}:`, err);
            })
        );

        await Promise.all(promises);
        console.log(`✅ Preloaded ${productList.length} models`);
    }

    /**
     * Create a simple ground plane for context
     */
    public createGroundPlane(size: number = 20, color: number = 0x1a1a2e): THREE.Mesh {
        const geometry = new THREE.PlaneGeometry(size, size);
        const material = new THREE.MeshStandardMaterial({
            color: color,
            metalness: 0.1,
            roughness: 0.9
        });

        const ground = new THREE.Mesh(geometry, material);
        ground.rotation.x = -Math.PI / 2;
        ground.receiveShadow = true;
        ground.position.y = -1;

        return ground;
    }
}
