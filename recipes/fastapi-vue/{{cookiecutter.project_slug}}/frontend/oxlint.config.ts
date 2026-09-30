import e18e from '@e18e/eslint-plugin';
import { defineConfig } from 'oxlint';

export default defineConfig({
  plugins: ['typescript', 'unicorn', 'oxc'],
  jsPlugins: ['@e18e/eslint-plugin'],
  categories: { correctness: 'error' },
  rules: { ...e18e.configs.recommended.rules },
  ignorePatterns: ['dist/**', 'coverage/**'],
});
