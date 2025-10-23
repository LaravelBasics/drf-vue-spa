// src/stores/locale.js - 多言語設定管理

import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import i18n from '@/plugins/i18n';

export const useLocaleStore = defineStore('locale', () => {
    // localStorageから初期言語を取得
    const getInitialLocale = () => {
        const saved = localStorage.getItem('locale');
        if (saved && ['ja', 'en'].includes(saved)) {
            return saved;
        }
        return i18n.global.locale.value;
    };

    const locale = ref(getInitialLocale());

    // 初期化時にvue-i18nと同期
    i18n.global.locale.value = locale.value;

    // 言語変更を監視してvue-i18n、Vuetify、localStorageに反映
    watch(locale, (newLocale) => {
        i18n.global.locale.value = newLocale;

        if (window.$vuetify) {
            window.$vuetify.locale.current = newLocale;
        }

        localStorage.setItem('locale', newLocale);
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
