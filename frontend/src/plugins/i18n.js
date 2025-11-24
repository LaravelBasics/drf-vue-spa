// src/plugins/i18n.js

import { createI18n } from 'vue-i18n';
import ja from '@/locales/ja.json';
import en from '@/locales/en.json';

// 🌟 Vuetifyのロケールファイルをインポート
import { ja as vuetifyJa, en as vuetifyEn } from 'vuetify/locale';

const i18n = createI18n({
    legacy: false, // Composition API使用
    locale: 'ja', // デフォルト固定(Storeが管理)
    fallbackLocale: 'ja',

    // 🌟 修正点: Vuetifyのメッセージを統合
    messages: {
        ja: {
            ...ja,
            $vuetify: vuetifyJa, // Vuetifyの内部キーを$vuetifyとして追加(Vuetifyの標準テキストの翻訳は、すべて Vue I18nに任せる)
        },

        en: {
            ...en,
            $vuetify: vuetifyEn,
        },
    },

    // 本番環境では警告非表示(シンプル化)
    silentFallbackWarn: import.meta.env.PROD,
    silentTranslationWarn: import.meta.env.PROD,
});

export default i18n;
