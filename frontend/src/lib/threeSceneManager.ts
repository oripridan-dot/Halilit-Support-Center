/**
 * Three.js Scene Manager
 * Handles 3D scene initialization, camera, renderer, and lighting
 * 
 * Path: frontend/src/lib/threeSceneManager.ts
 * 
 * Usage:
 *   const sceneManager = new ThreeSceneManager(container, 800, 600);
 *   sceneManager.addObject(mesh);
 *   // ... render loop handled automatically
 *   sceneManager.dispose(); // on cleanup
 */

import * as THREE from 'three';

export interface SceneConfig {
    backgroundColor?: number;
    fogNear?: number;
    fogFar?: number;
    cameraPosition?: { x: number; y: number; z: number };
    cameraFOV?: number;
}

export class ThreeSceneManager {
    private scene: THREE.Scene;
    private camera: THREE.PerspectiveCamera;
    private renderer: THREE.WebGLRenderer;
    private animationId: number = 0;
    private lights: Map<string, THREE.Light> = new Map();
    private config: Required<SceneConfig>;
    private isRunning: boolean = true;

    // Default configuration (Theatrical lighting setup)
    private readonly defaultConfig: Required<SceneConfig> = {
        backgroundColor: 0x0a0e27,
        fogNear: 100,
        fogFar: 500,
        cameraPosition: { x: 0, y: 2, z: 5 },
        cameraFOV: 75
    };

    constructor(
        container: HTMLElement,
        width: number,
        height: number,
        config?: SceneConfig
    ) {
        this.config = { ...this.defaultConfig, ...config };

        // === SCENE SETUP ===
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.config.backgroundColor);
        this.scene.fog = new THREE.Fog(
            this.config.backgroundColor,
            this.config.fogNear,
            this.config.fogFar
        );

        // === CAMERA SETUP ===
        this.camera = new THREE.PerspectiveCamera(
            this.config.cameraFOV,
            width / height,
            0.1,
            1000
        );
        this.camera.position.set(
            this.config.cameraPosition.x,
            this.config.cameraPosition.y,
            this.config.cameraPosition.z
        );

        // === RENDERER SETUP ===
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(width, height);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        container.appendChild(this.renderer.domElement);

        // === LIGHTING SETUP ===
        this.setupTheatricalLighting();

        // === START RENDER LOOP ===
        this.animate();

        console.log('✅ ThreeSceneManager initialized', {
            width,
            height,
            pixelRatio: window.devicePixelRatio,
            lights: this.lights.size
        });
    }

    /**
     * Setup theatrical lighting (3-point lighting + ambient)
     * Matches the design system in 04_DESIGN_SYSTEM.md
     */
    private setupTheatricalLighting() {
        // ===== KEY LIGHT (Main illumination from 175°) =====
        // This is the primary light source creating sharp god's beams
        const keyLight = new THREE.DirectionalLight(0xffffff, 0.8);
        keyLight.position.set(8, 6, -3);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        keyLight.shadow.camera.near = 0.1;
        keyLight.shadow.camera.far = 100;
        keyLight.shadow.camera.left = -20;
        keyLight.shadow.camera.right = 20;
        keyLight.shadow.camera.top = 20;
        keyLight.shadow.camera.bottom = -20;
        this.scene.add(keyLight);
        this.lights.set('key', keyLight);

        // ===== FILL LIGHT (Secondary, opposite side) =====
        // Softens shadows and adds blue color accent
        const fillLight = new THREE.DirectionalLight(0x4a90e2, 0.4);
        fillLight.position.set(-8, 4, 3);
        this.scene.add(fillLight);
        this.lights.set('fill', fillLight);

        // ===== RIM LIGHT (Separation/edge lighting) =====
        // Creates dramatic orange rim around objects
        const rimLight = new THREE.DirectionalLight(0xff6b35, 0.3);
        rimLight.position.set(0, 3, -8);
        this.scene.add(rimLight);
        this.lights.set('rim', rimLight);

        // ===== AMBIENT LIGHT (Overall visibility) =====
        // Low intensity to maintain contrast
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.3);
        this.scene.add(ambientLight);
        this.lights.set('ambient', ambientLight);
    }

    /**
     * Add object to scene (automatically receives shadows)
     */
    public addObject(object: THREE.Object3D) {
        this.scene.add(object);
        // Enable shadows on all meshes
        object.traverse((child) => {
            if (child instanceof THREE.Mesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
    }

    /**
     * Remove object from scene
     */
    public removeObject(object: THREE.Object3D) {
        this.scene.remove(object);
    }

    /**
     * Get scene reference (for advanced operations)
     */
    public getScene(): THREE.Scene {
        return this.scene;
    }

    /**
     * Get camera reference (for controls)
     */
    public getCamera(): THREE.PerspectiveCamera {
        return this.camera;
    }

    /**
     * Get renderer reference
     */
    public getRenderer(): THREE.WebGLRenderer {
        return this.renderer;
    }

    /**
     * Get light by name ('key', 'fill', 'rim', 'ambient')
     */
    public getLight(name: string): THREE.Light | undefined {
        return this.lights.get(name);
    }

    /**
     * Update light intensity
     */
    public setLightIntensity(name: string, intensity: number) {
        const light = this.lights.get(name);
        if (light) {
            light.intensity = intensity;
        }
    }

    /**
     * Animation loop (automatically called)
     */
    private animate = () => {
        if (!this.isRunning) return;
        this.animationId = requestAnimationFrame(this.animate);
        this.renderer.render(this.scene, this.camera);
    };

    /**
     * Stop render loop and cleanup
     */
    public dispose() {
        this.isRunning = false;
        cancelAnimationFrame(this.animationId);

        // Dispose geometries and materials
        this.scene.traverse((object) => {
            if (object instanceof THREE.Mesh) {
                object.geometry.dispose();
                if (Array.isArray(object.material)) {
                    object.material.forEach((mat) => mat.dispose());
                } else {
                    object.material.dispose();
                }
            }
        });

        // Dispose lights
        this.lights.forEach((light) => {
            if (light instanceof THREE.Light) {
                light.dispose?.();
            }
        });

        // Dispose renderer
        this.renderer.dispose();
        this.renderer.domElement.remove();

        console.log('✅ ThreeSceneManager disposed');
    }

    /**
     * Handle window resize
     */
    public resize(width: number, height: number) {
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * Set camera position (for product focus)
     */
    public setCameraPosition(x: number, y: number, z: number) {
        this.camera.position.set(x, y, z);
    }

    /**
     * Look at target (for camera control)
     */
    public lookAt(x: number, y: number, z: number) {
        this.camera.lookAt(x, y, z);
    }

    /**
     * Get current canvas element
     */
    public getCanvas(): HTMLCanvasElement {
        return this.renderer.domElement;
    }

    /**
     * Clear scene of all objects (keeping lights)
     */
    public clearObjects() {
        this.scene.children.forEach((child) => {
            if (!this.lights.has(child.uuid)) {
                this.scene.remove(child);
            }
        });
    }
}
