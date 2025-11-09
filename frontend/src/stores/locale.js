// src/stores/locale.js - 多言語設定管理
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import i18n from '@/plugins/i18n';
import vuetify from '@/plugins/vuetify';

export const useLocaleStore = defineStore(
    'locale',
    () => {
        // サポートする言語リスト
        const SUPPORTED_LOCALES = ['ja', 'en'];

        // デフォルト言語（vue-i18nの初期値）
        const locale = ref(i18n.global.locale.value);

        // 言語変更を監視して vue-i18n と Vuetify に反映
        watch(locale, (newLocale) => {
            i18n.global.locale.value = newLocale;
            vuetify.locale.current = newLocale;
        });

        // 言語を変更する関数
        // newLocale: 新しい言語コード ('ja' | 'en')
        function setLocale(newLocale) {
            if (SUPPORTED_LOCALES.includes(newLocale)) {
                locale.value = newLocale;
            } else {
                console.warn(`Unsupported locale: ${newLocale}`);
            }
        }

        return {
            locale,
            setLocale,
        };
    },
    {
        // Piniaの永続化プラグインで自動的にlocalStorageに保存
        persist: true,
    },
);
