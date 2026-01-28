/**
 * 3D Environment System - Type Definitions
 * Halilit Support Center - Galaxy Edition v4
 * 
 * Comprehensive type system for immersive subcategory visualization
 * @module environment3d.types
 * @version 4.1.0
 */

import type * as THREE from 'three';

// ============================================================================
// CORE TYPES
// ============================================================================

/**
 * Complete 3D environment specification for a subcategory slot
 * Includes scene layout, lighting, materials, camera setup, and brand integration
 */
export interface Environment3D {
    /** Unique identifier for this environment */
    id: string;
    /** Parent category ID */
    categoryId: string;
    /** Target subcategory ID */
    subcategoryId: string;
    /** Display name */
    name: string;
    /** Brief description for documentation */
    description: string;
    /** Core configuration settings */
    config: EnvironmentConfig;
    /** Scene layout and 3D elements */
    scene: SceneDefinition;
    /** Lighting system setup */
    lighting: LightingRig;
    /** Camera configuration */
    camera: CameraSetup;
    /** Dynamic brand color integration */
    brandColors: BrandColorScheme;
    /** Asset manifest for loading */
    assets: AssetManifest;
    /** Performance targets and optimizations */
    performance: PerformanceProfile;
    /** Version control for configuration changes */
    version: string;
    /** Last update timestamp */
    lastModified: number;
}

export interface EnvironmentConfig {
    /** Physical dimensions in meters */
    dimensions: {
        width: number;
        height: number;
        depth: number;
    };
    /** Visual style category */
    style: EnvironmentStyle;
    /** Scene complexity level */
    complexity: ComplexityLevel;
    /** User interaction capabilities */
    interactionMode: InteractionMode;
    /** Asset loading priority */
    loadPriority: LoadPriority;
    /** Enable HDR rendering */
    hdr?: boolean;
    /** Enable gamma correction */
    gammaCorrection?: boolean;
}

export enum EnvironmentStyle {
    SHOWROOM = 'showroom',
    STUDIO = 'studio',
    STAGE = 'stage',
    HOME = 'home',
    WORKSHOP = 'workshop',
    VENUE = 'venue',
    BOUTIQUE = 'boutique',
    LAB = 'lab'
}

export enum ComplexityLevel {
    SIMPLE = 'simple',      // 30K polygons, 30 draw calls
    MEDIUM = 'medium',      // 80K polygons, 60 draw calls
    COMPLEX = 'complex'     // 150K polygons, 90 draw calls
}

export enum InteractionMode {
    STATIC = 'static',          // No interaction
    HOVER = 'hover',            // Hover effects only
    CLICKABLE = 'clickable',    // Click to focus products
    EXPLORABLE = 'explorable'   // Full camera control enabled
}

export enum LoadPriority {
    CRITICAL = 'critical',   // Load immediately on app start
    HIGH = 'high',          // Load on category selection
    NORMAL = 'normal',      // Load on subcategory view
    LOW = 'low'            // Lazy load when viewport near
}

// ============================================================================
// SCENE ARCHITECTURE
// ============================================================================

export interface SceneDefinition {
    /** Layered scene organization (hero, context, atmosphere) */
    layers: SceneLayers;
    /** Geometric structures (floor, walls, props) */
    geometry: GeometryDefinition;
    /** Material library */
    materials: MaterialLibrary;
    /** Post-processing effects */
    postProcessing: PostProcessingStack;
    /** Background environment */
    background?: BackgroundConfig;
}

export interface SceneLayers {
    /** 0-2m: Featured products, primary interaction zone */
    hero: LayerConfig;
    /** 2-5m: Environmental storytelling elements */
    context: LayerConfig;
    /** 5-10m: Background, depth, ambient elements */
    atmosphere: LayerConfig;
}

export interface LayerConfig {
    name: string;
    /** Depth range [near, far] in meters */
    depth: [number, number];
    /** 3D elements in this layer */
    elements: SceneElement[];
    /** Layer opacity 0-1 */
    visibility: number;
    /** Render order (lower = rendered first) */
    renderOrder: number;
    /** Layer-specific fog settings */
    fog?: FogConfig;
}

