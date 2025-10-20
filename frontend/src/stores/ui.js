// src/stores/ui.js - 修正版

import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';
import { useDisplay } from 'vuetify';

export const useUiStore = defineStore('ui', () => {
    // Vuetifyのブレークポイント検出
    const { mdAndUp } = useDisplay();

    // ⭐ drawer: サイドバーの開閉状態
    // 初期値は画面サイズに応じて決定
    const drawer = ref(mdAndUp.value);

    // ⭐ rail: ミニモード（アイコンのみ表示）かどうか
    const rail = ref(true);

    // ⭐ レスポンシブ判定: PC画面かどうか
    const isDesktop = computed(() => mdAndUp.value);

    // ⭐ サイドバーのモード判定
    const sidebarMode = computed(() => {
        return isDesktop.value ? 'permanent' : 'temporary';
    });

    // ⭐ 画面サイズが変わったときの自動調整（簡潔化）
    watch(mdAndUp, (newValue) => {
        drawer.value = newValue;
    });

    // ⭐ サイドバーの切り替え（完全開閉）
    const toggleDrawer = () => {
        drawer.value = !drawer.value;
    };

    // ⭐ レールモードの切り替え（フル⇔ミニ）
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
});
