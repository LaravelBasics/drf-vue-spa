// src/stores/locale.js
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import i18n from '@/plugins/i18n';

export const useLocaleStore = defineStore('locale', () => {
    // ⭐ localStorageから初期値を取得
    const getInitialLocale = () => {
        const saved = localStorage.getItem('locale');
        if (saved && ['ja', 'en'].includes(saved)) {
            return saved;
        }
        // localStorage にない場合は i18n の初期設定を使用
        return i18n.global.locale.value;
    };

    const locale = ref(getInitialLocale());

    // ⭐ 初期化時に vue-i18n と同期
    i18n.global.locale.value = locale.value;

    // ⭐ locale変更を監視
    watch(locale, (newLocale) => {
        // 1. vue-i18n の言語を変更
        i18n.global.locale.value = newLocale;

        // 2. Vuetify の言語も変更（グローバルに設定）
        if (window.$vuetify) {
            window.$vuetify.locale.current = newLocale;
        }

        // 3. localStorage に保存
        localStorage.setItem('locale', newLocale);

        console.log('🌐 言語設定を保存:', newLocale);
    });

    function setLocale(newLocale) {
        if (['ja', 'en'].includes(newLocale)) {
            locale.value = newLocale;
        }
    }

    return {
        locale,
        setLocale,
    };
});