export interface SceneElement {
    id: string;
    type: ElementType;
    /** Path to glTF/GLB model */
    modelPath: string;
    /** World position */
    position: Vector3;
    /** Euler rotation in radians */
    rotation: Vector3;
    /** Uniform scale or per-axis */
    scale: Vector3 | number;
    /** Material assignments */
    materials: MaterialAssignment[];
    /** Level of detail variants */
    lod: LODConfig[];
    /** Additional metadata */
    metadata: ElementMetadata;
    /** Custom animations */
    animations?: AnimationConfig[];
}

export enum ElementType {
    PRODUCT = 'product',
    PROP = 'prop',
    STRUCTURE = 'structure',
    DECORATION = 'decoration',
    LIGHTING_FIXTURE = 'lighting_fixture',
    PARTICLE_SYSTEM = 'particle_system'
}

export interface Vector3 {
    x: number;
    y: number;
    z: number;
}

export interface MaterialAssignment {
    /** Target mesh name from model */
    meshName: string;
    /** Material ID from library */
    materialId: string;
    /** Property overrides for this instance */
    overrides?: Partial<MaterialProperties>;
}

export interface LODConfig {
    /** LOD level (0 = highest quality) */
    level: number;
    /** Switch distance in meters */
    distance: number;
    /** Different model path for this LOD */
    modelPath?: string;
    /** Simplification factor 0-1 (if same model) */
    simplification?: number;
}

export interface ElementMetadata {
    description: string;
    /** Associated brand ID (if product/branded prop) */
    brandId?: string;
    /** Halilit product ID (if actual inventory item) */
    productId?: string;
    /** Can be interacted with */
    interactive: boolean;
    /** Click handler enabled */
    clickable: boolean;
    /** Hover effects enabled */
    hoverable: boolean;
    /** Searchable tags */
    tags: string[];
    /** Display name override */
    displayName?: string;
}

export interface AnimationConfig {
    /** Animation clip name */
    name: string;
    /** Auto-play on load */
    autoPlay: boolean;
    /** Loop animation */
    loop: boolean;
    /** Playback speed multiplier */
    speed: number;
    /** Start time offset */
    startTime?: number;
}

export interface FogConfig {
    enabled: boolean;
    color: Color;
    near: number;
    far: number;
    density?: number;  // For exponential fog
}

// ============================================================================
// GEOMETRY SYSTEM
// ============================================================================

export interface GeometryDefinition {
    background: BackgroundGeometry;
    floor: FloorGeometry;
    structures: StructureGeometry[];
    props: PropGeometry[];
}

export interface BackgroundGeometry {
    type: 'wall' | 'curtain' | 'panel' | 'sky' | 'open' | 'cyclorama';
    material: string;
    dimensions: {
        width: number;
        height: number;
    };
    subdivisions?: number;
    curve?: CurveDefinition;
    /** Enable realtime reflections */
    reflective?: boolean;
}

export interface FloorGeometry {
    type: 'flat' | 'platform' | 'stepped' | 'curved' | 'terrain';
    material: string;
    dimensions: {
        width: number;
        depth: number;
    };
    pattern?: FloorPattern;
    /** Enable reflections */
    reflective?: boolean;
    /** Reflection intensity */
    reflectionIntensity?: number;
}

export enum FloorPattern {
    PLAIN = 'plain',
    GRID = 'grid',
    WOOD_PLANK = 'wood_plank',
    HERRINGBONE = 'herringbone',
    TILE = 'tile',
    CARPET = 'carpet',
    CONCRETE = 'concrete',
    MARBLE = 'marble'
}

export interface StructureGeometry {
    type: 'shelf' | 'rack' | 'table' | 'stand' | 'booth' | 'truss' | 'pedestal';
    modelPath: string;
    placement: PlacementRule[];
    /** Cast shadows */
    castShadow?: boolean;
    /** Receive shadows */
    receiveShadow?: boolean;
}

export interface PropGeometry {
    type: string;
    modelPath: string;
    count: number;
    distribution: DistributionRule;
}

export interface CurveDefinition {
    points: Vector3[];
    tension: number;
    closed: boolean;
}

export interface PlacementRule {
    position: Vector3;
    rotation: Vector3;
    scale?: Vector3 | number;
    randomOffset?: {
        position: Vector3;
        rotation: Vector3;
    };
}

export interface DistributionRule {
    method: 'grid' | 'random' | 'curve' | 'manual' | 'circular';
    parameters: Record<string, unknown>;
}

export interface BackgroundConfig {
    type: 'color' | 'gradient' | 'skybox' | 'equirectangular';
    color?: Color;
    colors?: Color[];  // For gradient
    texture?: string;  // Path to HDRI or cubemap
    rotation?: number;
    intensity?: number;
}

