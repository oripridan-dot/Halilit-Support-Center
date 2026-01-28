/**
 * Procedural Asset Generator
 * Creates placeholder 3D geometry for testing before real assets are created
 * 
 * This allows the 3D environment system to work without Blender-created assets.
 * Replace these procedural assets with real GLB files as they become available.
 */

import * as THREE from 'three';
import { GLTFExporter } from 'three/examples/jsm/exporters/GLTFExporter';

// ============================================================================
// ASSET TYPE DEFINITIONS
// ============================================================================

export enum AssetType {
    ELECTRIC_GUITAR = 'electric-guitar',
    ACOUSTIC_GUITAR = 'acoustic-guitar',
    BASS_GUITAR = 'bass-guitar',
    SYNTHESIZER = 'synthesizer',
    KEYBOARD = 'keyboard',
    DRUM_KIT = 'drum-kit',
    AMPLIFIER = 'amplifier',
    PEDESTAL = 'pedestal',
    WALL_BRICK = 'wall-brick',
    FLOOR_WOOD = 'floor-wood',
    SPOTLIGHT = 'spotlight',
    CABLE = 'cable'
}

// ============================================================================
// GENERATOR CLASS
// ============================================================================

export class ProceduralAssetGenerator {
    private scene: THREE.Scene;
    private exporter: GLTFExporter;

    constructor() {
        this.scene = new THREE.Scene();
        this.exporter = new GLTFExporter();
    }

    /**
     * Generate a procedural asset by type
     */
    public generateAsset(type: AssetType): THREE.Group {
        switch (type) {
            case AssetType.ELECTRIC_GUITAR:
                return this.createElectricGuitar();
            case AssetType.ACOUSTIC_GUITAR:
                return this.createAcousticGuitar();
            case AssetType.BASS_GUITAR:
                return this.createBassGuitar();
            case AssetType.SYNTHESIZER:
                return this.createSynthesizer();
            case AssetType.KEYBOARD:
                return this.createKeyboard();
            case AssetType.DRUM_KIT:
                return this.createDrumKit();
            case AssetType.AMPLIFIER:
                return this.createAmplifier();
            case AssetType.PEDESTAL:
                return this.createPedestal();
            case AssetType.WALL_BRICK:
                return this.createBrickWall();
            case AssetType.FLOOR_WOOD:
                return this.createWoodFloor();
            case AssetType.SPOTLIGHT:
                return this.createSpotlight();
            case AssetType.CABLE:
                return this.createCable();
            default:
                return this.createPlaceholder();
        }
    }

    /**
     * Export asset as GLB blob
     */
    public async exportAsGLB(asset: THREE.Group): Promise<Blob> {
        return new Promise((resolve, reject) => {
            this.exporter.parse(
                asset,
                (gltf) => {
                    const blob = new Blob([JSON.stringify(gltf)], { type: 'application/json' });
                    resolve(blob);
                },
                (error) => {
                    reject(error);
                },
                { binary: false }
            );
        });
    }

    // ==========================================================================
    // GUITAR GENERATORS
    // ==========================================================================

