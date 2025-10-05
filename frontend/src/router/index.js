// src/router/index.js (App.vueでレイアウト管理版)

import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from './auth-guard.js';
import { routes } from '@/constants/routes';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        // ⭐ routes定数を使用してパスを管理
        {
            path: routes.HOME, // '/'
            name: 'Home',
            component: () => import('@/views/Home.vue'),
            meta: { requiresAuth: true, transition: 'slide-left' },
        },

        // ⭐ その他の認証が必要なページ
        {
            path: routes.SETTINGS,
            name: 'Settings',
            component: () => import('@/views/Settings.vue'),
            meta: { requiresAuth: true },
        },

        // ⭐ ログインページ（認証不要）
        {
            path: routes.LOGIN, // '/auth/login'
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: { hideForAuth: true, transition: 'fade' },
        },
        // ユーザー管理（一覧）
        {
            path: routes.USERS,
            name: 'Users',
            component: () => import('@/views/users/UserList.vue'),
            meta: { requiresAuth: true },
        },

        // ユーザー新規作成
        {
            path: routes.USER_CREATE,
            name: 'UserCreate',
            component: () => import('@/views/users/UserCreate.vue'),
            meta: { requiresAuth: true, transition: 'fade' },
        },

        // ユーザー編集
        {
            path: routes.USER_EDIT,
            name: 'UserEdit',
            component: () => import('@/views/users/UserEdit.vue'),
            meta: { requiresAuth: true, transition: 'fade' },
            props: true,
        },

        // ユーザー削除
        {
            path: routes.USER_DELETE,
            name: 'UserDelete',
            component: () => import('@/views/users/UserDelete.vue'),
            meta: { requiresAuth: true, transition: 'fade' },
            props: true,
        },

        // ⭐ 404ページ
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            redirect: routes.LOGIN, // ホームにリダイレクト
        },
    ],
    // ⭐ スクロール位置制御（ちらつき防止）
    scrollBehavior(to, from, savedPosition) {
        // ⭐ ページ遷移時のスクロール位置を制御
        if (savedPosition) {
            // ブラウザの戻る/進むボタン使用時
            return savedPosition;
        } else if (to.hash) {
            // アンカーリンク
            return { el: to.hash, behavior: 'smooth' };
        } else {
            // 通常の遷移は最上部へ（滑らかに）
            return { top: 0, behavior: 'smooth' };
        }
    },
});
// ⭐ ナビゲーション開始時の処理
router.beforeEach(async (to, from, next) => {
    // ページ遷移開始時にローディング状態を設定
    document.body.style.cursor = 'progress';

    // 認証ガード実行
    const result = await authGuard(to, from);

    if (result === true) {
        next();
    } else {
        next(result);
    }
});

// ⭐ ナビゲーション完了時の処理
router.afterEach((to, from) => {
    // ローディング状態解除
    document.body.style.cursor = '';

    // ページタイトル更新
    document.title = to.meta.title || 'ページタイトル更新';

    // アクセシビリティ: スクリーンリーダー用
    const main = document.querySelector('main, [role="main"], #app');
    if (main) {
        main.focus();
    }
});

export default router;