// ============================================================================
// MATERIAL SYSTEM
// ============================================================================

export interface MaterialLibrary {
    materials: Record<string, MaterialDefinition>;
    textures: Record<string, TextureDefinition>;
    shaders?: Record<string, ShaderDefinition>;
}

export interface MaterialDefinition {
    id: string;
    name: string;
    type: MaterialType;
    properties: MaterialProperties;
    textures: TextureAssignment[];
    /** Enable transparency */
    transparent?: boolean;
    /** Alpha test threshold */
    alphaTest?: number;
    /** Depth write */
    depthWrite?: boolean;
    /** Depth test */
    depthTest?: boolean;
    /** Render side */
    side?: 'front' | 'back' | 'double';
}

export enum MaterialType {
    PBR_STANDARD = 'pbr_standard',
    PBR_PHYSICAL = 'pbr_physical',
    SHADER_CUSTOM = 'shader_custom',
    TOON = 'toon',
    EMISSIVE = 'emissive',
    GLASS = 'glass',
    MATCAP = 'matcap'
}

export interface MaterialProperties {
    baseColor: Color;
    metalness: number;      // 0-1
    roughness: number;      // 0-1
    opacity: number;        // 0-1
    emissive?: Color;
    emissiveIntensity?: number;
    normalScale?: number;
    aoIntensity?: number;
    clearcoat?: number;
    clearcoatRoughness?: number;
    transmission?: number;  // For glass
    ior?: number;          // Index of refraction (1.5 for glass)
    thickness?: number;    // For thin-film interference
    sheen?: number;        // Fabric sheen
    sheenColor?: Color;
    specularIntensity?: number;
    specularColor?: Color;
}

export interface Color {
    r: number;
    g: number;
    b: number;
    a?: number;
}

export interface TextureAssignment {
    channel: TextureChannel;
    textureId: string;
    uvSet?: number;
    transform?: TextureTransform;
}

export enum TextureChannel {
    BASE_COLOR = 'baseColor',
    METALLIC = 'metallic',
    ROUGHNESS = 'roughness',
    NORMAL = 'normal',
    AMBIENT_OCCLUSION = 'ao',
    EMISSIVE = 'emissive',
    OPACITY = 'opacity',
    DISPLACEMENT = 'displacement',
    CLEARCOAT = 'clearcoat',
    CLEARCOAT_ROUGHNESS = 'clearcoatRoughness',
    TRANSMISSION = 'transmission'
}

export interface TextureDefinition {
    id: string;
    path: string;
    format: TextureFormat;
    resolution: [number, number];
    compression: CompressionType;
    mipMaps: boolean;
    wrapping: TextureWrapping;
    /** Color space */
    colorSpace?: 'srgb' | 'linear';
    /** Anisotropy level */
    anisotropy?: number;
}

export enum TextureFormat {
    PNG = 'png',
    WEBP = 'webp',
    KTX2 = 'ktx2',
    BASIS = 'basis',
    JPEG = 'jpeg'
}

export enum CompressionType {
    NONE = 'none',
    DRACO = 'draco',
    MESHOPT = 'meshopt',
    KTX2_UASTC = 'ktx2_uastc',
    KTX2_ETC1S = 'ktx2_etc1s'
}

export enum TextureWrapping {
    REPEAT = 'repeat',
    CLAMP = 'clamp',
    MIRROR = 'mirror'
}

export interface TextureTransform {
    offset: [number, number];
    scale: [number, number];
    rotation: number;
}

export interface ShaderDefinition {
    id: string;
    name: string;
    vertexShader: string;
    fragmentShader: string;
    uniforms: Record<string, ShaderUniform>;
    /** Enable depth write */
    depthWrite?: boolean;
    /** Blending mode */
    blending?: 'normal' | 'additive' | 'multiply' | 'custom';
}

export interface ShaderUniform {
    type: 'float' | 'vec2' | 'vec3' | 'vec4' | 'color' | 'texture' | 'int' | 'bool';
    value: unknown;
}

// ============================================================================
// LIGHTING SYSTEM
// ============================================================================

export interface LightingRig {
    ambient: AmbientLighting;
    directional: DirectionalLight[];
    point: PointLight[];
    spot: SpotLight[];
    area: AreaLight[];
    ibl: IBLConfig;
    brandLights: BrandLight[];
    shadows: ShadowConfig;
    /** Global light intensity multiplier */
    globalIntensity?: number;
}

