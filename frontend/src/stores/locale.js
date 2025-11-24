// src/stores/locale.js
import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import i18n from '@/plugins/i18n';

export const useLocaleStore = defineStore(
    'locale',
    () => {
        const SUPPORTED_LOCALES = ['ja', 'en'];

        // 初期言語決定: 日本限定サービスのため常に'ja'
        // ブラウザ言語検出は不要(業務用アプリ想定)
        const getInitialLocale = () => {
            // 日本の業務システムなので常に日本語を初期値とする
            // ユーザーが明示的に変更した場合のみlocalStorageに保存される
            return 'ja';
        };

        // Pinia persistがlocalStorageから自動復元
        // 復元値がある場合: ユーザーが以前選択した言語を使用
        // 復元値がない場合: getInitialLocale()で'ja'を設定
        const locale = ref(getInitialLocale());

        // 初回: i18nを同期(localStorage復元後に実行)
        i18n.global.locale.value = locale.value;

        // 以降の変更を監視してi18nに反映
        // 🌟 vuetifyはadapterで自動同期されるので不要
        watch(locale, (newLocale) => {
            i18n.global.locale.value = newLocale;
        });

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
        persist: true, // localStorage自動永続化
    },
);
