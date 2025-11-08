import { defineConfig } from 'eslint/config';
import globals from 'globals';
import js from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import skipFormatting from '@vue/eslint-config-prettier/skip-formatting';

export default defineConfig([
    {
        name: 'app/files-to-lint',
        files: ['**/*.{js,mjs,jsx,vue}'],
    },

    {
        ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**'],
    },

    {
        languageOptions: {
            globals: {
                ...globals.browser,
            },
        },
    },

    js.configs.recommended,
    ...pluginVue.configs['flat/essential'],

    // ✅ Vue ルール追加
    {
        name: 'app/vue-rules', // 「Vue用のルール」という名前
        files: ['**/*.vue'], // .vueファイルにのみ適用
        rules: {
            // ルール1: v-slot は # で書いてね（警告）
            'vue/v-slot-style': ['warn', 'shorthand'],

            // ルール2: コンポーネント名は PascalCase
            'vue/component-name-in-template-casing': ['error', 'PascalCase'],

            // ルール3: 使ってない変数あったら教えて（警告）
            'vue/no-unused-vars': 'warn',
        },
    },

    skipFormatting,
]);
