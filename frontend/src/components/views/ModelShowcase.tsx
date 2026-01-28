/**
 * ModelShowcase - Display generated 3D models
 * Simple viewer for the Blender-generated instrument models
 */

import React, { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OBJLoader } from "three/examples/jsm/loaders/OBJLoader";
import { MTLLoader } from "three/examples/jsm/loaders/MTLLoader";

interface Model {
  name: string;
  objPath: string;
  mtlPath: string;
  rotation?: { x: number; y: number; z: number };
}

const MODELS: Model[] = [
  {
    name: "Electric Guitar - Stratocaster",
    objPath: "/models/guitars/electric/stratocaster.obj",
    mtlPath: "/models/guitars/electric/stratocaster.mtl",
    rotation: { x: 0, y: Math.PI / 4, z: 0 },
  },
  {
    name: "Acoustic Guitar - Dreadnought",
    objPath: "/models/guitars/acoustic/dreadnought.obj",
    mtlPath: "/models/guitars/acoustic/dreadnought.mtl",
    rotation: { x: 0, y: Math.PI / 6, z: 0 },
  },
  {
    name: "Bass Guitar - Fender Precision",
    objPath: "/models/guitars/bass/fender_precision.obj",
    mtlPath: "/models/guitars/bass/fender_precision.mtl",
    rotation: { x: 0, y: Math.PI / 3, z: 0 },
  },
  {
    name: "Synthesizer - Moog Sub Phatty",
    objPath: "/models/synths/moog_sub_phatty.obj",
    mtlPath: "/models/synths/moog_sub_phatty.mtl",
    rotation: { x: 0, y: Math.PI / 5, z: 0 },
  },
  {
    name: "Drum Kit - Acoustic",
    objPath: "/models/drums/acoustic_kit.obj",
    mtlPath: "/models/drums/acoustic_kit.mtl",
    rotation: { x: 0, y: Math.PI / 8, z: 0 },
  },
  {
    name: "Amplifier - Marshall Stack",
    objPath: "/models/amps/marshall_stack.obj",
    mtlPath: "/models/amps/marshall_stack.mtl",
    rotation: { x: 0, y: Math.PI / 4, z: 0 },
  },
];

