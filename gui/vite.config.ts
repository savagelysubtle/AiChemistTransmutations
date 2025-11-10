import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import electron from 'vite-plugin-electron';
import path from 'node:path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    electron([
      {
        // Main-Process entry file of Hot-Reload.
        entry: 'src/main/main.ts',
        onstart(options) {
          // Don't auto-launch Electron - we'll launch it manually via electron:dev script
          // This prevents double launching (vite-plugin-electron + our script)
          console.log('📦 Electron main process built. Launch Electron manually via "npm run electron:dev"');
        },
        vite: {
          build: {
            outDir: 'dist-electron/main',
            // mdx-to-md (via mdx-bundler) needs to call the esbuild binary
            // at runtime. If esbuild gets bundled into the single output
            // file the relative path it relies on breaks and we hit the
            // runtime error: "The esbuild JavaScript API cannot be bundled".
            // Declaring it as an external dependency keeps the `require`
            // statement intact so Node/Electron resolves it from
            // node_modules on-demand.
            rollupOptions: {
              external: ['esbuild'],
            },
          },
        },
      },
      {
        entry: 'src/main/preload.ts',
        onstart(options) {
          // Notify the Renderer-Process to reload the page when the Preload-Scripts build is complete,
          // instead of restarting the entire Electron App.
          options.reload();
        },
        vite: {
          build: {
            outDir: 'dist-electron/preload',
            // Same reasoning as in the main build: keep the dynamic require
            // for the "esbuild" package intact to avoid runtime failures.
            rollupOptions: {
              external: ['esbuild'],
            },
          },
        },
      },
    ]),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist', // Output directory for the renderer process build
    // Configure asset handling - don't hash public assets
    assetsInlineLimit: 0, // Don't inline small assets
    rollupOptions: {
      output: {
        // Keep original filenames for all assets (no hashing)
        assetFileNames: 'assets/[name][extname]',
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
      },
    },
  },
  // Ensure public directory is copied correctly (this is default, but explicit is better)
  publicDir: 'public',
  server: {
    port: 3000, // You can specify a port for the dev server
    strictPort: true,
  },
});