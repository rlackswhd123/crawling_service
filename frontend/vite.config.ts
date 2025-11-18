// import {defineConfig} from 'vite'
// import vue from '@vitejs/plugin-vue'
// import tailwindcss from '@tailwindcss/vite'
// import path from 'path'

// // https://vite.dev/config/
// export default defineConfig({
// 	plugins: [vue(), tailwindcss()],

// 	resolve: {
// 		alias: {
// 			'@': path.resolve(__dirname, './src'),
// 		},
// 	},

// 	server: {
// 		open: true,
// 		port: 8501,

// 	}
// })

// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import fs from 'fs'

export default defineConfig(({ mode }) => {
  // 배포 환경에서만 HTTPS 활성화
  const isProduction = mode === 'production'

  // HTTPS 인증서 경로
  const HTTPS_KEY_PATH = 'C:/anytalk/bin/key.pem'
  const HTTPS_CERT_PATH = 'C:/anytalk/bin/cert.pem'

  // 파일 존재 여부 확인
  const useHttps = isProduction &&
                   fs.existsSync(HTTPS_KEY_PATH) &&
                   fs.existsSync(HTTPS_CERT_PATH)

  return {
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      open: true,
      port: 8501,
      ...(useHttps && {
        https: {
          key: fs.readFileSync(HTTPS_KEY_PATH),
          cert: fs.readFileSync(HTTPS_CERT_PATH),
        },
      }),
    },
  }
})
