// src/router/index.js (修正版 - beforeEach統合)

import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from './auth-guard.js';
import { adminGuard } from './admin-guard.js';
import { routes } from '@/constants/routes';

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: routes.HOME,
            name: 'Home',
            component: () => import('@/views/Home.vue'),
            meta: { requiresAuth: true, transition: 'slide-left' },
        },
        {
            path: routes.SETTINGS,
            name: 'Settings',
            component: () => import('@/views/Settings.vue'),
            meta: { requiresAuth: true },
        },
        {
            path: routes.LOGIN,
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: { hideForAuth: true, transition: 'fade' },
        },

        // ⭐ 管理者権限必要
        {
            path: '/admin',
            name: 'AdminMenu',
            component: () => import('@/views/admin/AdminMenu.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
            },
        },
        {
            path: routes.USERS,
            name: 'UserList',
            component: () => import('@/views/users/UserList.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
            path: routes.USER_CREATE,
            name: 'UserCreate',
            component: () => import('@/views/users/UserCreate.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
        },
        {
            path: routes.USER_DETAIL,
            name: 'UserDetail',
            component: () => import('@/views/users/UserDetail.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
            props: true,
        },
        {
            path: routes.USER_UPDATE,
            name: 'UserUpdate',
            component: () => import('@/views/users/UserUpdate.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
            props: true,
        },
        {
            path: routes.USER_DELETE,
            name: 'UserDelete',
            component: () => import('@/views/users/UserDelete.vue'),
            meta: { requiresAuth: true, requiresAdmin: true },
            props: true,
        },
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            redirect: routes.HOME,
        },
    ],
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition;
        } else if (to.hash) {
            return { el: to.hash, behavior: 'smooth' };
        } else {
            return { top: 0 };
        }
    },
});

// ⭐ ナビゲーションガード（統合版）
router.beforeEach(async (to, from, next) => {
    // ローディング表示
    document.body.style.cursor = 'progress';

    // 1. 認証チェック
    const authResult = await authGuard(to, from);
    if (authResult !== true) {
        document.body.style.cursor = '';
        next(authResult);
        return;
    }

    // 2. 管理者権限チェック
    const adminResult = await adminGuard(to, from);
    if (adminResult !== true) {
        document.body.style.cursor = '';
        next(adminResult);
        return;
    }

    // 全てのガードを通過
    document.body.style.cursor = '';
    next();
});

// ⭐ ナビゲーション完了時の処理
router.afterEach((to, from) => {
    // ローディング状態解除（念のため）
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
