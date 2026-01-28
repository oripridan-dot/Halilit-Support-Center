/**
 * Environment3DRenderer - Core Three.js Implementation
 * Halilit Support Center - Immersive 3D Visualization System
 * 
 * This class handles the complete lifecycle of 3D environment rendering:
 * - Scene management and layer orchestration
 * - Dynamic brand color integration
 * - Performance optimization and monitoring
 * - Asset loading and caching
 * - Post-processing effects
 * - User interaction handling
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader';
import { RGBELoader } from 'three/examples/jsm/loaders/RGBELoader';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';
import { SSAOPass } from 'three/examples/jsm/postprocessing/SSAOPass';
import { ShaderPass } from 'three/examples/jsm/postprocessing/ShaderPass';
import { FXAAShader } from 'three/examples/jsm/shaders/FXAAShader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

import type {
  Environment3D,
  SceneElement,
  BrandColorScheme,
  PerformanceMetrics,
  LoadProgress
} from './environment3d.types';

import { assetGenerator, AssetType } from './asset-generator';

// ============================================================================
// MAIN RENDERER CLASS
// ============================================================================

export class Environment3DRenderer {
  // Core Three.js objects
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera | THREE.OrthographicCamera;
  private renderer: THREE.WebGLRenderer;
  private composer: EffectComposer;
  private controls?: OrbitControls;

  // Scene organization
  private heroLayer: THREE.Group;
  private contextLayer: THREE.Group;
  private atmosphereLayer: THREE.Group;

  // Lighting system
  private lights: Map<string, THREE.Light>;
  private brandLights: Map<string, THREE.Light>;

  // Asset management
  private gltfLoader: GLTFLoader;
  private textureLoader: THREE.TextureLoader;
  private rgbeLoader: RGBELoader;
  private assetCache: Map<string, any>;

  // State management
  private environment: Environment3D;
  private isInitialized: boolean = false;
  private isAnimating: boolean = false;
  private animationId?: number;

  // Performance tracking
  private performanceMetrics: PerformanceMetrics;
  private clock: THREE.Clock;

  // Interaction
  private raycaster: THREE.Raycaster;
  private mouse: THREE.Vector2;
  private hoveredObject: THREE.Object3D | null = null;

  // ============================================================================
  // CONSTRUCTOR & INITIALIZATION
  // ============================================================================

  constructor(
    container: HTMLElement,
    environment: Environment3D
  ) {
    this.environment = environment;
    this.assetCache = new Map();
    this.lights = new Map();
    this.brandLights = new Map();
    this.clock = new THREE.Clock();
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();

    // Initialize performance metrics
    this.performanceMetrics = {
      currentFPS: 60,
      polyCount: 0,
      drawCalls: 0,
      textureMemory: 0,
      vramUsage: 0,
      loadTime: 0,
      timestamp: Date.now()
    };

    // Create scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x1a1a1a);

    // Create camera
    this.camera = this.createCamera(container);

    // Create renderer
    this.renderer = this.createRenderer(container);

    // Create composer for post-processing
    this.composer = new EffectComposer(this.renderer);

    // Create scene layers
    this.heroLayer = new THREE.Group();
    this.heroLayer.name = 'Hero Layer';
    this.scene.add(this.heroLayer);

    this.contextLayer = new THREE.Group();
    this.contextLayer.name = 'Context Layer';
    this.scene.add(this.contextLayer);

    this.atmosphereLayer = new THREE.Group();
    this.atmosphereLayer.name = 'Atmosphere Layer';
    this.scene.add(this.atmosphereLayer);

    // Initialize loaders
    this.setupLoaders();

    // Setup controls if enabled
    if (environment.camera.controls.enabled) {
      this.setupControls(container);
    }

    // Setup interaction handlers
    this.setupInteractionHandlers(container);

    // Handle window resize
    window.addEventListener('resize', () => this.handleResize(container));
  }

  // ============================================================================
  // SETUP METHODS
  // ============================================================================

  private createCamera(container: HTMLElement): THREE.PerspectiveCamera | THREE.OrthographicCamera {
    const aspect = container.clientWidth / container.clientHeight;
    const config = this.environment.camera.default;

    if (config.type === 'perspective') {
      const camera = new THREE.PerspectiveCamera(
        config.fov || 50,
        aspect,
        config.near,
        config.far
      );
      camera.position.set(config.position.x, config.position.y, config.position.z);
      camera.lookAt(config.target.x, config.target.y, config.target.z);
      return camera;
    } else {
      const frustumSize = 10;
      const camera = new THREE.OrthographicCamera(
        -frustumSize * aspect / 2,
        frustumSize * aspect / 2,
        frustumSize / 2,
        -frustumSize / 2,
        config.near,
        config.far
      );
      camera.position.set(config.position.x, config.position.y, config.position.z);
      camera.lookAt(config.target.x, config.target.y, config.target.z);
      return camera;
    }
  }

  private createRenderer(container: HTMLElement): THREE.WebGLRenderer {
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: false,
      powerPreference: 'high-performance'
    });

    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.0;
    renderer.shadowMap.enabled = this.environment.lighting.shadows.enabled;
    renderer.shadowMap.type = this.getShadowMapType();
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    container.appendChild(renderer.domElement);

    return renderer;
  }

  private getShadowMapType(): THREE.ShadowMapType {
    const shadowType = this.environment.lighting.shadows.type;
    switch (shadowType) {
      case 'pcf':
        return THREE.PCFShadowMap;
      case 'pcf_soft':
        return THREE.PCFSoftShadowMap;
      case 'vsm':
        return THREE.VSMShadowMap;
      default:
        return THREE.PCFSoftShadowMap;
    }
  }

  private setupLoaders(): void {
    // GLTF Loader with Draco compression support
    this.gltfLoader = new GLTFLoader();
    const dracoLoader = new DRACOLoader();
    dracoLoader.setDecoderPath('/draco/');
    this.gltfLoader.setDRACOLoader(dracoLoader);

    // Texture Loader
    this.textureLoader = new THREE.TextureLoader();

    // RGBE Loader for HDR environments
    this.rgbeLoader = new RGBELoader();
  }

  private setupControls(container: HTMLElement): void {
    if (this.camera instanceof THREE.PerspectiveCamera) {
      this.controls = new OrbitControls(this.camera, this.renderer.domElement);

      const restrictions = this.environment.camera.controls.restrictions;
      if (restrictions.minDistance) this.controls.minDistance = restrictions.minDistance;
      if (restrictions.maxDistance) this.controls.maxDistance = restrictions.maxDistance;
      if (restrictions.minPolarAngle) this.controls.minPolarAngle = restrictions.minPolarAngle;
      if (restrictions.maxPolarAngle) this.controls.maxPolarAngle = restrictions.maxPolarAngle;

      this.controls.enablePan = restrictions.enablePan !== false;
      this.controls.enableZoom = restrictions.enableZoom !== false;
      this.controls.enableRotate = restrictions.enableRotate !== false;

      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;

      // Set initial target
      const target = this.environment.camera.default.target;
      this.controls.target.set(target.x, target.y, target.z);
      this.controls.update();
    }
  }

  private setupInteractionHandlers(container: HTMLElement): void {
    const canvas = this.renderer.domElement;

    // Mouse move for hover effects
    canvas.addEventListener('mousemove', (event) => {
      const rect = canvas.getBoundingClientRect();
      this.mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

      this.handleHover();
    });

    // Click for interaction
    canvas.addEventListener('click', (event) => {
      this.handleClick(event);
    });

    // Touch support
    canvas.addEventListener('touchstart', (event) => {
      if (event.touches.length === 1) {
        const rect = canvas.getBoundingClientRect();
        this.mouse.x = ((event.touches[0].clientX - rect.left) / rect.width) * 2 - 1;
        this.mouse.y = -((event.touches[0].clientY - rect.top) / rect.height) * 2 + 1;
      }
    });
  }

  /**
   * Handle window resize
   */
  public handleResize(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = container.clientHeight;

    if (this.camera instanceof THREE.PerspectiveCamera) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    } else if (this.camera instanceof THREE.OrthographicCamera) {
      const frustumSize = 10;
      const aspect = width / height;
      this.camera.left = -frustumSize * aspect / 2;
      this.camera.right = frustumSize * aspect / 2;
      this.camera.top = frustumSize / 2;
      this.camera.bottom = -frustumSize / 2;
      this.camera.updateProjectionMatrix();
    }

    this.renderer.setSize(width, height);
    this.composer.setSize(width, height);
  }

  // ============================================================================
  // LOADING & INITIALIZATION
  // ============================================================================

  public async initialize(
    onProgress?: (progress: LoadProgress) => void
  ): Promise<void> {
    if (this.isInitialized) {
      console.warn('Environment already initialized');
      return;
    }

    const startTime = performance.now();

    try {
      // Load assets
      await this.loadAssets(onProgress);

      // Build scene
      await this.buildScene();

      // Setup lighting
      await this.setupLighting();

      // Setup brand colors
      await this.applyBrandColors();

      // Setup post-processing
      await this.setupPostProcessing();

      // Calculate load time
      const loadTime = (performance.now() - startTime) / 1000;
      this.performanceMetrics.loadTime = loadTime;

      this.isInitialized = true;

      console.log(`Environment initialized in ${loadTime.toFixed(2)}s`);
    } catch (error) {
      console.error('Failed to initialize environment:', error);
      throw error;
    }
  }

  private async loadAssets(
    onProgress?: (progress: LoadProgress) => void
  ): Promise<void> {
    const totalAssets =
      this.environment.assets.models.length +
      this.environment.assets.textures.length;

    let loadedAssets = 0;

    // Load models (with procedural fallback)
    for (const modelAsset of this.environment.assets.models) {
      try {
        const gltf = await this.gltfLoader.loadAsync(modelAsset.path);
        this.assetCache.set(modelAsset.id, gltf);
        loadedAssets++;

        if (onProgress) {
          onProgress({
            loaded: loadedAssets,
            total: totalAssets,
            percentage: (loadedAssets / totalAssets) * 100,
            currentAsset: modelAsset.id
          });
        }
      } catch (error) {
        console.warn(`Model not found, using procedural asset: ${modelAsset.path}`);

        // Generate procedural asset as fallback
        const proceduralAsset = this.generateProceduralAsset(modelAsset.id, modelAsset.path);
        if (proceduralAsset) {
          // Wrap in GLTF-like structure
          const mockGLTF = {
            scene: proceduralAsset,
            scenes: [proceduralAsset],
            animations: [],
            cameras: [],
            asset: {}
          };
          this.assetCache.set(modelAsset.id, mockGLTF);
        }

        loadedAssets++;

        if (onProgress) {
          onProgress({
            loaded: loadedAssets,
            total: totalAssets,
            percentage: (loadedAssets / totalAssets) * 100,
            currentAsset: `${modelAsset.id} (procedural)`
          });
        }
      }
    }

    // Load textures
    for (const textureAsset of this.environment.assets.textures) {
      try {
        const texture = await this.textureLoader.loadAsync(textureAsset.path);

        // Configure texture
        if (textureAsset.wrapping === 'repeat') {
          texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
        } else if (textureAsset.wrapping === 'clamp') {
          texture.wrapS = texture.wrapT = THREE.ClampToEdgeWrapping;
        } else if (textureAsset.wrapping === 'mirror') {
          texture.wrapS = texture.wrapT = THREE.MirroredRepeatWrapping;
        }

        if (textureAsset.mipMaps) {
          texture.generateMipmaps = true;
          texture.minFilter = THREE.LinearMipmapLinearFilter;
        }

        texture.colorSpace = THREE.SRGBColorSpace;

        this.assetCache.set(textureAsset.id, texture);
        loadedAssets++;

        if (onProgress) {
          onProgress({
            loaded: loadedAssets,
            total: totalAssets,
            percentage: (loadedAssets / totalAssets) * 100,
            currentAsset: textureAsset.id
          });
        }
      } catch (error) {
        console.error(`Failed to load texture: ${textureAsset.path}`, error);
      }
    }

    // Load IBL if enabled (graceful fallback if file missing)
    if (this.environment.lighting.ibl.enabled) {
      try {
        const envMap = await this.rgbeLoader.loadAsync(
          this.environment.lighting.ibl.envMapPath
        );
        envMap.mapping = THREE.EquirectangularReflectionMapping;
        this.scene.environment = envMap;
        this.assetCache.set('ibl_envmap', envMap);
      } catch (error) {
        console.warn('IBL environment map not available, using fallback');
        // Continue without IBL - it's optional
      }
    }
  }

  /**
   * Generate procedural 3D asset as fallback when real model is not available
   */
  private generateProceduralAsset(assetId: string, modelPath: string): THREE.Group | null {
    // Parse asset type from path or ID
    const pathLower = modelPath.toLowerCase();
    const idLower = assetId.toLowerCase();

    // Determine asset type from path/ID
    if (pathLower.includes('guitar') || idLower.includes('guitar')) {
      if (pathLower.includes('electric') || pathLower.includes('strat') || pathLower.includes('tele') || pathLower.includes('les_paul')) {
        return assetGenerator.generateAsset(AssetType.ELECTRIC_GUITAR);
      } else if (pathLower.includes('acoustic') || idLower.includes('acoustic')) {
        return assetGenerator.generateAsset(AssetType.ACOUSTIC_GUITAR);
      } else if (pathLower.includes('bass') || idLower.includes('bass')) {
        return assetGenerator.generateAsset(AssetType.BASS_GUITAR);
      }
    }

    if (pathLower.includes('synth') || idLower.includes('synth')) {
      return assetGenerator.generateAsset(AssetType.SYNTHESIZER);
    }

    if (pathLower.includes('keyboard') || pathLower.includes('piano') || idLower.includes('piano')) {
      return assetGenerator.generateAsset(AssetType.KEYBOARD);
    }

    if (pathLower.includes('drum') || idLower.includes('drum')) {
      return assetGenerator.generateAsset(AssetType.DRUM_KIT);
    }

    if (pathLower.includes('amp') || idLower.includes('amp')) {
      return assetGenerator.generateAsset(AssetType.AMPLIFIER);
    }

    if (pathLower.includes('pedestal') || pathLower.includes('stand') || idLower.includes('pedestal')) {
      return assetGenerator.generateAsset(AssetType.PEDESTAL);
    }

    if (pathLower.includes('wall') || pathLower.includes('brick') || idLower.includes('wall')) {
      return assetGenerator.generateAsset(AssetType.WALL_BRICK);
    }

    if (pathLower.includes('floor') || pathLower.includes('wood') || idLower.includes('floor')) {
      return assetGenerator.generateAsset(AssetType.FLOOR_WOOD);
    }

    if (pathLower.includes('light') || pathLower.includes('spot') || idLower.includes('light')) {
      return assetGenerator.generateAsset(AssetType.SPOTLIGHT);
    }

    if (pathLower.includes('cable') || idLower.includes('cable')) {
      return assetGenerator.generateAsset(AssetType.CABLE);
    }

    // Default placeholder
    console.log(`Creating generic placeholder for: ${assetId}`);
    const group = new THREE.Group();
    group.name = assetId;

    // Create a simple colored cube as placeholder
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshStandardMaterial({
      color: Math.random() * 0xffffff,
      metalness: 0.5,
      roughness: 0.5
    });
    const mesh = new THREE.Mesh(geometry, material);
    group.add(mesh);

    return group;
  }

  private async buildScene(): Promise<void> {
    try {
      // Build each layer
      if (this.environment.scene.layers.hero) {
        await this.buildLayer(this.environment.scene.layers.hero, this.heroLayer);
      }
      if (this.environment.scene.layers.context) {
        await this.buildLayer(this.environment.scene.layers.context, this.contextLayer);
      }
      if (this.environment.scene.layers.atmosphere) {
        await this.buildLayer(this.environment.scene.layers.atmosphere, this.atmosphereLayer);
      }

      // Add geometry (floor, background)
      this.addBackgroundGeometry();
      this.addFloorGeometry();
    } catch (error) {
      console.error('Error building scene:', error);
    }
  }

  private async buildLayer(
    layerConfig: any,
    layerGroup: THREE.Group
  ): Promise<void> {
    if (!layerConfig || !layerConfig.elements || layerConfig.elements.length === 0) {
      return; // Skip empty layers
    }

    try {
      for (const element of layerConfig.elements) {
        try {
          const object = await this.createSceneElement(element);
          if (object) {
            layerGroup.add(object);
          }
        } catch (error) {
          console.warn(`Failed to create scene element: ${element.id}`, error);
        }
      }

      layerGroup.visible = layerConfig.visibility !== false && (layerConfig.visibility === undefined || layerConfig.visibility > 0);
      if (layerConfig.renderOrder !== undefined) {
        layerGroup.renderOrder = layerConfig.renderOrder;
      }
    } catch (error) {
      console.error('Error building layer:', error);
    }
  }

  private async createSceneElement(
    element: SceneElement
  ): Promise<THREE.Object3D | null> {
    const gltf = this.assetCache.get(element.id);
    let object: THREE.Object3D;

    if (!gltf) {
      // Create placeholder if asset not loaded
      console.warn(`Asset not loaded, creating placeholder: ${element.id}`);
      const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color(Math.random() * 0xffffff),
        metalness: 0.5,
        roughness: 0.5
      });
      object = new THREE.Mesh(geometry, material);
      object.name = element.id;
    } else {
      object = gltf.scene.clone();
    }

    // Apply transforms
    object.position.set(element.position.x, element.position.y, element.position.z);
    object.rotation.set(
      THREE.MathUtils.degToRad(element.rotation.x),
      THREE.MathUtils.degToRad(element.rotation.y),
      THREE.MathUtils.degToRad(element.rotation.z)
    );
    object.scale.set(element.scale.x, element.scale.y, element.scale.z);

    // Apply materials
    this.applyMaterials(object, element.materials);

    // Setup LOD if configured
    if (element.lod && element.lod.length > 0) {
      const lod = new THREE.LOD();
      lod.addLevel(object, element.lod[0].distance);

      for (let i = 1; i < element.lod.length; i++) {
        // Simplified LOD levels would be loaded here
        // For now, use the same object with simplified rendering
      }

      return lod;
    }

    // Store metadata
    object.userData = element.metadata;

    return object;
  }

  private applyMaterials(
    object: THREE.Object3D,
    materialAssignments: any[]
  ): void {
    if (!materialAssignments || materialAssignments.length === 0) {
      return; // No materials to apply
    }

    object.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        const assignment = materialAssignments.find(
          (a) => a.meshName === child.name
        );

        if (assignment && this.environment.scene.materials && this.environment.scene.materials.materials) {
          const materialDef = this.environment.scene.materials.materials.get(
            assignment.materialId
          );

          if (materialDef) {
            child.material = this.createMaterial(materialDef);
          }
        }
      }
    });
  }

  private createMaterial(materialDef: any): THREE.Material {
    const props = materialDef.properties || {};

    // Ensure all color properties exist with defaults
    const baseColor = props.baseColor || { r: 0.8, g: 0.8, b: 0.8 };
    const emissiveColor = props.emissive ? new THREE.Color(props.emissive.r, props.emissive.g, props.emissive.b) : new THREE.Color(0x000000);

    switch (materialDef.type) {
      case 'pbr_standard':
        return new THREE.MeshStandardMaterial({
          color: new THREE.Color(baseColor.r, baseColor.g, baseColor.b),
          metalness: props.metalness || 0,
          roughness: props.roughness || 0.5,
          opacity: props.opacity !== undefined ? props.opacity : 1.0,
          transparent: (props.opacity || 1.0) < 1.0,
          emissive: emissiveColor,
          emissiveIntensity: props.emissiveIntensity || 0,
          side: THREE.FrontSide
        });

      case 'pbr_physical':
        return new THREE.MeshPhysicalMaterial({
          color: new THREE.Color(baseColor.r, baseColor.g, baseColor.b),
          metalness: props.metalness || 0,
          roughness: props.roughness || 0.5,
          opacity: props.opacity !== undefined ? props.opacity : 1.0,
          transparent: (props.opacity || 1.0) < 1.0,
          clearcoat: props.clearcoat || 0,
          clearcoatRoughness: props.clearcoatRoughness || 0,
          transmission: props.transmission || 0,
          ior: props.ior || 1.5,
          side: THREE.FrontSide
        });

      default:
        return new THREE.MeshStandardMaterial({
          color: new THREE.Color(baseColor.r, baseColor.g, baseColor.b),
          metalness: 0.5,
          roughness: 0.5,
          emissive: new THREE.Color(0x000000),
          emissiveIntensity: 0,
          side: THREE.FrontSide
        });
    }
  }

  private addBackgroundGeometry(): void {
    try {
      const bg = this.environment.scene.geometry?.background;
      if (!bg) return;

      if (bg.type === 'wall') {
        const geometry = new THREE.PlaneGeometry(
          bg.dimensions?.width || 4,
          bg.dimensions?.height || 3,
          bg.subdivisions || 1,
          bg.subdivisions || 1
        );

        const materialDef = this.environment.scene.materials?.materials?.get(bg.material);
        const material = materialDef ? this.createMaterial(materialDef) : new THREE.MeshStandardMaterial({
          color: 0x888888,
          metalness: 0.1,
          roughness: 0.8
        });

        const wall = new THREE.Mesh(geometry, material);
        wall.position.z = -(this.environment.config?.dimensions?.depth || 1.5) / 2;
        wall.receiveShadow = true;

        this.contextLayer.add(wall);
      }
    } catch (error) {
      console.warn('Error adding background geometry:', error);
    }
  }

  private addFloorGeometry(): void {
    try {
      const floor = this.environment.scene.geometry?.floor;
      if (!floor) return;

      const geometry = new THREE.PlaneGeometry(
        floor.dimensions?.width || 5,
        floor.dimensions?.depth || 3,
        50,
        50
      );
      geometry.rotateX(-Math.PI / 2);

      const materialDef = this.environment.scene.materials?.materials?.get(floor.material);
      const material = materialDef ? this.createMaterial(materialDef) : new THREE.MeshStandardMaterial({
        color: 0x8B4513,
        metalness: 0.1,
        roughness: 0.8
      });

      const floorMesh = new THREE.Mesh(geometry, material);
      floorMesh.receiveShadow = true;
      floorMesh.position.y = 0;

      this.contextLayer.add(floorMesh);
    } catch (error) {
      console.warn('Error adding floor geometry:', error);
    }
  }

  // ============================================================================
  // LIGHTING SETUP
  // ============================================================================

  private async setupLighting(): Promise<void> {
    try {
      const lighting = this.environment.lighting;
      if (!lighting) return;

      // Ambient light
      if (lighting.ambient) {
        const ambient = new THREE.AmbientLight(
          new THREE.Color(lighting.ambient.color?.r || 1, lighting.ambient.color?.g || 1, lighting.ambient.color?.b || 1),
          lighting.ambient.intensity || 0.5
        );
        this.scene.add(ambient);
      }

      // Directional lights
      if (lighting.directional && Array.isArray(lighting.directional)) {
        for (const dirLight of lighting.directional) {
          try {
            const light = new THREE.DirectionalLight(
              new THREE.Color(dirLight.color?.r || 1, dirLight.color?.g || 1, dirLight.color?.b || 1),
              dirLight.intensity || 1
            );
            light.position.set(dirLight.position?.x || 5, dirLight.position?.y || 10, dirLight.position?.z || 7);
            light.target.position.set(dirLight.target?.x || 0, dirLight.target?.y || 0, dirLight.target?.z || 0);
            light.castShadow = dirLight.castShadow || false;

            if (dirLight.castShadow) {
              this.configureShadows(light);
            }

            this.scene.add(light);
            this.scene.add(light.target);
            this.lights.set(dirLight.id, light);
          } catch (error) {
            console.warn('Error adding directional light:', error);
          }
        }
      }

      // Point lights
      if (lighting.point && Array.isArray(lighting.point)) {
        for (const pointLight of lighting.point) {
          try {
            const light = new THREE.PointLight(
              new THREE.Color(pointLight.color?.r || 1, pointLight.color?.g || 1, pointLight.color?.b || 1),
              pointLight.intensity || 1,
              pointLight.distance || 100,
              pointLight.decay || 2
            );
            light.position.set(pointLight.position?.x || 0, pointLight.position?.y || 2, pointLight.position?.z || 0);
            light.castShadow = pointLight.castShadow || false;

            if (pointLight.castShadow) {
              this.configureShadows(light);
            }

            this.scene.add(light);
            this.lights.set(pointLight.id, light);
          } catch (error) {
            console.warn('Error adding point light:', error);
          }
        }
      }

      // Spot lights
      if (lighting.spot && Array.isArray(lighting.spot)) {
        for (const spotLight of lighting.spot) {
          try {
            const light = new THREE.SpotLight(
              new THREE.Color(spotLight.color?.r || 1, spotLight.color?.g || 1, spotLight.color?.b || 1),
              spotLight.intensity || 1,
              0,
              spotLight.angle || Math.PI / 4,
              spotLight.penumbra || 0,
              spotLight.decay || 2
            );
            light.position.set(spotLight.position?.x || 0, spotLight.position?.y || 2, spotLight.position?.z || 0);
            light.target.position.set(spotLight.target?.x || 0, spotLight.target?.y || 0, spotLight.target?.z || 0);
            light.castShadow = spotLight.castShadow || false;

            if (spotLight.castShadow) {
              this.configureShadows(light);
            }

            this.scene.add(light);
            this.scene.add(light.target);
            this.lights.set(spotLight.id, light);
          } catch (error) {
            console.warn('Error adding spot light:', error);
          }
        }
      }
    } catch (error) {
      console.error('Error setting up lighting:', error);
    }
  }

  private configureShadows(light: THREE.Light): void {
    const shadowConfig = this.environment.lighting.shadows;

    if (light.shadow) {
      light.shadow.mapSize.width = shadowConfig.quality;
      light.shadow.mapSize.height = shadowConfig.quality;
      light.shadow.bias = shadowConfig.bias;
      light.shadow.radius = shadowConfig.radius;

      if (light instanceof THREE.DirectionalLight) {
        light.shadow.camera.left = -10;
        light.shadow.camera.right = 10;
        light.shadow.camera.top = 10;
        light.shadow.camera.bottom = -10;
        light.shadow.camera.near = 0.1;
        light.shadow.camera.far = 20;
      }
    }
  }

  // ============================================================================
  // BRAND COLOR SYSTEM
  // ============================================================================

  private async applyBrandColors(): Promise<void> {
    try {
      const brandScheme = this.environment.brandColors;
      if (!brandScheme) return;

      const lighting = this.environment.lighting;
      if (!lighting || !lighting.brandLights || !Array.isArray(lighting.brandLights)) {
        return;
      }

      // Create brand lights
      for (const brandLight of lighting.brandLights) {
        try {
          let light: THREE.Light | undefined;

          switch (brandLight.type) {
            case 'point':
              light = new THREE.PointLight(
                new THREE.Color(brandLight.color?.r || 1, brandLight.color?.g || 1, brandLight.color?.b || 1),
                brandLight.intensity || 1,
                brandLight.distance || 10,
                brandLight.decay || 2
              );
              light.position.set(brandLight.position?.x || 0, brandLight.position?.y || 2, brandLight.position?.z || 0);
              break;

            case 'spot':
              light = new THREE.SpotLight(
                new THREE.Color(brandLight.color?.r || 1, brandLight.color?.g || 1, brandLight.color?.b || 1),
                brandLight.intensity || 1,
                0,
                brandLight.angle || Math.PI / 6,
                brandLight.penumbra || 0.3,
                brandLight.decay || 2
              );
              light.position.set(brandLight.position?.x || 0, brandLight.position?.y || 2, brandLight.position?.z || 0);
              if (brandLight.target) {
                (light as THREE.SpotLight).target.position.set(
                  brandLight.target.x || 0,
                  brandLight.target.y || 0,
                  brandLight.target.z || 0
                );
                this.scene.add((light as THREE.SpotLight).target);
              }
              break;

            default:
              continue;
          }

          if (light) {
            this.scene.add(light);
            this.brandLights.set(brandLight.id, light);

            // Setup animation if configured
            if (brandLight.animation) {
              this.animateBrandLight(brandLight.id, brandLight.animation);
            }
          }
        } catch (error) {
          console.warn('Error creating brand light:', error);
        }
      }

      // Apply brand colors to zones (for future implementations)
      // This would involve creating colored fog, volumetric lighting, etc.
    } catch (error) {
      console.error('Error applying brand colors:', error);
    }
  }

  private animateBrandLight(lightId: string, animation: any): void {
    // Animation will be handled in the render loop
    // Store animation data in light userData
    const light = this.brandLights.get(lightId);
    if (light) {
      light.userData.animation = animation;
    }
  }

  // ============================================================================
  // POST-PROCESSING
  // ============================================================================

  private async setupPostProcessing(): Promise<void> {
    const ppConfig = this.environment.scene.postProcessing;

    if (!ppConfig || !ppConfig.enabled) {
      return;
    }

    try {
      // Clear existing passes
      this.composer.passes = [];

      // Add render pass
      const renderPass = new RenderPass(this.scene, this.camera);
      this.composer.addPass(renderPass);

      // Sort passes by order
      const sortedPasses = (ppConfig.passes || [])
        .filter(p => p && p.enabled)
        .sort((a, b) => (a.order || 0) - (b.order || 0));

      // Add each pass
      for (const passConfig of sortedPasses) {
        if (!passConfig.type) continue;

        switch (passConfig.type) {
          case 'bloom':
            this.addBloomPass(passConfig.parameters || {});
            break;
          case 'ssao':
            this.addSSAOPass(passConfig.parameters || {});
            break;
          case 'fxaa':
            this.addFXAAPass();
            break;
          // Additional passes can be added here
        }
      }
    } catch (error) {
      console.warn('Error setting up post-processing:', error);
    }
  }

  private addBloomPass(params: any): void {
    try {
      const bloomPass = new UnrealBloomPass(
        new THREE.Vector2(window.innerWidth, window.innerHeight),
        params.strength || 1,
        params.radius || 0.4,
        params.threshold || 0.85
      );
      bloomPass.exposure = params.exposure || 2;
      this.composer.addPass(bloomPass);
    } catch (error) {
      console.warn('Error adding bloom pass:', error);
    }
  }

  private addSSAOPass(params: any): void {
    try {
      const ssaoPass = new SSAOPass(
        this.scene,
        this.camera,
        window.innerWidth,
        window.innerHeight
      );
      ssaoPass.kernelRadius = params.radius || 16;
      ssaoPass.minDistance = 0.005;
      ssaoPass.maxDistance = 0.1;
      this.composer.addPass(ssaoPass);
    } catch (error) {
      console.warn('Error adding SSAO pass:', error);
    }
  }

  private addFXAAPass(): void {
    try {
      const fxaaPass = new ShaderPass(FXAAShader);
      const pixelRatio = this.renderer.getPixelRatio();
      fxaaPass.material.uniforms['resolution'].value.x = 1 / (window.innerWidth * pixelRatio);
      fxaaPass.material.uniforms['resolution'].value.y = 1 / (window.innerHeight * pixelRatio);
      this.composer.addPass(fxaaPass);
    } catch (error) {
      console.warn('Error adding FXAA pass:', error);
    }
  }

  // ============================================================================
  // INTERACTION & HOVER
  // ============================================================================

  private handleHover(): void {
    this.raycaster.setFromCamera(this.mouse, this.camera);

    const intersects = this.raycaster.intersectObjects(
      this.heroLayer.children,
      true
    );

    if (intersects.length > 0) {
      const object = intersects[0].object;

      // Find the top-level object with metadata
      let target: THREE.Object3D | null = object;
      while (target && !target.userData.interactive) {
        target = target.parent;
      }

      if (target && target !== this.hoveredObject) {
        // Unhover previous
        if (this.hoveredObject) {
          this.unhoverObject(this.hoveredObject);
        }

        // Hover new
        this.hoveredObject = target;
        this.hoverObject(target);
      }
    } else {
      if (this.hoveredObject) {
        this.unhoverObject(this.hoveredObject);
        this.hoveredObject = null;
      }
    }
  }

  private hoverObject(object: THREE.Object3D): void {
    // Change cursor
    this.renderer.domElement.style.cursor = 'pointer';

    // Add highlight effect (example: increase emissive)
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material instanceof THREE.MeshStandardMaterial) {
        child.material.emissive.setHex(0x333333);
        child.material.emissiveIntensity = 0.5;
      }
    });
  }

  private unhoverObject(object: THREE.Object3D): void {
    // Reset cursor
    this.renderer.domElement.style.cursor = 'default';

    // Remove highlight effect
    object.traverse((child) => {
      if (child instanceof THREE.Mesh && child.material instanceof THREE.MeshStandardMaterial) {
        child.material.emissive.setHex(0x000000);
        child.material.emissiveIntensity = 0;
      }
    });
  }

  private handleClick(event: MouseEvent): void {
    this.raycaster.setFromCamera(this.mouse, this.camera);

    const intersects = this.raycaster.intersectObjects(
      this.heroLayer.children,
      true
    );

    if (intersects.length > 0) {
      const object = intersects[0].object;

      // Find the top-level object with metadata
      let target: THREE.Object3D | null = object;
      while (target && !target.userData.clickable) {
        target = target.parent;
      }

      if (target && target.userData) {
        this.onProductClick(target.userData);
      }
    }
  }

  private onProductClick(metadata: any): void {
    console.log('Product clicked:', metadata);
    // Dispatch custom event or call callback
    const event = new CustomEvent('environment3d:product-click', {
      detail: metadata
    });
    window.dispatchEvent(event);
  }

  // ============================================================================
  // ANIMATION & RENDERING
  // ============================================================================

  public startAnimation(): void {
    if (this.isAnimating) {
      console.warn('Animation already running');
      return;
    }

    this.isAnimating = true;
    this.animate();
  }

  public stopAnimation(): void {
    this.isAnimating = false;
    if (this.animationId !== undefined) {
      cancelAnimationFrame(this.animationId);
    }
  }

  private animate = (): void => {
    if (!this.isAnimating) return;

    this.animationId = requestAnimationFrame(this.animate);

    const deltaTime = this.clock.getDelta();

    // Update controls
    if (this.controls) {
      this.controls.update();
    }

    // Update brand light animations
    this.updateBrandLightAnimations(deltaTime);

    // Render
    if (this.environment.scene.postProcessing.enabled) {
      this.composer.render();
    } else {
      this.renderer.render(this.scene, this.camera);
    }

    // Update performance metrics
    this.updatePerformanceMetrics();
  };

  private updateBrandLightAnimations(deltaTime: number): void {
    const time = this.clock.getElapsedTime();

    this.brandLights.forEach((light) => {
      if (light.userData.animation) {
        const anim = light.userData.animation;

        switch (anim.type) {
          case 'pulse':
            const pulse = Math.sin(time * anim.speed) * 0.5 + 0.5;
            light.intensity = THREE.MathUtils.lerp(anim.range[0], anim.range[1], pulse);
            break;

          case 'flicker':
            if (Math.random() < 0.1) {
              light.intensity = THREE.MathUtils.lerp(anim.range[0], anim.range[1], Math.random());
            }
            break;
        }
      }
    });
  }

  private updatePerformanceMetrics(): void {
    this.performanceMetrics.currentFPS = 1 / this.clock.getDelta();
    this.performanceMetrics.timestamp = Date.now();

    // Get renderer info
    const info = this.renderer.info;
    this.performanceMetrics.polyCount = info.render.triangles;
    this.performanceMetrics.drawCalls = info.render.calls;
    this.performanceMetrics.textureMemory = info.memory.textures;
  }

  // ============================================================================
  // UTILITY METHODS
  // ============================================================================

  public getPerformanceMetrics(): PerformanceMetrics {
    return { ...this.performanceMetrics };
  }

  public setCameraPreset(presetName: string): void {
    const preset = this.environment.camera.presets.get(presetName);
    if (!preset) {
      console.warn(`Camera preset not found: ${presetName}`);
      return;
    }

    this.camera.position.set(preset.position.x, preset.position.y, preset.position.z);

    if (this.controls) {
      this.controls.target.set(preset.target.x, preset.target.y, preset.target.z);
      this.controls.update();
    }
  }

  public focusOnProduct(productId: string): void {
    // Find product in scene
    let targetObject: THREE.Object3D | null = null;

    this.heroLayer.traverse((object) => {
      if (object.userData.productId === productId) {
        targetObject = object;
      }
    });

    if (targetObject) {
      // Calculate optimal camera position
      const box = new THREE.Box3().setFromObject(targetObject);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());

      const maxDim = Math.max(size.x, size.y, size.z);
      const fov = (this.camera as THREE.PerspectiveCamera).fov * (Math.PI / 180);
      let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.5;

      const cameraPos = new THREE.Vector3(
        center.x,
        center.y + size.y * 0.3,
        center.z + cameraZ
      );

      // Animate camera (simplified, would use GSAP in production)
      this.camera.position.lerp(cameraPos, 0.1);

      if (this.controls) {
        this.controls.target.lerp(center, 0.1);
        this.controls.update();
      }
    }
  }

  private handleResize(container: HTMLElement): void {
    const width = container.clientWidth;
    const height = container.clientHeight;

    if (this.camera instanceof THREE.PerspectiveCamera) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    }

    this.renderer.setSize(width, height);
    this.composer.setSize(width, height);
  }

  public dispose(): void {
    this.stopAnimation();

    // Dispose scene objects
    this.scene.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        object.geometry.dispose();
        if (Array.isArray(object.material)) {
          object.material.forEach(material => material.dispose());
        } else {
          object.material.dispose();
        }
      }
    });

    // Dispose renderer
    this.renderer.dispose();

    // Dispose controls
    if (this.controls) {
      this.controls.dispose();
    }

    // Clear caches
    this.assetCache.clear();
    this.lights.clear();
    this.brandLights.clear();
  }
}