export const ModelShowcase: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const modelRef = useRef<THREE.Group | null>(null);
  const [currentModelIndex, setCurrentModelIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const animationIdRef = useRef<number>();

  useEffect(() => {
    if (!containerRef.current) return;

    console.log("🎬 Initializing 3D viewer");

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    sceneRef.current = scene;
    console.log("✓ Scene created");

    // Camera setup
    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight;
    console.log(`Canvas dimensions: ${width}x${height}`);
    
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(0, 0, 2);
    cameraRef.current = camera;
    console.log("✓ Camera created");

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x1a1a1a, 1);
    console.log("✓ Renderer created, adding to DOM");
    
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;
    console.log("✓ Renderer added to DOM");

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    const pointLight = new THREE.PointLight(0xff6b6b, 0.4);
    pointLight.position.set(-5, 3, 5);
    scene.add(pointLight);
    console.log("✓ Lighting added");

    // Animation loop
    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);

      if (modelRef.current) {
        modelRef.current.rotation.y += 0.005;
      }

      renderer.render(scene, camera);
    };

    console.log("🎬 Starting animation loop");
    animate();

    // Handle resize
    const handleResize = () => {
      const newWidth = containerRef.current?.clientWidth || width;
      const newHeight = containerRef.current?.clientHeight || height;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (animationIdRef.current) {
        cancelAnimationFrame(animationIdRef.current);
      }
      renderer.dispose();
      containerRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  // Load model
  useEffect(() => {
    const loadModel = async () => {
      if (!sceneRef.current || !cameraRef.current) return;

      console.log(`📦 Loading model ${currentModelIndex}: ${MODELS[currentModelIndex].name}`);
      setIsLoading(true);
      setError(null);

      // Remove previous model
      if (modelRef.current) {
        sceneRef.current.remove(modelRef.current);
        modelRef.current = null;
        console.log("✓ Previous model removed");
      }

      try {
        const model = MODELS[currentModelIndex];
        const mtlLoader = new MTLLoader();
        const objLoader = new OBJLoader();

        // Load MTL first (materials)
        mtlLoader.load(
          model.mtlPath,
          (materials) => {
            console.log("✓ Materials loaded");
            materials.preload();
            objLoader.setMaterials(materials);

            // Then load OBJ
            objLoader.load(
              model.objPath,
              (group) => {
                console.log("✓ OBJ loaded, processing geometry");
                // Center and scale model
                const box = new THREE.Box3().setFromObject(group);
                const center = box.getCenter(new THREE.Vector3());
                const size = box.getSize(new THREE.Vector3());
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = 1.5 / maxDim;

                group.position.sub(center.multiplyScalar(scale));
                group.scale.multiplyScalar(scale);

                // Apply rotation
                if (model.rotation) {
                  group.rotation.set(
                    model.rotation.x,
                    model.rotation.y,
                    model.rotation.z,
                  );
                }

                console.log(`✓ Model scaled and positioned, adding to scene`);
                sceneRef.current?.add(group);
                modelRef.current = group;
                setIsLoading(false);
                console.log("🎉 Model ready for display");
              },
              (progress) => {
                const percent = (progress.loaded / progress.total) * 100;
                console.log(`Loading OBJ: ${percent.toFixed(2)}%`);
              },
              (error) => {
                console.error("OBJ load error:", error);
                setError(`Failed to load model: ${error.message}`);
                setIsLoading(false);
              },
            );
          },
          (progress) => {
            const percent = (progress.loaded / progress.total) * 100;
            console.log(`Loading MTL: ${percent.toFixed(2)}%`);
          },
          (error) => {
            console.error("MTL load error:", error);
            setError(`Failed to load materials: ${error.message}`);
            setIsLoading(false);
          },
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        setError(`Error loading model: ${message}`);
        setIsLoading(false);
      }
    };

    loadModel();
  }, [currentModelIndex]);

  const handleNext = () => {
    setCurrentModelIndex((prev) => (prev + 1) % MODELS.length);
  };

  const handlePrev = () => {
    setCurrentModelIndex((prev) => (prev - 1 + MODELS.length) % MODELS.length);
  };

  return (
    <div className="w-full h-full flex flex-col bg-black">
      {/* Canvas */}
      <div ref={containerRef} className="flex-1 relative">
        {/* Loading indicator */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-white text-center">
              <div className="mb-4">Loading model...</div>
              <div className="w-8 h-8 border-4 border-gray-600 border-t-white rounded-full animate-spin mx-auto"></div>
            </div>
          </div>
        )}

        {/* Error display */}
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50">
            <div className="text-red-400 text-center max-w-md">
              <div className="font-bold mb-2">Error</div>
              <div className="text-sm">{error}</div>
            </div>
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="bg-gray-900 border-t border-gray-700 p-4">
        {/* Model name */}
        <div className="text-white text-center mb-4 font-semibold">
          {MODELS[currentModelIndex].name}
        </div>

        {/* Navigation buttons */}
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={handlePrev}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>

          {/* Model counter */}
          <div className="text-gray-400 text-sm">
            {currentModelIndex + 1} / {MODELS.length}
          </div>

          <button
            onClick={handleNext}
            disabled={isLoading}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next →
          </button>
        </div>

        {/* Thumbnails */}
        <div className="mt-4 flex gap-2 justify-center flex-wrap">
          {MODELS.map((m, idx) => (
            <button
              key={idx}
              onClick={() => setCurrentModelIndex(idx)}
              disabled={isLoading}
              className={`px-3 py-1 text-xs rounded transition-colors ${
                idx === currentModelIndex
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {m.name.split(" - ")[0]}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
