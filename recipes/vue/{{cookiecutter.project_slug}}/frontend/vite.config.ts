import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [vue()],
{% if cookiecutter._backend %}  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
{% endif %}  test: {
    environment: 'jsdom',
    clearMocks: true,
    restoreMocks: true,
    unstubGlobals: true,
  },
});