export interface AmbientLighting {
    color: Color;
    intensity: number;
    /** Ground color for hemisphere light */
    groundColor?: Color;
    /** Use ambient light or hemisphere */
    type?: 'ambient' | 'hemisphere';
}

export interface DirectionalLight {
    id: string;
    name: string;
    color: Color;
    intensity: number;
    position: Vector3;
    target: Vector3;
    castShadow: boolean;
    /** Shadow camera size */
    shadowCameraSize?: number;
    /** Shadow bias to prevent acne */
    shadowBias?: number;
}

export interface PointLight {
    id: string;
    name: string;
    color: Color;
    intensity: number;
    position: Vector3;
    /** Falloff distance */
    distance: number;
    /** Falloff rate */
    decay: number;
    castShadow: boolean;
}

export interface SpotLight {
    id: string;
    name: string;
    color: Color;
    intensity: number;
    position: Vector3;
    target: Vector3;
    /** Cone angle in radians */
    angle: number;
    /** Edge softness 0-1 */
    penumbra: number;
    decay: number;
    castShadow: boolean;
    /** Shadow bias */
    shadowBias?: number;
}

export interface AreaLight {
    id: string;
    name: string;
    color: Color;
    intensity: number;
    position: Vector3;
    width: number;
    height: number;
    rotation: Vector3;
}

export interface IBLConfig {
    enabled: boolean;
    /** Path to HDRI environment map */
    envMapPath: string;
    intensity: number;
    /** Y-axis rotation in radians */
    rotation: number;
    /** Environment map blur 0-1 */
    blur: number;
    /** Use as background */
    background?: boolean;
    /** Background blur (if different from reflection blur) */
    backgroundBlur?: number;
}

export interface BrandLight {
    id: string;
    brandId: string;
    type: 'point' | 'spot' | 'area';
    /** Dynamic color from brand palette */
    color: Color;
    intensity: number;
    position: Vector3;
    target?: Vector3;
    animation?: LightAnimation;
    /** Blend with scene lighting */
    blendMode?: 'add' | 'multiply' | 'screen';
}

export interface LightAnimation {
    type: 'pulse' | 'flicker' | 'fade' | 'color_cycle' | 'strobe';
    speed: number;
    /** Min/max intensity or hue shift */
    range: [number, number];
    /** Easing function */
    easing?: 'linear' | 'sine' | 'elastic';
}

export interface ShadowConfig {
    enabled: boolean;
    type: ShadowType;
    quality: ShadowQuality;
    bias: number;
    /** Shadow blur radius */
    radius: number;
    /** Auto-update shadows (expensive) */
    autoUpdate?: boolean;
}

export enum ShadowType {
    PCF = 'pcf',              // Percentage Closer Filtering
    PCF_SOFT = 'pcf_soft',    // Softer PCF
    VSM = 'vsm'               // Variance Shadow Maps
}

export enum ShadowQuality {
    LOW = 512,
    MEDIUM = 1024,
    HIGH = 2048,
    ULTRA = 4096
}

// ============================================================================
// CAMERA SYSTEM
// ============================================================================

export interface CameraSetup {
    default: CameraConfig;
    presets: Record<string, CameraConfig>;
    animations: CameraAnimation[];
    controls: CameraControls;
    /** Initial intro animation */
    introAnimation?: string;
}

export interface CameraConfig {
    name: string;
    type: 'perspective' | 'orthographic';
    position: Vector3;
    target: Vector3;
    /** Field of view (perspective only) */
    fov?: number;
    near: number;
    far: number;
    /** Zoom level (orthographic only) */
    zoom?: number;
}

export interface CameraAnimation {
    id: string;
    name: string;
    keyframes: CameraKeyframe[];
    /** Duration in seconds */
    duration: number;
    easing: EasingFunction;
    loop: boolean;
    /** Auto-play on environment load */
    autoPlay?: boolean;
}

export interface CameraKeyframe {
    /** Time 0-1 normalized */
    time: number;
    position: Vector3;
    target: Vector3;
    fov?: number;
}

export enum EasingFunction {
    LINEAR = 'linear',
    EASE_IN = 'easeIn',
    EASE_OUT = 'easeOut',
    EASE_IN_OUT = 'easeInOut',
    ELASTIC = 'elastic',
    BOUNCE = 'bounce',
    CUBIC = 'cubic',
    QUAD = 'quad'
}

