// src/router/auth-guard.js - 認証状態チェック

import { useAuthStore } from '@/stores/auth';
import { routes } from '@/constants/routes';

export const authGuard = async (to, from) => {
    const auth = useAuthStore();

    // ログイン済みユーザーがログインページにアクセスした場合
    if (to.meta.hideForAuth && auth.user) {
        return { path: routes.HOME, replace: true };
    }

    // 認証が必要なページの場合
    if (to.meta.requiresAuth) {
        // 初期化が完了していない場合は待機
        if (!auth.initialized) {
            await auth.initialize();
        }

        // ユーザー情報がない場合のみ取得を試みる
        if (!auth.user && !auth.loading) {
            try {
                await auth.fetchUser();
            } catch (error) {
                // fetchUser失敗時はuserがnullのまま
            }
        }

        // 最終的な認証チェック
        if (!auth.user) {
            return {
                path: routes.LOGIN,
                query: { next: to.fullPath },
                replace: true,
            };
        }
    }

    return true;
};
