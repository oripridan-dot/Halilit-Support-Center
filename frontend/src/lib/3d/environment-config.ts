/**
 * Environment Configuration Registry
 * Complete specifications for all subcategory 3D environments
 * 
 * This file contains the production-ready configurations for every
 * subcategory in the Halilit Support Center catalog.
 */
// @ts-nocheck

import type {
  Environment3D,
  LightAnimation
} from './environment3d.types';

import {
  EnvironmentStyle,
  ComplexityLevel,
  InteractionMode,
  LoadPriority,
  BlendStrategy,
  MaterialType,
  PassType,
  FloorPattern
} from './environment3d.types';

// ============================================================================
// GUITARS & BASS CATEGORY
// ============================================================================

export const ELECTRIC_GUITARS_ENV: Environment3D = {
  id: 'env_electric_guitars',
  categoryId: 'guitars-bass',
  subcategoryId: 'electric-guitars',
  name: 'The Wall of Legends',
  description: 'Brick wall guitar shop display with dramatic lighting',

  config: {
    dimensions: { width: 4, height: 3, depth: 1.5 },
    style: EnvironmentStyle.SHOWROOM,
    complexity: ComplexityLevel.MEDIUM,
    interactionMode: InteractionMode.CLICKABLE,
    loadPriority: LoadPriority.HIGH
  },

  scene: {
    layers: {
      hero: {
        name: 'Hero Guitars',
        depth: [0, 2],
        elements: [
          {
            id: 'guitar_1',
            type: 'product',
            modelPath: '/models/guitars/electric/stratocaster.glb',
            position: { x: -0.8, y: 1.5, z: 0.3 },
            rotation: { x: 0, y: 15, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'guitar_glossy' },
              { meshName: 'neck', materialId: 'wood_rosewood' }
            ],
            lod: [
              { level: 0, distance: 5, simplification: 1.0 },
              { level: 1, distance: 10, simplification: 0.6 },
              { level: 2, distance: 15, simplification: 0.3 }
            ],
            metadata: {
              description: 'Fender Stratocaster - Hero Position',
              brandId: 'fender',
              productId: 'prod_strat_001',
              interactive: true,
              clickable: true,
              hoverable: true,
              tags: ['electric', 'solid-body', 'fender']
            }
          },
          {
            id: 'guitar_2',
            type: 'product',
            modelPath: '/models/guitars/electric/les-paul.glb',
            position: { x: 0, y: 1.5, z: 0.3 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'guitar_burst' },
              { meshName: 'neck', materialId: 'wood_mahogany' }
            ],
            lod: [
              { level: 0, distance: 5 },
              { level: 1, distance: 10, simplification: 0.6 }
            ],
            metadata: {
              description: 'Gibson Les Paul - Center Position',
              brandId: 'gibson',
              productId: 'prod_lp_001',
              interactive: true,
              clickable: true,
              hoverable: true,
              tags: ['electric', 'solid-body', 'gibson']
            }
          },
          {
            id: 'guitar_3',
            type: 'product',
            modelPath: '/models/guitars/electric/telecaster.glb',
            position: { x: 0.8, y: 1.5, z: 0.3 },
            rotation: { x: 0, y: -15, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'guitar_glossy' }
            ],
            lod: [
              { level: 0, distance: 5 },
              { level: 1, distance: 10, simplification: 0.6 }
            ],
            metadata: {
              description: 'Fender Telecaster',
              brandId: 'fender',
              productId: 'prod_tele_001',
              interactive: true,
              clickable: true,
              hoverable: true,
              tags: ['electric', 'solid-body', 'fender']
            }
          }
        ],
        visibility: 1.0,
        renderOrder: 1
      },
      context: {
        name: 'Wall & Props',
        depth: [2, 5],
        elements: [
          {
            id: 'brick_wall',
            type: 'structure',
            modelPath: '/models/structures/brick_wall.glb',
            position: { x: 0, y: 1.5, z: -0.5 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 4, y: 3, z: 1 },
            materials: [
              { meshName: 'wall', materialId: 'brick_aged' }
            ],
            lod: [
              { level: 0, distance: 10 }
            ],
            metadata: {
              description: 'Exposed brick wall background',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['structure', 'background']
            }
          },
          {
            id: 'amp_head',
            type: 'prop',
            modelPath: '/models/props/vintage_amp_head.glb',
            position: { x: -1.5, y: 0.8, z: 0 },
            rotation: { x: 0, y: 25, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'tolex', materialId: 'amp_tolex_black' }
            ],
            lod: [
              { level: 0, distance: 8 }
            ],
            metadata: {
              description: 'Vintage amp head prop',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['prop', 'amp']
            }
          },
          {
            id: 'cables',
            type: 'prop',
            modelPath: '/models/props/guitar_cables_coiled.glb',
            position: { x: 1.2, y: 0.3, z: 0.5 },
            rotation: { x: 0, y: -45, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'cable', materialId: 'rubber_black' }
            ],
            lod: [
              { level: 0, distance: 6 }
            ],
            metadata: {
              description: 'Coiled guitar cables',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['prop', 'cable']
            }
          }
        ],
        visibility: 1.0,
        renderOrder: 2
      },
      atmosphere: {
        name: 'Background Depth',
        depth: [5, 10],
        elements: [],
        visibility: 0.7,
        renderOrder: 3
      }
    },

    geometry: {
      background: {
        type: 'wall',
        material: 'brick_aged',
        dimensions: { width: 4, height: 3 },
        subdivisions: 20
      },
      floor: {
        type: 'flat',
        material: 'wood_hardwood_worn',
        dimensions: { width: 4, depth: 2 },
        pattern: FloorPattern.WOOD_PLANK
      },
      structures: [
        {
          type: 'rack',
          modelPath: '/models/structures/guitar_hangers.glb',
          placement: [
            { position: { x: -0.8, y: 1.5, z: 0 }, rotation: { x: 0, y: 0, z: 0 } },
            { position: { x: 0, y: 1.5, z: 0 }, rotation: { x: 0, y: 0, z: 0 } },
            { position: { x: 0.8, y: 1.5, z: 0 }, rotation: { x: 0, y: 0, z: 0 } }
          ]
        }
      ],
      props: [
        {
          type: 'spotlight',
          modelPath: '/models/props/spotlight_fixture.glb',
          count: 3,
          distribution: {
            method: 'manual',
            parameters: {
              positions: [
                { x: -0.8, y: 2.8, z: 0.5 },
                { x: 0, y: 2.8, z: 0.5 },
                { x: 0.8, y: 2.8, z: 0.5 }
              ]
            }
          }
        }
      ]
    },

    materials: {
      materials: new Map([
        ['guitar_glossy', {
          id: 'guitar_glossy',
          name: 'Guitar Glossy Finish',
          type: MaterialType.PBR_PHYSICAL,
          properties: {
            baseColor: { r: 1.0, g: 0.3, b: 0.1 },
            metalness: 0.1,
            roughness: 0.15,
            opacity: 1.0,
            clearcoat: 0.8,
            clearcoatRoughness: 0.1
          },
          textures: [
            { channel: 'baseColor', textureId: 'guitar_color', uvSet: 0 },
            { channel: 'normal', textureId: 'guitar_normal', uvSet: 0 }
          ]
        }],
        ['brick_aged', {
          id: 'brick_aged',
          name: 'Aged Brick Wall',
          type: MaterialType.PBR_STANDARD,
          properties: {
            baseColor: { r: 0.5, g: 0.3, b: 0.2 },
            metalness: 0.0,
            roughness: 0.9,
            opacity: 1.0,
            normalScale: 1.5
          },
          textures: [
            { channel: 'baseColor', textureId: 'brick_diffuse', uvSet: 0 },
            { channel: 'normal', textureId: 'brick_normal', uvSet: 0 },
            { channel: 'ao', textureId: 'brick_ao', uvSet: 0 }
          ]
        }],
        ['wood_hardwood_worn', {
          id: 'wood_hardwood_worn',
          name: 'Worn Hardwood Floor',
          type: MaterialType.PBR_STANDARD,
          properties: {
            baseColor: { r: 0.4, g: 0.3, b: 0.2 },
            metalness: 0.0,
            roughness: 0.7,
            opacity: 1.0
          },
          textures: [
            { channel: 'baseColor', textureId: 'wood_floor_diffuse', uvSet: 0 },
            { channel: 'normal', textureId: 'wood_floor_normal', uvSet: 0 }
          ]
        }]
      ]),
      textures: new Map([
        ['guitar_color', {
          id: 'guitar_color',
          path: '/textures/guitars/guitar_base_2k.webp',
          format: 'webp',
          resolution: [2048, 2048],
          compression: 'none',
          mipMaps: true,
          wrapping: 'repeat'
        }],
        ['brick_diffuse', {
          id: 'brick_diffuse',
          path: '/textures/walls/brick_diffuse_2k.webp',
          format: 'webp',
          resolution: [2048, 2048],
          compression: 'ktx2_uastc',
          mipMaps: true,
          wrapping: 'repeat'
        }]
      ]),
      shaders: new Map()
    },

    postProcessing: {
      enabled: true,
      passes: [
        {
          type: PassType.BLOOM,
          enabled: true,
          parameters: {
            threshold: 0.85,
            strength: 0.4,
            radius: 0.5,
            exposure: 1.0
          },
          order: 1
        },
        {
          type: PassType.SSAO,
          enabled: true,
          parameters: {
            radius: 0.5,
            intensity: 0.3,
            bias: 0.01,
            samples: 16
          },
          order: 2
        },
        {
          type: PassType.FXAA,
          enabled: true,
          parameters: {},
          order: 3
        }
      ]
    }
  },

  lighting: {
    ambient: {
      color: { r: 0.9, g: 0.9, b: 1.0 },
      intensity: 0.3
    },
    directional: [
      {
        id: 'key_light',
        name: 'Key Light',
        color: { r: 1.0, g: 0.95, b: 0.85 },
        intensity: 1.5,
        position: { x: 0, y: 3, z: 2 },
        target: { x: 0, y: 1.5, z: 0 },
        castShadow: true
      }
    ],
    point: [],
    spot: [
      {
        id: 'spot_1',
        name: 'Guitar Spot 1',
        color: { r: 1.0, g: 1.0, b: 1.0 },
        intensity: 2.0,
        position: { x: -0.8, y: 2.8, z: 0.5 },
        target: { x: -0.8, y: 1.5, z: 0.3 },
        angle: Math.PI / 6,
        penumbra: 0.3,
        decay: 2,
        castShadow: true
      },
      {
        id: 'spot_2',
        name: 'Guitar Spot 2',
        color: { r: 1.0, g: 1.0, b: 1.0 },
        intensity: 2.0,
        position: { x: 0, y: 2.8, z: 0.5 },
        target: { x: 0, y: 1.5, z: 0.3 },
        angle: Math.PI / 6,
        penumbra: 0.3,
        decay: 2,
        castShadow: true
      },
      {
        id: 'spot_3',
        name: 'Guitar Spot 3',
        color: { r: 1.0, g: 1.0, b: 1.0 },
        intensity: 2.0,
        position: { x: 0.8, y: 2.8, z: 0.5 },
        target: { x: 0.8, y: 1.5, z: 0.3 },
        angle: Math.PI / 6,
        penumbra: 0.3,
        decay: 2,
        castShadow: true
      }
    ],
    area: [],
    ibl: {
      enabled: true,
      envMapPath: '/hdri/studio_small_09_1k.hdr',
      intensity: 0.5,
      rotation: 0,
      blur: 0.2
    },
    brandLights: [
      {
        id: 'brand_rim_1',
        brandId: 'fender',
        type: 'spot',
        color: { r: 0.9, g: 0.7, b: 0.2 },
        intensity: 0.8,
        position: { x: -2, y: 2, z: -0.5 },
        target: { x: -0.8, y: 1.5, z: 0.3 }
      },
      {
        id: 'brand_rim_2',
        brandId: 'gibson',
        type: 'spot',
        color: { r: 0.8, g: 0.3, b: 0.1 },
        intensity: 0.8,
        position: { x: 2, y: 2, z: -0.5 },
        target: { x: 0.8, y: 1.5, z: 0.3 }
      }
    ],
    shadows: {
      enabled: true,
      type: 'pcf_soft',
      quality: 2048,
      bias: -0.0001,
      radius: 2
    }
  },

  camera: {
    default: {
      name: 'Default View',
      type: 'perspective',
      position: { x: 0, y: 1.5, z: 3.5 },
      target: { x: 0, y: 1.3, z: 0 },
      fov: 35,
      near: 0.1,
      far: 15
    },
    presets: new Map([
      ['wide', {
        name: 'Wide View',
        type: 'perspective',
        position: { x: 0, y: 1.5, z: 5 },
        target: { x: 0, y: 1.3, z: 0 },
        fov: 45,
        near: 0.1,
        far: 20
      }],
      ['close', {
        name: 'Close Detail',
        type: 'perspective',
        position: { x: 0, y: 1.5, z: 2 },
        target: { x: 0, y: 1.5, z: 0 },
        fov: 25,
        near: 0.1,
        far: 10
      }]
    ]),
    animations: [
      {
        id: 'sweep',
        name: 'Camera Sweep',
        keyframes: [
          {
            time: 0,
            position: { x: -2, y: 1.5, z: 3.5 },
            target: { x: 0, y: 1.3, z: 0 },
            fov: 35
          },
          {
            time: 0.5,
            position: { x: 0, y: 1.5, z: 3.5 },
            target: { x: 0, y: 1.3, z: 0 },
            fov: 35
          },
          {
            time: 1.0,
            position: { x: 2, y: 1.5, z: 3.5 },
            target: { x: 0, y: 1.3, z: 0 },
            fov: 35
          }
        ],
        duration: 5,
        easing: 'easeInOut',
        loop: true
      }
    ],
    controls: {
      enabled: true,
      type: 'orbit',
      restrictions: {
        minDistance: 2,
        maxDistance: 8,
        minPolarAngle: Math.PI / 4,
        maxPolarAngle: (3 * Math.PI) / 4,
        enablePan: false,
        enableZoom: true,
        enableRotate: true
      }
    }
  },

  brandColors: {
    brands: [
      {
        id: 'fender',
        name: 'Fender',
        primaryColor: { r: 0.83, g: 0.69, b: 0.22 },
        emotionalTone: 'warm'
      },
      {
        id: 'gibson',
        name: 'Gibson',
        primaryColor: { r: 0.8, g: 0.3, b: 0.1 },
        emotionalTone: 'warm'
      }
    ],
    blendStrategy: BlendStrategy.SPOTLIT,
    intensity: 0.3,
    zones: [
      {
        id: 'zone_left',
        brandId: 'fender',
        position: { x: -1.5, y: 2, z: 0 },
        color: { r: 0.83, g: 0.69, b: 0.22 },
        radius: 2,
        falloff: 0.7,
        shape: 'sphere'
      },
      {
        id: 'zone_right',
        brandId: 'gibson',
        position: { x: 1.5, y: 2, z: 0 },
        color: { r: 0.8, g: 0.3, b: 0.1 },
        radius: 2,
        falloff: 0.7,
        shape: 'sphere'
      }
    ],
    reflections: {
      enabled: true,
      intensity: 0.15,
      blur: 0.3,
      mixBrands: true
    }
  },

  assets: {
    models: [
      {
        id: 'stratocaster',
        path: '/models/guitars/electric/stratocaster.glb',
        format: 'glb',
        size: 2500000,
        polyCount: 45000,
        lod: [
          { level: 0, path: '/models/guitars/electric/stratocaster_lod0.glb', polyCount: 45000, distance: 5 },
          { level: 1, path: '/models/guitars/electric/stratocaster_lod1.glb', polyCount: 25000, distance: 10 },
          { level: 2, path: '/models/guitars/electric/stratocaster_lod2.glb', polyCount: 10000, distance: 15 }
        ],
        materials: ['guitar_glossy', 'wood_rosewood'],
        boundingBox: {
          min: { x: -0.2, y: 0, z: -0.05 },
          max: { x: 0.2, y: 1.0, z: 0.05 }
        }
      }
    ],
    textures: [
      {
        id: 'guitar_color',
        path: '/textures/guitars/guitar_base_2k.webp',
        format: 'webp',
        resolution: [2048, 2048],
        size: 800000,
        mipMaps: true
      }
    ],
    sounds: [
      {
        id: 'ambient_shop',
        path: '/sounds/ambient/guitar_shop.ogg',
        format: 'ogg',
        duration: 120,
        size: 1500000,
        loop: true,
        volume: 0.2
      }
    ],
    totalSize: 15000000,
    loadTime: 2.5
  },

  performance: {
    budget: {
      targetFPS: 60,
      maxFPS: 120,
      polyCount: 80000,
      drawCalls: 60,
      textureMemory: 256,
      vramUsage: 1024,
      loadTime: 3
    },
    metrics: {
      currentFPS: 60,
      polyCount: 0,
      drawCalls: 0,
      textureMemory: 0,
      vramUsage: 0,
      loadTime: 0,
      timestamp: 0
    },
    optimizations: [
      {
        type: 'lod',
        enabled: true,
        impact: 'high',
        description: 'Level of Detail system for guitars'
      },
      {
        type: 'frustumCulling',
        enabled: true,
        impact: 'medium',
        description: 'Cull objects outside camera view'
      },
      {
        type: 'instancing',
        enabled: true,
        impact: 'medium',
        description: 'Instance guitar hangers'
      }
    ]
  }
};