export interface CameraControls {
    enabled: boolean;
    type: ControlType;
    restrictions: ControlRestrictions;
    /** Damping factor for smooth movement */
    dampingFactor?: number;
    /** Auto-rotation speed */
    autoRotate?: boolean;
    autoRotateSpeed?: number;
}

export enum ControlType {
    ORBIT = 'orbit',
    TRACKBALL = 'trackball',
    FLY = 'fly',
    FIRST_PERSON = 'firstPerson',
    NONE = 'none'
}

export interface ControlRestrictions {
    minDistance?: number;
    maxDistance?: number;
    /** Min vertical angle */
    minPolarAngle?: number;
    /** Max vertical angle */
    maxPolarAngle?: number;
    minAzimuthAngle?: number;
    maxAzimuthAngle?: number;
    enablePan?: boolean;
    enableZoom?: boolean;
    enableRotate?: boolean;
    /** Zoom speed multiplier */
    zoomSpeed?: number;
    /** Rotation speed multiplier */
    rotateSpeed?: number;
}

// ============================================================================
// BRAND COLOR SYSTEM
// ============================================================================

export interface BrandColorScheme {
    brands: BrandInfo[];
    blendStrategy: BlendStrategy;
    /** Global color intensity multiplier 0-1 */
    intensity: number;
    zones: ColorZone[];
    reflections: ReflectionConfig;
    /** Allow brand colors to affect materials */
    affectMaterials?: boolean;
}

export interface BrandInfo {
    id: string;
    name: string;
    primaryColor: Color;
    secondaryColor?: Color;
    tertiaryColor?: Color;
    logoTexture?: string;
    emotionalTone: 'warm' | 'cool' | 'neutral' | 'vibrant';
    /** Accent color for highlights */
    accentColor?: Color;
}

export enum BlendStrategy {
    SEPARATED = 'separated',      // Distinct color zones
    GRADIENT = 'gradient',        // Smooth blend between colors
    REFLECTED = 'reflected',      // Only in reflections/specular
    SPOTLIT = 'spotlit',         // Individual colored spotlights
    ZONED = 'zoned',             // Geographic zones
    AMBIENT = 'ambient'          // Mixed in ambient lighting
}

export interface ColorZone {
    id: string;
    brandId: string;
    position: Vector3;
    color: Color;
    radius: number;
    /** Falloff curve 0-1 */
    falloff: number;
    shape: ZoneShape;
    /** Rotation for non-spherical shapes */
    rotation?: Vector3;
}

export enum ZoneShape {
    SPHERE = 'sphere',
    BOX = 'box',
    CONE = 'cone',
    CYLINDER = 'cylinder',
    PLANE = 'plane'
}

export interface ReflectionConfig {
    enabled: boolean;
    /** Reflection intensity 0-1 */
    intensity: number;
    /** Reflection blur 0-1 */
    blur: number;
    /** Allow brand color blending in reflections */
    mixBrands: boolean;
    /** Use cube camera for realtime reflections */
    realtime?: boolean;
}

// ============================================================================
// ASSET MANAGEMENT
// ============================================================================

export interface AssetManifest {
    models: ModelAsset[];
    textures: TextureAsset[];
    sounds: SoundAsset[];
    /** Total asset size in bytes */
    totalSize: number;
    /** Estimated load time in seconds */
    loadTime: number;
    /** Asset version for cache busting */
    version?: string;
}

export interface ModelAsset {
    id: string;
    path: string;
    format: ModelFormat;
    /** File size in bytes */
    size: number;
    polyCount: number;
    lod: LODVariant[];
    /** Material IDs referenced */
    materials: string[];
    boundingBox: BoundingBox;
    /** Preload this asset */
    preload?: boolean;
}

export enum ModelFormat {
    GLTF = 'gltf',
    GLB = 'glb',
    FBX = 'fbx',
    OBJ = 'obj',
    USDZ = 'usdz'
}

export interface LODVariant {
    level: number;
    path: string;
    polyCount: number;
    /** Switch distance in meters */
    distance: number;
}

export interface TextureAsset {
    id: string;
    path: string;
    format: TextureFormat;
    resolution: [number, number];
    /** File size in bytes */
    size: number;
    mipMaps: boolean;
    /** Color space hint */
    colorSpace?: 'srgb' | 'linear';
}

