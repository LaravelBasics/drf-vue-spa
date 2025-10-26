// src/router/index.js - 定数を使ったchildren構造

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
                breadcrumb: 'breadcrumbs.home',
            },
        },
        {
            path: routes.SETTINGS,
            name: 'Settings',
            component: () => import('@/views/Settings.vue'),
            meta: {
                requiresAuth: true,
                requiresLargeScreen: true,
                breadcrumb: 'breadcrumbs.settings',
            },
        },
        {
            path: routes.LOGIN,
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: {
                hideForAuth: true,
                transition: 'fade',
                breadcrumb: false,
            },
        },

        // 管理者専用ページ（階層構造 + 定数使用）
        {
            path: routes.ADMIN.ROOT, // '/admin'
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                requiresLargeScreen: true,
                breadcrumb: 'breadcrumbs.admin',
            },
            children: [
                {
                    path: routes.ADMIN.INDEX, // ''
                    name: 'AdminMenu',
                    component: () => import('@/views/admin/AdminMenu.vue'),
                },
                {
                    path: routes.ADMIN.USERS.SEGMENT, // 'users'
                    meta: {
                        breadcrumb: 'breadcrumbs.users.list',
                    },
                    children: [
                        {
                            path: routes.ADMIN.USERS.INDEX, // ''
                            name: 'UserList',
                            component: () =>
                                import('@/views/users/UserList.vue'),
                        },
                        {
                            path: routes.ADMIN.USERS.CREATE, // 'create'
                            name: 'UserCreate',
                            component: () =>
                                import('@/views/users/UserCreate.vue'),
                            meta: {
                                breadcrumb: 'breadcrumbs.users.create',
                            },
                        },
                        {
                            path: routes.ADMIN.USERS.DETAIL, // ':id'
                            name: 'UserDetail',
                            component: () =>
                                import('@/views/users/UserDetail.vue'),
                            meta: {
                                breadcrumb: 'breadcrumbs.users.detail',
                            },
                            props: true,
                        },
                        {
                            path: routes.ADMIN.USERS.UPDATE, // ':id/update'
                            name: 'UserUpdate',
                            component: () =>
                                import('@/views/users/UserUpdate.vue'),
                            meta: {
                                breadcrumb: 'breadcrumbs.users.update',
                            },
                            props: true,
                        },
                        {
                            path: routes.ADMIN.USERS.DELETE, // ':id/delete'
                            name: 'UserDelete',
                            component: () =>
                                import('@/views/users/UserDelete.vue'),
                            meta: {
                                breadcrumb: 'breadcrumbs.users.delete',
                            },
                            props: true,
                        },
                    ],
                },
            ],
        },

        // エラーページ
        {
            path: routes.UNSUPPORTED_DEVICE,
            name: 'UnsupportedDevice',
            component: () => import('@/views/errors/UnsupportedDevice.vue'),
            meta: {
                requiresAuth: false,
                breadcrumb: false,
            },
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
