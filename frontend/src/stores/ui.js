// C:\Users\pvufx\Desktop\template\frontend\src\stores\ui.js

import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUiStore = defineStore(
    'ui',
    () => {
        // ⭐ drawer: サイドバーの開閉状態
        const drawer = ref(true);

        // ⭐ rail: ミニモード（アイコンのみ表示）かどうか
        const rail = ref(true);

        // ⭐ サイドバーの切り替え（完全開閉）
        const toggleDrawer = () => {
            drawer.value = !drawer.value;
        };

        // ⭐ レールモードの切り替え（フル⇔ミニ）
        const toggleRail = () => {
            rail.value = !rail.value;
        };

        return {
            drawer,
            rail,
            toggleDrawer,
            toggleRail,
        };
    },
    {
        persist: true,
    },
);