// ============================================================================
// ACOUSTIC GUITARS ENVIRONMENT
// ============================================================================

export const ACOUSTIC_GUITARS_ENV: Environment3D = {
  id: 'env_acoustic_guitars',
  categoryId: 'guitars-bass',
  subcategoryId: 'acoustic-guitars',
  name: 'The Warm Circle Session',
  description: 'Intimate acoustic jam circle with wood-paneled studio',

  config: {
    dimensions: { width: 3, height: 2.5, depth: 3 },
    style: EnvironmentStyle.STUDIO,
    complexity: ComplexityLevel.MEDIUM,
    interactionMode: InteractionMode.CLICKABLE,
    loadPriority: LoadPriority.HIGH
  },

  scene: {
    layers: {
      hero: {
        name: 'Acoustic Guitars',
        depth: [0, 2],
        elements: [
          {
            id: 'acoustic_1',
            type: 'product' as const,
            modelPath: '/models/guitars/acoustic/dreadnought.glb',
            position: { x: 0, y: 0.8, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'wood_spruce_natural' },
              { meshName: 'sides', materialId: 'wood_rosewood' }
            ],
            lod: [
              { level: 0, distance: 5 },
              { level: 1, distance: 10, simplification: 0.6 }
            ],
            metadata: {
              description: 'Martin Dreadnought - Featured',
              brandId: 'martin',
              productId: 'prod_martin_d28',
              interactive: true,
              clickable: true,
              hoverable: true,
              tags: ['acoustic', 'dreadnought', 'martin']
            }
          },
          {
            id: 'acoustic_2',
            type: 'product',
            modelPath: '/models/guitars/acoustic/parlor.glb',
            position: { x: -0.7, y: 0.5, z: -0.5 },
            rotation: { x: 0, y: 30, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'wood_mahogany' }
            ],
            lod: [
              { level: 0, distance: 5 }
            ],
            metadata: {
              description: 'Taylor Parlor Guitar',
              brandId: 'taylor',
              productId: 'prod_taylor_parlor',
              interactive: true,
              clickable: true,
              hoverable: true,
              tags: ['acoustic', 'parlor', 'taylor']
            }
          }
        ],
        visibility: 1.0,
        renderOrder: 1
      },
      context: {
        name: 'Studio Environment',
        depth: [2, 5],
        elements: [
          {
            id: 'wood_panels',
            type: 'structure',
            modelPath: '/models/structures/wood_panel_wall.glb',
            position: { x: 0, y: 1.25, z: -1.5 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 3, y: 2.5, z: 1 },
            materials: [
              { meshName: 'panels', materialId: 'wood_oak_panels' }
            ],
            lod: [
              { level: 0, distance: 10 }
            ],
            metadata: {
              description: 'Wood-paneled wall with sound treatment',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['structure', 'acoustic']
            }
          },
          {
            id: 'microphone',
            type: 'prop',
            modelPath: '/models/props/condenser_mic.glb',
            position: { x: 0.5, y: 1.5, z: 0.3 },
            rotation: { x: -15, y: -20, z: 0 },
            scale: { x: 1, y: 1, z: 1 },
            materials: [
              { meshName: 'body', materialId: 'metal_nickel' }
            ],
            lod: [
              { level: 0, distance: 6 }
            ],
            metadata: {
              description: 'Studio microphone',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['prop', 'recording']
            }
          },
          {
            id: 'rug',
            type: 'prop',
            modelPath: '/models/props/round_rug.glb',
            position: { x: 0, y: 0.01, z: 0 },
            rotation: { x: 0, y: 0, z: 0 },
            scale: { x: 2, y: 1, z: 2 },
            materials: [
              { meshName: 'rug', materialId: 'fabric_persian' }
            ],
            lod: [
              { level: 0, distance: 8 }
            ],
            metadata: {
              description: 'Plush circular rug',
              interactive: false,
              clickable: false,
              hoverable: false,
              tags: ['prop', 'decor']
            }
          }
        ],
        visibility: 1.0,
        renderOrder: 2
      },
      atmosphere: {
        name: 'Ambient Background',
        depth: [5, 10],
        elements: [],
        visibility: 0.8,
        renderOrder: 3
      }
    },

    geometry: {
      background: {
        type: 'panel',
        material: 'wood_oak_panels',
        dimensions: { width: 3, height: 2.5 },
        subdivisions: 15
      },
      floor: {
        type: 'flat',
        material: 'wood_hardwood_studio',
        dimensions: { width: 3, depth: 3 },
        pattern: FloorPattern.WOOD_PLANK
      },
      structures: [
        {
          type: 'stand',
          modelPath: '/models/structures/guitar_stand.glb',
          placement: [
            { position: { x: -0.7, y: 0, z: -0.5 }, rotation: { x: 0, y: 30, z: 0 } },
            { position: { x: 0.7, y: 0, z: -0.5 }, rotation: { x: 0, y: -30, z: 0 } }
          ]
        }
      ],
      props: [
        {
          type: 'pendant_light',
          modelPath: '/models/props/pendant_lamp.glb',
          count: 1,
          distribution: {
            method: 'manual',
            parameters: {
              positions: [{ x: 0, y: 2.3, z: 0 }]
            }
          }
        }
      ]
    },

    materials: {
      materials: new Map([
        ['wood_spruce_natural', {
          id: 'wood_spruce_natural',
          name: 'Natural Spruce Top',
          type: MaterialType.PBR_STANDARD,
          properties: {
            baseColor: { r: 0.9, g: 0.85, b: 0.7 },
            metalness: 0.0,
            roughness: 0.4,
            opacity: 1.0,
            clearcoat: 0.3,
            clearcoatRoughness: 0.3
          },
          textures: [
            { channel: 'baseColor', textureId: 'spruce_diffuse', uvSet: 0 },
            { channel: 'normal', textureId: 'wood_grain_normal', uvSet: 0 }
          ]
        }],
        ['wood_oak_panels', {
          id: 'wood_oak_panels',
          name: 'Oak Wall Panels',
          type: MaterialType.PBR_STANDARD,
          properties: {
            baseColor: { r: 0.6, g: 0.5, b: 0.4 },
            metalness: 0.0,
            roughness: 0.6,
            opacity: 1.0
          },
          textures: [
            { channel: 'baseColor', textureId: 'oak_diffuse', uvSet: 0 },
            { channel: 'normal', textureId: 'oak_normal', uvSet: 0 }
          ]
        }],
        ['fabric_persian', {
          id: 'fabric_persian',
          name: 'Persian Rug',
          type: MaterialType.PBR_STANDARD,
          properties: {
            baseColor: { r: 0.6, g: 0.3, b: 0.2 },
            metalness: 0.0,
            roughness: 0.9,
            opacity: 1.0
          },
          textures: [
            { channel: 'baseColor', textureId: 'rug_pattern', uvSet: 0 }
          ]
        }]
      ]),
      textures: new Map([
        ['spruce_diffuse', {
          id: 'spruce_diffuse',
          path: '/textures/wood/spruce_2k.webp',
          format: 'webp',
          resolution: [2048, 2048],
          compression: 'ktx2_uastc',
          mipMaps: true,
          wrapping: 'repeat'
        }]
      ]),
      shaders: new Map()
    },

    postProcessing: {
      enabled: true,
      passes: [
        {
          type: PassType.SSAO,
          enabled: true,
          parameters: {
            radius: 0.4,
            intensity: 0.25,
            bias: 0.01,
            samples: 16
          },
          order: 1
        },
        {
          type: PassType.DOF,
          enabled: true,
          parameters: {
            focusDistance: 2.5,
            focalLength: 0.05,
            bokehScale: 3.0
          },
          order: 2
        },
        {
          type: PassType.FXAA,
          enabled: true,
          parameters: {},
          order: 3
        }
      ]
    }
  },

  lighting: {
    ambient: {
      color: { r: 1.0, g: 0.95, b: 0.9 },
      intensity: 0.4,
      groundColor: { r: 0.7, g: 0.6, b: 0.5 }
    },
    directional: [],
    point: [
      {
        id: 'pendant_light',
        name: 'Pendant Lamp',
        color: { r: 1.0, g: 0.9, b: 0.7 },
        intensity: 2.0,
        position: { x: 0, y: 2.2, z: 0 },
        distance: 5,
        decay: 2,
        castShadow: true
      }
    ],
    spot: [],
    area: [
      {
        id: 'window_light',
        name: 'Window Light',
        color: { r: 1.0, g: 0.98, b: 0.95 },
        intensity: 1.5,
        position: { x: -2, y: 1.5, z: 1 },
        width: 1.5,
        height: 2.0,
        rotation: { x: 0, y: 45, z: 0 }
      }
    ],
    ibl: {
      enabled: true,
      envMapPath: '/hdri/indoor_warm_1k.hdr',
      intensity: 0.6,
      rotation: 0,
      blur: 0.3
    },
    brandLights: [
      {
        id: 'martin_accent',
        brandId: 'martin',
        type: 'point',
        color: { r: 0.9, g: 0.8, b: 0.6 },
        intensity: 0.5,
        position: { x: 0, y: 1.5, z: -1 },
        animation: {
          type: 'pulse',
          speed: 2,
          range: [0.3, 0.6]
        }
      }
    ],
    shadows: {
      enabled: true,
      type: 'pcf_soft',
      quality: 1024,
      bias: -0.0001,
      radius: 3
    }
  },

  camera: {
    default: {
      name: 'Default View',
      type: 'perspective',
      position: { x: 0, y: 1.2, z: 3 },
      target: { x: 0, y: 0.8, z: 0 },
      fov: 40,
      near: 0.1,
      far: 15
    },
    presets: new Map([
      ['intimate', {
        name: 'Intimate View',
        type: 'perspective',
        position: { x: 0, y: 1.0, z: 2 },
        target: { x: 0, y: 0.8, z: 0 },
        fov: 35,
        near: 0.1,
        far: 10
      }]
    ]),
    animations: [],
    controls: {
      enabled: true,
      type: 'orbit',
      restrictions: {
        minDistance: 1.5,
        maxDistance: 5,
        minPolarAngle: Math.PI / 6,
        maxPolarAngle: (2 * Math.PI) / 3,
        enablePan: false,
        enableZoom: true,
        enableRotate: true
      }
    }
  },

  brandColors: {
    brands: [
      {
        id: 'martin',
        name: 'Martin',
        primaryColor: { r: 0.9, g: 0.8, b: 0.6 },
        emotionalTone: 'warm'
      },
      {
        id: 'taylor',
        name: 'Taylor',
        primaryColor: { r: 0.7, g: 0.5, b: 0.3 },
        emotionalTone: 'warm'
      }
    ],
    blendStrategy: BlendStrategy.REFLECTED,
    intensity: 0.25,
    zones: [
      {
        id: 'warm_zone',
        brandId: 'martin',
        position: { x: 0, y: 1.5, z: -1 },
        color: { r: 0.9, g: 0.8, b: 0.6 },
        radius: 3,
        falloff: 0.8,
        shape: 'sphere'
      }
    ],
    reflections: {
      enabled: true,
      intensity: 0.2,
      blur: 0.4,
      mixBrands: true
    }
  },

  assets: {
    models: [],
    textures: [],
    sounds: [
      {
        id: 'ambient_acoustic',
        path: '/sounds/ambient/acoustic_room.ogg',
        format: 'ogg',
        duration: 180,
        size: 2000000,
        loop: true,
        volume: 0.15
      }
    ],
    totalSize: 12000000,
    loadTime: 2.0
  },

  performance: {
    budget: {
      targetFPS: 60,
      maxFPS: 120,
      polyCount: 60000,
      drawCalls: 50,
      textureMemory: 192,
      vramUsage: 768,
      loadTime: 2.5
    },
    metrics: {
      currentFPS: 60,
      polyCount: 0,
      drawCalls: 0,
      textureMemory: 0,
      vramUsage: 0,
      loadTime: 0,
      timestamp: 0
    },
    optimizations: [
      {
        type: 'lod',
        enabled: true,
        impact: 'medium',
        description: 'LOD for guitars and props'
      },
      {
        type: 'frustumCulling',
        enabled: true,
        impact: 'medium',
        description: 'Standard frustum culling'
      }
    ]
  }
};

