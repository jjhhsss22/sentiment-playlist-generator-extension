import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    ],

  build: {
    outDir: '../gateway/static',  // output directly to Flask static folder
    emptyOutDir: true,           // clear previous build
    rollupOptions: {
      input: './src/main.jsx',       // main entry
      output: {
        entryFileNames: `assets/[name].js`,
        chunkFileNames: `assets/[name].js`,
        assetFileNames: `assets/[name].[ext]`,
      }
    }
  }
});