export interface SoundAsset {
    id: string;
    path: string;
    format: SoundFormat;
    /** Duration in seconds */
    duration: number;
    size: number;
    loop: boolean;
    volume: number;
    /** 3D positional audio */
    positional?: boolean;
    position?: Vector3;
}

export enum SoundFormat {
    MP3 = 'mp3',
    OGG = 'ogg',
    WAV = 'wav',
    AAC = 'aac'
}

export interface BoundingBox {
    min: Vector3;
    max: Vector3;
}

// ============================================================================
// POST-PROCESSING
// ============================================================================

export interface PostProcessingStack {
    enabled: boolean;
    passes: PostProcessPass[];
    /** Render at lower resolution for performance */
    resolution?: number;
}

export interface PostProcessPass {
    type: PassType;
    enabled: boolean;
    parameters: Record<string, unknown>;
    /** Render order */
    order: number;
}

export enum PassType {
    BLOOM = 'bloom',
    SSAO = 'ssao',
    SSR = 'ssr',
    DOF = 'dof',
    MOTION_BLUR = 'motionBlur',
    FXAA = 'fxaa',
    SMAA = 'smaa',
    TAA = 'taa',
    COLOR_CORRECTION = 'colorCorrection',
    VIGNETTE = 'vignette',
    CHROMATIC_ABERRATION = 'chromaticAberration',
    FILM_GRAIN = 'filmGrain',
    LENS_FLARE = 'lensFlare'
}

export interface BloomPassConfig {
    /** Luminance threshold */
    threshold: number;
    strength: number;
    radius: number;
    exposure: number;
}

export interface SSAOPassConfig {
    radius: number;
    intensity: number;
    bias: number;
    samples: number;
    /** Use half-resolution for performance */
    halfResolution?: boolean;
}

export interface SSRPassConfig {
    intensity: number;
    maxDistance: number;
    thickness: number;
    steps: number;
    /** Fade at screen edges */
    edgeFade?: number;
}

export interface DOFPassConfig {
    focusDistance: number;
    focalLength: number;
    bokehScale: number;
    /** Auto-focus on center object */
    autoFocus?: boolean;
}

// ============================================================================
// PERFORMANCE MONITORING
// ============================================================================

export interface PerformanceProfile {
    budget: PerformanceBudget;
    metrics: PerformanceMetrics;
    optimizations: Optimization[];
}

export interface PerformanceBudget {
    /** Target FPS */
    targetFPS: number;
    /** Max FPS cap */
    maxFPS: number;
    /** Max polygons */
    polyCount: number;
    /** Max draw calls */
    drawCalls: number;
    /** Texture memory budget in MB */
    textureMemory: number;
    /** VRAM budget in MB */
    vramUsage: number;
    /** Max acceptable load time in seconds */
    loadTime: number;
}

export interface PerformanceMetrics {
    currentFPS: number;
    polyCount: number;
    drawCalls: number;
    textureMemory: number;
    vramUsage: number;
    loadTime: number;
    timestamp: number;
    /** Frame render time in ms */
    frameTime?: number;
    /** GPU memory usage in MB */
    gpuMemory?: number;
}

export interface Optimization {
    type: OptimizationType;
    enabled: boolean;
    impact: 'low' | 'medium' | 'high';
    description: string;
    /** Auto-enable when performance drops */
    autoEnable?: boolean;
    /** FPS threshold to trigger */
    fpsThreshold?: number;
}

export enum OptimizationType {
    LOD = 'lod',
    FRUSTUM_CULLING = 'frustumCulling',
    OCCLUSION_CULLING = 'occlusionCulling',
    INSTANCING = 'instancing',
    TEXTURE_ATLASING = 'textureAtlasing',
    GEOMETRY_MERGING = 'geometryMerging',
    LAZY_LOADING = 'lazyLoading',
    COMPRESSION = 'compression',
    RENDER_RESOLUTION = 'renderResolution',
    SHADOW_RESOLUTION = 'shadowResolution',
    POST_PROCESSING = 'postProcessing'
}

// ============================================================================
// INTERACTION SYSTEM
// ============================================================================

export interface InteractionConfig {
    raycasting: RaycastConfig;
    hover: HoverConfig;
    click: ClickConfig;
    drag?: DragConfig;
    /** Double-click settings */
    doubleClick?: DoubleClickConfig;
}

