// C:\Users\pvufx\Desktop\template\frontend\src\stores\ui.js

import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useUiStore = defineStore(
    'ui',
    () => {
        const drawer = ref(false);
        return { drawer };
    },
    {
        // 💡 ここに永続化設定を追加
        persist: true,
    },
);
