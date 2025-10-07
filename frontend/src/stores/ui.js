// C:\Users\pvufx\Desktop\template\frontend\src\stores\ui.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useDisplay } from 'vuetify';

export const useUiStore = defineStore(
    'ui',
    () => {
        // Vuetifyのブレークポイント検出
        const { mdAndUp } = useDisplay();

        // ⭐ drawer: サイドバーの開閉状態
        // モバイルでは初期状態を閉じる
        const drawer = ref(mdAndUp.value ? true : false);

        // ⭐ rail: ミニモード（アイコンのみ表示）かどうか
        const rail = ref(true);

        // ⭐ レスポンシブ判定: PC画面かどうか
        const isDesktop = computed(() => mdAndUp.value);

        // ⭐ サイドバーのモード判定
        // PC: permanent + rail対応
        // Mobile: temporary（モーダル式）
        const sidebarMode = computed(() => {
            return isDesktop.value ? 'permanent' : 'temporary';
        });

        // ⭐ サイドバーの切り替え（完全開閉）
        const toggleDrawer = () => {
            drawer.value = !drawer.value;
        };

        // ⭐ レールモードの切り替え（フル⇔ミニ）
        // PCのみ有効、モバイルでは無視
        const toggleRail = () => {
            if (isDesktop.value) {
                rail.value = !rail.value;
            } else {
                // モバイルではdrawerを開閉
                toggleDrawer();
            }
        };

        return {
            drawer,
            rail,
            isDesktop,
            sidebarMode,
            toggleDrawer,
            toggleRail,
        };
    },
    {
        persist: true,
    },
);
