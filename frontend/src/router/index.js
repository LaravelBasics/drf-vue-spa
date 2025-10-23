// src/router/index.js - Vue Routerの設定

import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from './auth-guard.js';
import { adminGuard } from './admin-guard.js';
import { screenSizeGuard } from './screen-size-guard.js';
import { routes } from '@/constants/routes';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: routes.HOME,
            name: 'Home',
            component: () => import('@/views/Home.vue'),
            meta: {
                requiresAuth: true,
                requiresLargeScreen: true,
                transition: 'slide-left',
            },
        },
        {
            path: routes.SETTINGS,
            name: 'Settings',
            component: () => import('@/views/Settings.vue'),
            meta: { requiresAuth: true, requiresLargeScreen: true },
        },
        {
            path: routes.LOGIN,
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: { hideForAuth: true, transition: 'fade' },
        },

        // 管理者専用ページ
        {
            path: '/admin',
            name: 'AdminMenu',
            component: () => import('@/views/admin/AdminMenu.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
        },
        {
            path: routes.USERS,
            name: 'UserList',
            component: () => import('@/views/users/UserList.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
        },
        {
            path: routes.USER_CREATE,
            name: 'UserCreate',
            component: () => import('@/views/users/UserCreate.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
        },
        {
            path: routes.USER_DETAIL,
            name: 'UserDetail',
            component: () => import('@/views/users/UserDetail.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
            props: true,
        },
        {
            path: routes.USER_UPDATE,
            name: 'UserUpdate',
            component: () => import('@/views/users/UserUpdate.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
            props: true,
        },
        {
            path: routes.USER_DELETE,
            name: 'UserDelete',
            component: () => import('@/views/users/UserDelete.vue'),
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
            },
            props: true,
        },

        // エラーページ
        {
            path: routes.UNSUPPORTED_DEVICE,
            name: 'UnsupportedDevice',
            component: () => import('@/views/errors/UnsupportedDevice.vue'),
            meta: { requiresAuth: false },
        },

        // 404ページはホームにリダイレクト
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

// ナビゲーションガード（実行順: 認証 → 画面サイズ → 管理者権限）
router.beforeEach(async (to, from, next) => {
    document.body.style.cursor = 'progress';

    // 1. 認証チェック
    const authResult = await authGuard(to, from);
    if (authResult !== true) {
        document.body.style.cursor = '';
        next(authResult);
        return;
    }

    // 2. 画面サイズチェック（認証後に実行）
    const screenResult = screenSizeGuard(to, from);
    if (screenResult !== true) {
        document.body.style.cursor = '';
        next(screenResult);
        return;
    }

    // 3. 管理者権限チェック
    const adminResult = await adminGuard(to, from);
    if (adminResult !== true) {
        document.body.style.cursor = '';
        next(adminResult);
        return;
    }

    // すべてのガードを通過
    document.body.style.cursor = '';
    next();
});

// ナビゲーション完了後の処理（タイトル設定、フォーカス管理）
router.afterEach((to, from) => {
    document.body.style.cursor = '';
    document.title = to.meta.title || t('app.tabTitle');

    // メインコンテンツにフォーカスを移動（アクセシビリティ対応）
    const main = document.querySelector('main, [role="main"], #app');
    if (main) {
        main.focus();
    }
});

export default router;