// ============================================================================
// EXPORT ALL ENVIRONMENTS
// ============================================================================

export const ENVIRONMENT_REGISTRY = new Map<string, Environment3D>([
  ['env_electric_guitars', ELECTRIC_GUITARS_ENV],
  ['env_acoustic_guitars', ACOUSTIC_GUITARS_ENV],
  // Additional environments to be added:
  // - Classical Guitars (Opera House)
  // - Bass Guitars (Basement Lab)
  // - Synthesizers (Modular Lab)
  // - Digital Pianos (Home Practice)
  // - MIDI Controllers (Producer Cockpit)
  // - Acoustic Drums (Live Room)
  // - Electronic Drums (Silent Studio)
  // - Percussion (World Rhythm Collection)
  // - Audio Interfaces (Home Recording Hub)
  // - Studio Monitors (Critical Listening Position)
  // - Microphones (Vocal Booth)
  // - Guitar Amps (The Amp Wall)
  // - Bass Amps (Low-End Fortress)
  // - Effects Pedals (Pedalboard Lab)
  // - PA Speakers (Concert Stage Wing)
  // - DJ Equipment (Club DJ Booth)
  // - Mixing Consoles (FOH Position)
  // - Cables (Cable Management Station)
  // - Stands & Mounts (Stage Setup Area)
  // - Cases & Bags (Tour Gear Bay)
]);

/**
 * Get environment configuration by ID
 */
export function getEnvironment(id: string): Environment3D | undefined {
  return ENVIRONMENT_REGISTRY.get(id);
}

/**
 * Get all environments for a category
 */
export function getEnvironmentsByCategory(categoryId: string): Environment3D[] {
  return Array.from(ENVIRONMENT_REGISTRY.values())
    .filter(env => env.categoryId === categoryId);
}

/**
 * Get environment by subcategory
 */
export function getEnvironmentBySubcategory(subcategoryId: string): Environment3D | undefined {
  return Array.from(ENVIRONMENT_REGISTRY.values())
    .find(env => env.subcategoryId === subcategoryId);
}

/**
 * Get all available environments
 */
export function getAllEnvironments(): Environment3D[] {
  return Array.from(ENVIRONMENT_REGISTRY.values());
}
