import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { nodePolyfills } from 'vite-plugin-node-polyfills'

export default defineConfig({
  plugins: [
    vue(),
    nodePolyfills({
      globals: {
        globalThis: true
      }
    })
  ],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    target: 'es2015',
    commonjsOptions: {
      transformMixedEsModules: true
    }
  },
  server: {
    host: '0.0.0.0',
    port: 9320,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:9321',
        changeOrigin: true
      }
    }
  }
})
