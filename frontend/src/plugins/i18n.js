// src/plugins/i18n.js - フォールバック対応版
import { createI18n } from 'vue-i18n';
import ja from '@/locales/ja.json';
import en from '@/locales/en.json';

// ブラウザの言語設定を取得
const getDefaultLocale = () => {
    const browserLocale = navigator.language || navigator.userLanguage;

    if (browserLocale.startsWith('ja')) return 'ja';
    if (browserLocale.startsWith('en')) return 'en';
    return 'ja'; // デフォルトは日本語
};

const i18n = createI18n({
    legacy: false, // Composition API を使用
    locale: getDefaultLocale(),
    fallbackLocale: 'ja', // ⭐ 英語で見つからない場合は日本語にフォールバック
    messages: {
        ja,
        en,
    },
    // ⭐ 本番環境では警告を非表示、開発環境では表示
    silentFallbackWarn: import.meta.env.PROD,
    // ⭐ 翻訳が見つからない場合の警告を表示（開発時のみ）
    silentTranslationWarn: import.meta.env.PROD,
    // ⭐ フォールバックロケールへの連鎖を有効化
    fallbackWarn: !import.meta.env.PROD,
    missingWarn: !import.meta.env.PROD,
});

export default i18n;
