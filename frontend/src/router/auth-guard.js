// src/router/auth-guard.js (修正版 - routes定数使用)

import { useAuthStore } from '@/stores/auth';
import { routes } from '@/constants/routes';

export const authGuard = async (to, from) => {
    const auth = useAuthStore();

    console.log('🔍 Auth Guard:', {
        to: to.path,
        from: from.path,
        hasUser: !!auth.user,
        requiresAuth: to.meta.requiresAuth,
        hideForAuth: to.meta.hideForAuth,
    });

    // ⭐ ログイン済みユーザーがログインページにアクセスした場合
    if (to.meta.hideForAuth && auth.user) {
        // ⭐ ホームページにリダイレクト（定数使用）
        console.log('✅ ログイン済みユーザー - ホームにリダイレクト');
        return { path: routes.HOME, replace: true };
    }

    // 認証が必要なページの場合
    if (to.meta.requiresAuth) {
        // ⭐ 初期化が完了していない場合は待機
        if (!auth.initialized) {
            console.log('⏳ 認証状態を初期化中...');
            await auth.initialize();
        }

        // ⭐ ユーザー情報がない場合のみfetchUser実行
        if (!auth.user && !auth.loading) {
            console.log('🔄 ユーザー情報を取得中...');
            try {
                await auth.fetchUser();
            } catch (error) {
                console.error('❌ 認証チェック中にエラーが発生:', error);
                // fetchUserが失敗した場合、userはnullのまま
            }
        }

        // ⭐ 最終的な認証チェック
        if (!auth.user) {
            console.log('🚫 認証が必要ですが未ログイン状態');
            return {
                path: routes.LOGIN, // 定数使用
                query: { next: to.fullPath },
                replace: true,
            };
        }
    }

    console.log('✅ Auth Guard 通過');
    return true;
};