export interface RaycastConfig {
    enabled: boolean;
    /** Three.js layers to raycast */
    layers: number[];
    /** Raycast precision */
    precision: number;
    /** Check for occlusion */
    respectOcclusion?: boolean;
}

export interface HoverConfig {
    enabled: boolean;
    cursor: CursorStyle;
    highlightColor?: Color;
    outlineWidth?: number;
    /** Show tooltip on hover */
    tooltip: boolean;
    /** Hover animation duration ms */
    animationDuration?: number;
}

export enum CursorStyle {
    AUTO = 'auto',
    POINTER = 'pointer',
    GRAB = 'grab',
    GRABBING = 'grabbing',
    ZOOM_IN = 'zoom-in',
    ZOOM_OUT = 'zoom-out',
    MOVE = 'move'
}

export interface ClickConfig {
    enabled: boolean;
    action: ClickAction;
    /** Animation duration in ms */
    animationDuration: number;
    /** Prevent event bubbling */
    stopPropagation?: boolean;
}

export enum ClickAction {
    FOCUS = 'focus',           // Move camera to product
    POPUP = 'popup',           // Show product details modal
    NAVIGATE = 'navigate',     // Go to product page
    SELECT = 'select',         // Multi-select mode
    CALLBACK = 'callback'      // Custom callback function
}

export interface DragConfig {
    enabled: boolean;
    axis: 'x' | 'y' | 'z' | 'xy' | 'xz' | 'yz' | 'xyz' | 'none';
    bounds?: BoundingBox;
    /** Snap to grid */
    snap?: number;
}

export interface DoubleClickConfig {
    enabled: boolean;
    /** Time window for double-click in ms */
    threshold: number;
    action: ClickAction;
}

// ============================================================================
// ENVIRONMENT REGISTRY
// ============================================================================

export interface EnvironmentRegistry {
    environments: Record<string, Environment3D>;
    templates: Record<string, EnvironmentTemplate>;
    presets: Record<string, PresetConfig>;
}

export interface EnvironmentTemplate {
    id: string;
    name: string;
    description: string;
    baseConfig: DeepPartial<Environment3D>;
    customization: CustomizationOptions;
}

export interface CustomizationOptions {
    allowBrandColors: boolean;
    allowProductSwap: boolean;
    allowLightingAdjustment: boolean;
    allowCameraPresets: boolean;
    allowMaterialOverrides?: boolean;
}

export interface PresetConfig {
    id: string;
    name: string;
    description: string;
    environmentId: string;
    overrides: DeepPartial<Environment3D>;
}

// ============================================================================
// RUNTIME CONTEXT
// ============================================================================

export interface EnvironmentContext {
    current: Environment3D | null;
    loading: boolean;
    error: Error | null;
    progress: LoadProgress;
    scene: THREE.Scene | null;
    camera: THREE.Camera | null;
    renderer: THREE.WebGLRenderer | null;
    /** Renderer memory stats */
    memory?: any;
    /** Renderer render info */
    info?: any;
}

export interface LoadProgress {
    loaded: number;
    total: number;
    percentage: number;
    currentAsset: string;
    /** Time elapsed in ms */
    elapsed?: number;
    /** Estimated time remaining in ms */
    remaining?: number;
}

// ============================================================================
// EVENT SYSTEM
// ============================================================================

export interface Environment3DEvents {
    onLoad?: (environment: Environment3D) => void;
    onLoadProgress?: (progress: LoadProgress) => void;
    onLoadError?: (error: Error) => void;
    onProductClick?: (productId: string, productData: unknown) => void;
    onProductHover?: (productId: string | null) => void;
    onCameraChange?: (camera: CameraConfig) => void;
    onPerformanceWarning?: (metrics: PerformanceMetrics) => void;
    onResize?: (width: number, height: number) => void;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export type DeepPartial<T> = {
    [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type ReadonlyDeep<T> = {
    readonly [P in keyof T]: T[P] extends object ? ReadonlyDeep<T[P]> : T[P];
};

/**
 * Helper to extract type of array elements
 */
export type ArrayElement<T> = T extends (infer U)[] ? U : never;

/**
 * Make specific fields optional
 */
export type PartialFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * Configuration validation result
 */
export interface ValidationResult {
    valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
}

export interface ValidationError {
    field: string;
    message: string;
    code: string;
}

export interface ValidationWarning {
    field: string;
    message: string;
    suggestion?: string;
}
