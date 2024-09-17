import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/vidhan-search/',
  server: {
    port: 5175,
    watch: {
      usePolling: true,
    },
  },
})
