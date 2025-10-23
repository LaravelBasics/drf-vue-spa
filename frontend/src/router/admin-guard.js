// src/router/admin-guard.js - 管理者権限チェック

import { useAuthStore } from '@/stores/auth';
import { routes } from '@/constants/routes';

export const adminGuard = async (to, from) => {
    // 管理者権限が不要なページはスキップ
    if (!to.meta.requiresAdmin) {
        return true;
    }

    const auth = useAuthStore();

    // ユーザー情報がない場合（念のため）
    if (!auth.user) {
        return true;
    }

    // 管理者権限チェック
    if (!auth.user.is_admin) {
        // ホームにリダイレクト + 通知用フラグを設定
        return {
            path: routes.HOME,
            replace: true,
            query: {
                unauthorized: 'admin',
            },
        };
    }

    return true;
};
