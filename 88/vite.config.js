import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api/sina': {
        target: 'http://hq.sinajs.cn/',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/sina\//, 'list='),
        headers: {
          'Referer': 'http://finance.sina.com.cn',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        timeout: 15000
      },
      '/api/em': {
        target: 'http://push2.eastmoney.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/em/, ''),
        headers: {
          'Referer': 'http://quote.eastmoney.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 15000
      },
      '/api/emhis': {
        target: 'http://push2his.eastmoney.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/emhis/, ''),
        headers: {
          'Referer': 'http://quote.eastmoney.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 20000
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1500,
    rollupOptions: {
      output: {
        manualChunks: {
          'echarts': ['echarts']
        }
      }
    }
  }
})
