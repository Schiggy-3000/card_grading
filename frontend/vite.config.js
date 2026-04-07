import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Plugin: redirect /card_grading (no trailing slash) → /card_grading/
// so Playwright tests using BASE_URL.rstrip("/") still reach the SPA.
function baseRedirectPlugin() {
  return {
    name: 'base-redirect',
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (req.url === '/card_grading') {
          res.writeHead(301, { Location: '/card_grading/' })
          res.end()
          return
        }
        next()
      })
    },
  }
}

export default defineConfig({
  plugins: [react(), baseRedirectPlugin()],
  base: '/card_grading/',   // matches GitHub Pages subdirectory
})
