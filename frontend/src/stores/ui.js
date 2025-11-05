// src/stores/ui.js - UI状態管理（サイドバー、レスポンシブ）

import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useDisplay } from 'vuetify';

export const useUiStore = defineStore('ui', () => {
    const { lgAndUp } = useDisplay();

    // サイドバーの開閉状態（初期値は画面サイズに応じて決定）
    const drawer = ref(lgAndUp.value);

    // レールモード（ミニモード: アイコンのみ表示）
    const rail = ref(true);

    // レスポンシブ判定
    const isDesktop = computed(() => lgAndUp.value);

    const sidebarMode = computed(() => {
        return isDesktop.value ? 'permanent' : 'temporary';
    });

    // 画面サイズ変更時の自動調整
    watch(lgAndUp, (newValue) => {
        drawer.value = newValue;
    });

    // サイドバーの開閉切り替え
    const toggleDrawer = () => {
        drawer.value = !drawer.value;
    };

    // レールモード切り替え（PC: フル⇔ミニ、モバイル: 開閉）
    const toggleRail = () => {
        if (isDesktop.value) {
            rail.value = !rail.value;
        } else {
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
});
