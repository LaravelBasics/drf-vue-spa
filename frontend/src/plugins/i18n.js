// src/plugins/i18n.js - 国際化設定
import { createI18n } from 'vue-i18n';
import ja from '@/locales/ja.json';
import en from '@/locales/en.json';

// ブラウザの言語設定を取得
const getDefaultLocale = () => {
    const browserLocale = navigator.language || navigator.userLanguage;
    const supportedLocales = ['ja', 'en'];

    if (browserLocale.startsWith('ja')) return 'ja';
    if (browserLocale.startsWith('en')) return 'en';
    return 'ja'; // デフォルトは日本語
};

const i18n = createI18n({
    legacy: false, // Composition API を使用
    locale: getDefaultLocale(),
    fallbackLocale: 'ja',
    messages: {
        ja,
        en,
    },
});

export default i18n;
