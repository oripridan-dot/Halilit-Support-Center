import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Use SWC for faster HMR
      jsxRuntime: "automatic",
    }),
  ],
  server: {
    host: "0.0.0.0",
    port: 5173,
    watch: {
      usePolling: true,
      interval: 500,
    },
    // Improve HMR performance
    hmr: {
      overlay: true,
    },
  },
  optimizeDeps: {
    // Pre-bundle these dependencies for faster dev server startup
    include: [
      "react",
      "react-dom",
      "react-dom/client",
      "zustand",
      "framer-motion",
      "lucide-react",
      "fuse.js",
    ],
    // Exclude large dependencies that change frequently
    exclude: [],
  },
  build: {
    // Faster builds
    target: "esnext",
    minify: "esbuild",
    // Aggressive code-splitting to reduce main bundle
    rollupOptions: {
      output: {
        manualChunks: {
          // Core vendor
          "vendor-react": ["react", "react-dom"],
          "vendor-zod": ["zod", "zustand"],
          // Separate heavy libraries
          "vendor-framer": ["framer-motion"],
          "vendor-lucide": ["lucide-react"],
          // Search
          "vendor-fuse": ["fuse.js"],
        },
      },
    },
    // More aggressive chunk splitting
    chunkSizeWarningLimit: 300,
    // Enable source maps only in dev
    sourcemap: process.env.NODE_ENV === "development",
  },
});
