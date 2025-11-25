// src/router/index.js - メインルーター（モジュール統合版）

import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from './auth-guard.js';
import { adminGuard } from './admin-guard.js';
import { routes } from '@/constants/routes';
import { ROUTE_NAMES } from '@/constants/routes';
import i18n from '@/plugins/i18n';

// ★ モジュール別ルートをインポート
import authRoutes from './modules/auth.js';
import adminRoutes from './modules/admin.js';
import usersRoutes from './modules/users.js';

const { t } = i18n.global;

const router = createRouter({
    history: createWebHistory(),
    routes: [
        // ===== 基本ルート =====
        {
            path: routes.HOME,
            name: 'Home',
            component: () => import('@/views/Home.vue'),
            meta: {
                requiresAuth: true,
                transition: 'slide-left',
                breadcrumb: 'breadcrumbs.home',
                title: t('pages.home.title'),
            },
        },
        {
            path: routes.SETTINGS,
            name: 'Settings',
            component: () => import('@/views/Settings.vue'),
            meta: {
                requiresAuth: true,
                breadcrumb: 'breadcrumbs.settings',
                title: t('pages.settings.title'),
            },
        },

        // ===== ログイン認証ルート（モジュールから展開） =====
        ...authRoutes,

        // ===== 管理者ルート =====
        {
            path: routes.ADMIN.ROOT, // '/admin'
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                breadcrumb: 'breadcrumbs.admin',
            },
            children: [
                // 管理画面トップ（モジュール）
                adminRoutes,

                // ユーザー管理（モジュール）
                usersRoutes,

                // 将来的に追加するモジュール
            ],
        },

        // ===== 404ページ =====
        {
            path: '/:pathMatch(.*)*',
            name: 'NotFound',
            redirect: (to) => {
                return { name: ROUTE_NAMES.HOME, params: {} };
            },
            meta: { breadcrumb: false },
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

// ナビゲーションガード
router.beforeEach(async (to, from, next) => {
    document.body.style.cursor = 'progress';

    const authResult = await authGuard(to, from);
    if (authResult !== true) {
        document.body.style.cursor = '';
        next(authResult);
        return;
    }

    const adminResult = await adminGuard(to, from);
    if (adminResult !== true) {
        document.body.style.cursor = '';
        next(adminResult);
        return;
    }

    document.body.style.cursor = '';
    next();
});

router.afterEach((to) => {
    document.body.style.cursor = '';
    document.title = to.meta.title || t('app.tabTitle');

    const main = document.querySelector('main, [role="main"], #app');
    if (main) {
        main.focus();
    }
});

export default router;
