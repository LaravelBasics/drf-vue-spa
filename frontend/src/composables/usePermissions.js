// src/composables/usePermissions.js

import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

export const usePermissions = () => {
    const auth = useAuthStore();

    // 管理者かどうか
    const isAdmin = computed(() => {
        return auth.user?.is_admin === true;
    });

    // アクティブなユーザーかどうか
    const isActive = computed(() => {
        return auth.user?.is_active === true;
    });

    return {
        isAdmin,
        isActive,
    };
};
