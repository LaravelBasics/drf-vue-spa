// src/router/admin-guard.js
import { useAuthStore } from '@/stores/auth';
import { routes } from '@/constants/routes';

export const adminGuard = async (to, from) => {
    // 管理者権限が不要なページはスキップ
    if (!to.meta.requiresAdmin) {
        return true;
    }

    const auth = useAuthStore();

    console.log('🔐 Admin Guard:', {
        path: to.path,
        user: auth.user?.employee_id,
        isAdmin: auth.user?.is_admin,
    });

    // ユーザー情報がない場合（念のため）
    if (!auth.user) {
        console.log('⏳ ユーザー情報を待機中...');
        return true;
    }

    // 管理者権限チェック
    if (!auth.user.is_admin) {
        console.warn('🚫 管理者権限がありません');

        // ⭐ ホームにリダイレクト + 通知用フラグ
        return {
            path: routes.HOME,
            replace: true,
            query: {
                unauthorized: 'admin', // ⭐ シンプルなフラグ
            },
        };
    }

    console.log('✅ 管理者権限確認完了');
    return true;
};
