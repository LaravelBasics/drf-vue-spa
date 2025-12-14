// src/router/admin-guard.js - 管理者権限チェック（修正版）

import { useAuthStore } from '@/stores/auth';
import { ROUTE_NAMES } from '@/constants/routes';

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

    // ✅ computed の isAdmin を使用
    // バックエンドの is_admin フィールドをチェック
    // （is_superuser=True または is_staff=True なら true）
    if (!auth.isAdmin) {
        // ホームにリダイレクト + 通知用フラグを設定
        return {
            name: ROUTE_NAMES.HOME,
            replace: true,
            query: {
                unauthorized: 'admin',
            },
        };
    }

    return true;
};