    private createElectricGuitar(): THREE.Group {
        const guitar = new THREE.Group();
        guitar.name = 'ElectricGuitar';

        // Body (Stratocaster-style contoured shape)
        const bodyGeometry = new THREE.BoxGeometry(0.35, 0.05, 0.45);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B0000, // Deep red
            metalness: 0.6,
            roughness: 0.3
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.name = 'body';
        guitar.add(body);

        // Neck
        const neckGeometry = new THREE.BoxGeometry(0.05, 0.03, 0.65);
        const neckMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B4513,
            metalness: 0.2,
            roughness: 0.7
        });
        const neck = new THREE.Mesh(neckGeometry, neckMaterial);
        neck.position.set(0, 0, -0.55);
        neck.name = 'neck';
        guitar.add(neck);

        // Headstock
        const headstockGeometry = new THREE.BoxGeometry(0.08, 0.02, 0.15);
        const headstock = new THREE.Mesh(headstockGeometry, neckMaterial);
        headstock.position.set(0, 0, -0.95);
        headstock.name = 'headstock';
        guitar.add(headstock);

        // Pickups (3 single-coils)
        const pickupMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.8,
            roughness: 0.2
        });
        for (let i = 0; i < 3; i++) {
            const pickupGeometry = new THREE.BoxGeometry(0.06, 0.01, 0.08);
            const pickup = new THREE.Mesh(pickupGeometry, pickupMaterial);
            pickup.position.set(0, 0.03, -0.15 + i * 0.12);
            pickup.name = `pickup_${i}`;
            guitar.add(pickup);
        }

        // Bridge
        const bridgeGeometry = new THREE.BoxGeometry(0.08, 0.02, 0.1);
        const bridgeMaterial = new THREE.MeshStandardMaterial({
            color: 0xC0C0C0,
            metalness: 0.9,
            roughness: 0.1
        });
        const bridge = new THREE.Mesh(bridgeGeometry, bridgeMaterial);
        bridge.position.set(0, 0.03, 0.15);
        bridge.name = 'bridge';
        guitar.add(bridge);

        // Strings
        const stringMaterial = new THREE.MeshStandardMaterial({
            color: 0xFFFFFF,
            metalness: 1.0,
            roughness: 0.1
        });
        for (let i = 0; i < 6; i++) {
            const stringGeometry = new THREE.CylinderGeometry(0.001, 0.001, 1.0, 8);
            const string = new THREE.Mesh(stringGeometry, stringMaterial);
            string.rotation.x = Math.PI / 2;
            string.position.set(-0.025 + i * 0.01, 0.03, -0.4);
            string.name = `string_${i}`;
            guitar.add(string);
        }

        // Rotate to proper orientation
        guitar.rotation.x = -Math.PI / 2;

        return guitar;
    }

    private createAcousticGuitar(): THREE.Group {
        const guitar = new THREE.Group();
        guitar.name = 'AcousticGuitar';

        // Body (rounded acoustic shape)
        const bodyGeometry = new THREE.SphereGeometry(0.25, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0xD2691E,
            metalness: 0.1,
            roughness: 0.6
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.name = 'body';
        guitar.add(body);

        // Sound hole
        const holeGeometry = new THREE.CircleGeometry(0.06, 32);
        const holeMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            side: THREE.DoubleSide
        });
        const hole = new THREE.Mesh(holeGeometry, holeMaterial);
        hole.position.set(0, 0.01, -0.08);
        hole.rotation.x = -Math.PI / 2;
        hole.name = 'soundhole';
        guitar.add(hole);

        // Neck
        const neckGeometry = new THREE.CylinderGeometry(0.025, 0.025, 0.7, 16);
        const neckMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B4513,
            metalness: 0.2,
            roughness: 0.7
        });
        const neck = new THREE.Mesh(neckGeometry, neckMaterial);
        neck.position.set(0, 0, -0.6);
        neck.rotation.x = Math.PI / 2;
        neck.name = 'neck';
        guitar.add(neck);

        // Headstock
        const headstockGeometry = new THREE.BoxGeometry(0.08, 0.02, 0.15);
        const headstock = new THREE.Mesh(headstockGeometry, neckMaterial);
        headstock.position.set(0, 0, -1.0);
        headstock.name = 'headstock';
        guitar.add(headstock);

        // Strings
        const stringMaterial = new THREE.MeshStandardMaterial({
            color: 0xFFD700,
            metalness: 0.8,
            roughness: 0.2
        });
        for (let i = 0; i < 6; i++) {
            const stringGeometry = new THREE.CylinderGeometry(0.001, 0.001, 1.0, 8);
            const string = new THREE.Mesh(stringGeometry, stringMaterial);
            string.rotation.x = Math.PI / 2;
            string.position.set(-0.025 + i * 0.01, 0.02, -0.5);
            string.name = `string_${i}`;
            guitar.add(string);
        }

        guitar.rotation.x = -Math.PI / 2;

        return guitar;
    }

    private createBassGuitar(): THREE.Group {
        const bass = this.createElectricGuitar();
        bass.name = 'BassGuitar';

        // Scale up slightly for bass proportions
        bass.scale.set(1.1, 1.1, 1.1);

        // Recolor to classic bass color (black)
        bass.traverse((child) => {
            if (child instanceof THREE.Mesh && child.name === 'body') {
                child.material = new THREE.MeshStandardMaterial({
                    color: 0x000000,
                    metalness: 0.7,
                    roughness: 0.2
                });
            }
        });

        return bass;
    }

    // ==========================================================================
    // KEYBOARD GENERATORS
    // ==========================================================================

    private createSynthesizer(): THREE.Group {
        const synth = new THREE.Group();
        synth.name = 'Synthesizer';

        // Main body
        const bodyGeometry = new THREE.BoxGeometry(0.8, 0.1, 0.4);
        const bodyMaterial = new THREE.MeshStandardMaterial({
            color: 0x2C3E50,
            metalness: 0.5,
            roughness: 0.4
        });
        const body = new THREE.Mesh(bodyGeometry, bodyMaterial);
        body.name = 'body';
        synth.add(body);

        // Keyboard keys (3 octaves = 36 keys)
        const whiteKeyMaterial = new THREE.MeshStandardMaterial({
            color: 0xFFFFFF,
            metalness: 0.3,
            roughness: 0.7
        });
        const blackKeyMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.6,
            roughness: 0.3
        });

        const keyWidth = 0.02;
        const whiteKeyGeometry = new THREE.BoxGeometry(keyWidth, 0.01, 0.1);
        const blackKeyGeometry = new THREE.BoxGeometry(keyWidth * 0.6, 0.015, 0.06);

        // Create 36 white keys
        for (let i = 0; i < 21; i++) {
            const key = new THREE.Mesh(whiteKeyGeometry, whiteKeyMaterial);
            key.position.set(-0.35 + i * keyWidth, 0.055, 0.1);
            key.name = `white_key_${i}`;
            synth.add(key);
        }

        // Create black keys (pattern: 2, 3, 2, 3...)
        const blackKeyPattern = [1, 2, 4, 5, 6]; // Positions within octave
        for (let octave = 0; octave < 3; octave++) {
            for (const pos of blackKeyPattern) {
                const key = new THREE.Mesh(blackKeyGeometry, blackKeyMaterial);
                key.position.set(-0.35 + (octave * 7 + pos) * keyWidth, 0.065, 0.13);
                key.name = `black_key_${octave}_${pos}`;
                synth.add(key);
            }
        }

        // Control panel
        const panelGeometry = new THREE.BoxGeometry(0.6, 0.08, 0.15);
        const panelMaterial = new THREE.MeshStandardMaterial({
            color: 0x34495E,
            metalness: 0.4,
            roughness: 0.5
        });
        const panel = new THREE.Mesh(panelGeometry, panelMaterial);
        panel.position.set(0, 0.05, -0.1);
        panel.name = 'control_panel';
        synth.add(panel);

        // Knobs (16 knobs in 2 rows)
        const knobMaterial = new THREE.MeshStandardMaterial({
            color: 0x95A5A6,
            metalness: 0.8,
            roughness: 0.2
        });
        for (let row = 0; row < 2; row++) {
            for (let i = 0; i < 8; i++) {
                const knobGeometry = new THREE.CylinderGeometry(0.012, 0.012, 0.02, 16);
                const knob = new THREE.Mesh(knobGeometry, knobMaterial);
                knob.position.set(-0.25 + i * 0.07, 0.1, -0.12 + row * 0.04);
                knob.name = `knob_${row}_${i}`;
                synth.add(knob);
            }
        }

        // Display screen
        const screenGeometry = new THREE.BoxGeometry(0.2, 0.05, 0.001);
        const screenMaterial = new THREE.MeshStandardMaterial({
            color: 0x1ABC9C,
            emissive: 0x0E7C6B,
            metalness: 0.9,
            roughness: 0.1
        });
        const screen = new THREE.Mesh(screenGeometry, screenMaterial);
        screen.position.set(0.25, 0.09, -0.075);
        screen.name = 'screen';
        synth.add(screen);

        return synth;
    }

    private createKeyboard(): THREE.Group {
        // Simplified version of synthesizer for stage piano
        const keyboard = this.createSynthesizer();
        keyboard.name = 'Keyboard';
        keyboard.scale.set(1.5, 1, 1); // Wider for 88 keys
        return keyboard;
    }

    // ==========================================================================
    // DRUM GENERATORS
    // ==========================================================================

    private createDrumKit(): THREE.Group {
        const kit = new THREE.Group();
        kit.name = 'DrumKit';

        const drumMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B0000,
            metalness: 0.7,
            roughness: 0.3
        });

        // Kick drum
        const kickGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.25, 32);
        const kick = new THREE.Mesh(kickGeometry, drumMaterial);
        kick.rotation.z = Math.PI / 2;
        kick.position.set(0, 0.3, 0);
        kick.name = 'kick';
        kit.add(kick);

        // Snare drum
        const snareGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.1, 32);
        const snare = new THREE.Mesh(snareGeometry, drumMaterial);
        snare.position.set(-0.35, 0.5, 0.2);
        snare.name = 'snare';
        kit.add(snare);

        // Tom-toms (2 rack toms)
        for (let i = 0; i < 2; i++) {
            const tomGeometry = new THREE.CylinderGeometry(0.12 - i * 0.02, 0.12 - i * 0.02, 0.12, 32);
            const tom = new THREE.Mesh(tomGeometry, drumMaterial);
            tom.position.set(0.25 + i * 0.2, 0.65, 0.1);
            tom.name = `tom_${i}`;
            kit.add(tom);
        }

        // Floor tom
        const floorTomGeometry = new THREE.CylinderGeometry(0.18, 0.18, 0.2, 32);
        const floorTom = new THREE.Mesh(floorTomGeometry, drumMaterial);
        floorTom.position.set(0.4, 0.3, -0.2);
        floorTom.name = 'floor_tom';
        kit.add(floorTom);

        // Cymbals (Hi-hat, 2 crashes, ride)
        const cymbalMaterial = new THREE.MeshStandardMaterial({
            color: 0xFFD700,
            metalness: 0.95,
            roughness: 0.05
        });
        const cymbalGeometry = new THREE.CylinderGeometry(0.15, 0.15, 0.01, 32);

        // Hi-hat
        const hihat = new THREE.Mesh(cymbalGeometry, cymbalMaterial);
        hihat.position.set(-0.5, 0.7, 0.3);
        hihat.name = 'hihat';
        kit.add(hihat);

        // Crash cymbals
        const crash1 = new THREE.Mesh(cymbalGeometry, cymbalMaterial);
        crash1.position.set(0, 0.9, 0.3);
        crash1.name = 'crash1';
        kit.add(crash1);

        const crash2 = new THREE.Mesh(cymbalGeometry, cymbalMaterial);
        crash2.position.set(0.5, 0.9, -0.1);
        crash2.name = 'crash2';
        kit.add(crash2);

        // Ride cymbal
        const ride = new THREE.Mesh(cymbalGeometry, cymbalMaterial);
        ride.position.set(0.6, 0.85, 0);
        ride.name = 'ride';
        kit.add(ride);

        return kit;
    }

    // ==========================================================================
    // ENVIRONMENT ELEMENT GENERATORS
    // ==========================================================================

    private createAmplifier(): THREE.Group {
        const amp = new THREE.Group();
        amp.name = 'Amplifier';

        // Main cabinet
        const cabinetGeometry = new THREE.BoxGeometry(0.5, 0.6, 0.3);
        const cabinetMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.3,
            roughness: 0.7
        });
        const cabinet = new THREE.Mesh(cabinetGeometry, cabinetMaterial);
        cabinet.position.set(0, 0.3, 0);
        cabinet.name = 'cabinet';
        amp.add(cabinet);

        // Speaker grille
        const grilleGeometry = new THREE.BoxGeometry(0.35, 0.35, 0.02);
        const grilleMaterial = new THREE.MeshStandardMaterial({
            color: 0x2C3E50,
            metalness: 0.6,
            roughness: 0.4
        });
        const grille = new THREE.Mesh(grilleGeometry, grilleMaterial);
        grille.position.set(0, 0.25, 0.16);
        grille.name = 'grille';
        amp.add(grille);

        // Control panel
        const panelGeometry = new THREE.BoxGeometry(0.4, 0.15, 0.02);
        const panelMaterial = new THREE.MeshStandardMaterial({
            color: 0xC0C0C0,
            metalness: 0.7,
            roughness: 0.3
        });
        const panel = new THREE.Mesh(panelGeometry, panelMaterial);
        panel.position.set(0, 0.5, 0.16);
        panel.name = 'panel';
        amp.add(panel);

        // Knobs
        const knobMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.5,
            roughness: 0.5
        });
        for (let i = 0; i < 6; i++) {
            const knobGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.02, 16);
            const knob = new THREE.Mesh(knobGeometry, knobMaterial);
            knob.rotation.x = Math.PI / 2;
            knob.position.set(-0.15 + i * 0.06, 0.5, 0.18);
            knob.name = `knob_${i}`;
            amp.add(knob);
        }

        return amp;
    }

    private createPedestal(): THREE.Group {
        const pedestal = new THREE.Group();
        pedestal.name = 'Pedestal';

        // Base
        const baseGeometry = new THREE.CylinderGeometry(0.2, 0.25, 0.05, 32);
        const baseMaterial = new THREE.MeshStandardMaterial({
            color: 0x2C3E50,
            metalness: 0.8,
            roughness: 0.2
        });
        const base = new THREE.Mesh(baseGeometry, baseMaterial);
        base.position.set(0, 0.025, 0);
        base.name = 'base';
        pedestal.add(base);

        // Column
        const columnGeometry = new THREE.CylinderGeometry(0.05, 0.05, 1.0, 16);
        const column = new THREE.Mesh(columnGeometry, baseMaterial);
        column.position.set(0, 0.55, 0);
        column.name = 'column';
        pedestal.add(column);

        // Top platform
        const topGeometry = new THREE.CylinderGeometry(0.18, 0.15, 0.05, 32);
        const top = new THREE.Mesh(topGeometry, baseMaterial);
        top.position.set(0, 1.075, 0);
        top.name = 'top';
        pedestal.add(top);

        return pedestal;
    }

    private createBrickWall(): THREE.Group {
        const wall = new THREE.Group();
        wall.name = 'BrickWall';

        const brickMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B4513,
            metalness: 0.1,
            roughness: 0.9
        });

        // Create brick pattern (10x20 bricks)
        const brickWidth = 0.2;
        const brickHeight = 0.1;
        const brickDepth = 0.1;

        for (let row = 0; row < 20; row++) {
            const offset = (row % 2) * brickWidth / 2;
            for (let col = 0; col < 10; col++) {
                const brickGeometry = new THREE.BoxGeometry(brickWidth, brickHeight, brickDepth);
                const brick = new THREE.Mesh(brickGeometry, brickMaterial);
                brick.position.set(
                    -1 + col * brickWidth + offset,
                    row * brickHeight,
                    0
                );
                brick.name = `brick_${row}_${col}`;
                wall.add(brick);
            }
        }

        return wall;
    }

    private createWoodFloor(): THREE.Group {
        const floor = new THREE.Group();
        floor.name = 'WoodFloor';

        const plankMaterial = new THREE.MeshStandardMaterial({
            color: 0x8B4513,
            metalness: 0.1,
            roughness: 0.6
        });

        // Create wooden planks (20 planks)
        const plankWidth = 0.2;
        const plankLength = 4.0;
        const plankThickness = 0.05;

        for (let i = 0; i < 20; i++) {
            const plankGeometry = new THREE.BoxGeometry(plankWidth, plankThickness, plankLength);
            const plank = new THREE.Mesh(plankGeometry, plankMaterial);
            plank.position.set(-2 + i * plankWidth, 0, 0);
            plank.name = `plank_${i}`;
            floor.add(plank);
        }

        return floor;
    }

    private createSpotlight(): THREE.Group {
        const spotlight = new THREE.Group();
        spotlight.name = 'Spotlight';

        // Housing
        const housingGeometry = new THREE.CylinderGeometry(0.1, 0.15, 0.3, 16);
        const housingMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.8,
            roughness: 0.2
        });
        const housing = new THREE.Mesh(housingGeometry, housingMaterial);
        housing.name = 'housing';
        spotlight.add(housing);

        // Lens
        const lensGeometry = new THREE.CircleGeometry(0.12, 32);
        const lensMaterial = new THREE.MeshStandardMaterial({
            color: 0xFFFFFF,
            emissive: 0xFFFF00,
            emissiveIntensity: 0.5,
            transparent: true,
            opacity: 0.8
        });
        const lens = new THREE.Mesh(lensGeometry, lensMaterial);
        lens.position.set(0, -0.15, 0);
        lens.rotation.x = -Math.PI / 2;
        lens.name = 'lens';
        spotlight.add(lens);

        return spotlight;
    }

    private createCable(): THREE.Group {
        const cable = new THREE.Group();
        cable.name = 'Cable';

        const cableMaterial = new THREE.MeshStandardMaterial({
            color: 0x000000,
            metalness: 0.3,
            roughness: 0.7
        });

        // Create cable using curve
        const curve = new THREE.CatmullRomCurve3([
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0.3, -0.1, 0.3),
            new THREE.Vector3(0.6, -0.15, 0.5),
            new THREE.Vector3(1.0, -0.1, 0.6),
            new THREE.Vector3(1.3, 0, 0.7)
        ]);

        const tubeGeometry = new THREE.TubeGeometry(curve, 20, 0.01, 8, false);
        const cableMesh = new THREE.Mesh(tubeGeometry, cableMaterial);
        cableMesh.name = 'cable_body';
        cable.add(cableMesh);

        // Jack connectors at both ends
        const jackGeometry = new THREE.CylinderGeometry(0.015, 0.015, 0.05, 8);
        const jackMaterial = new THREE.MeshStandardMaterial({
            color: 0x808080,
            metalness: 0.9,
            roughness: 0.1
        });

        const jack1 = new THREE.Mesh(jackGeometry, jackMaterial);
        jack1.position.copy(curve.getPoint(0));
        jack1.name = 'jack_1';
        cable.add(jack1);

        const jack2 = new THREE.Mesh(jackGeometry, jackMaterial);
        jack2.position.copy(curve.getPoint(1));
        jack2.name = 'jack_2';
        cable.add(jack2);

        return cable;
    }

    private createPlaceholder(): THREE.Group {
        const placeholder = new THREE.Group();
        placeholder.name = 'Placeholder';

        const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
        const material = new THREE.MeshStandardMaterial({
            color: 0xFF00FF,
            metalness: 0.5,
            roughness: 0.5,
            wireframe: true
        });
        const mesh = new THREE.Mesh(geometry, material);
        placeholder.add(mesh);

        return placeholder;
    }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const assetGenerator = new ProceduralAssetGenerator();
