// src/composables/usePermissions.js - 権限管理

import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';

export const usePermissions = () => {
    const auth = useAuthStore();

    // 管理者権限を持つか判定
    const isAdmin = computed(() => {
        return auth.user?.is_admin === true;
    });

    // アクティブなユーザーか判定
    const isActive = computed(() => {
        return auth.user?.is_active === true;
    });

    return {
        isAdmin,
        isActive,
    };
};
