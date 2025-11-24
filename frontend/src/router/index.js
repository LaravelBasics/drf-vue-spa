// src/router/index.js - App.vueでレイアウト制御＋Wrapperパターン

import { createRouter, createWebHistory } from 'vue-router';
import { authGuard } from './auth-guard.js';
import { adminGuard } from './admin-guard.js';
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
        {
            path: routes.LOGIN,
            name: 'Login',
            component: () => import('@/views/Login.vue'),
            meta: {
                hideForAuth: true,
                transition: 'fade',
                breadcrumb: false,
                title: t('auth.loginTitle'),
            },
        },

        // 🎯 管理者専用ページ（componentオプション省略でスキップ）
        {
            path: routes.ADMIN.ROOT, // '/admin'
            // 💡 componentを省略すると、App.vueの<router-view>が子を直接レンダリング
            meta: {
                requiresAuth: true,
                requiresAdmin: true,
                breadcrumb: 'breadcrumbs.admin',
                title: t('pages.admin.title'),
            },
            children: [
                {
                    path: routes.ADMIN.INDEX, // ''
                    name: 'AdminMenu',
                    component: () => import('@/views/admin/AdminMenu.vue'),
                },
                {
                    path: routes.ADMIN.USERS.SEGMENT, // 'users'
                    // 💡 ここもパンくず用の階層を作るだけなのでcomponent省略
                    meta: {
                        breadcrumb: 'breadcrumbs.users.list',
                    },
                    children: [
                        // ① ユーザー一覧
                        {
                            path: routes.ADMIN.USERS.INDEX, // ''
                            name: 'UserList',
                            component: () =>
                                import('@/views/users/UserList.vue'),
                            meta: {
                                title: t('pages.users.list.title'),
                            },
                        },
                        // ② 新規作成
                        {
                            path: routes.ADMIN.USERS.CREATE, // 'create'
                            name: 'UserCreate',
                            component: () =>
                                import('@/views/users/UserCreate.vue'),
                            meta: {
                                breadcrumb: 'breadcrumbs.users.create',
                                title: t('pages.users.create.title'),
                            },
                        },
                        // ③ 【重要】特定ユーザーのコンテキスト（Wrapper）
                        {
                            path: routes.ADMIN.USERS.DETAIL, // ':id'
                            component: () =>
                                import('@/views/users/UserWrapper.vue'), // 👈 ここだけcomponentが必要！
                            meta: {
                                breadcrumb: 'breadcrumbs.users.detail', // "詳細"
                                title: t('pages.users.detail.title'),
                            },
                            children: [
                                // ③-a: 詳細画面（デフォルト）
                                {
                                    path: '', // /admin/users/:id
                                    name: 'UserDetail', // 👈 これが実際の遷移先
                                    component: () =>
                                        import('@/views/users/UserDetail.vue'),
                                    meta: {
                                        title: t('pages.users.detail.title'),
                                        // 👇 子は表示しない（親で代表）
                                        breadcrumb: false,
                                    },
                                    props: true,
                                },
                                // ③-b: 編集画面
                                {
                                    path: 'update', // /admin/users/:id/update
                                    name: 'UserUpdate',
                                    component: () =>
                                        import('@/views/users/UserUpdate.vue'),
                                    meta: {
                                        breadcrumb: 'breadcrumbs.users.update', // "編集"
                                        title: t('pages.users.update.title'),
                                    },
                                    props: true,
                                },
                                // ③-c: 削除確認画面
                                {
                                    path: 'delete', // /admin/users/:id/delete
                                    name: 'UserDelete',
                                    component: () =>
                                        import('@/views/users/UserDelete.vue'),
                                    meta: {
                                        breadcrumb: 'breadcrumbs.users.delete', // "削除"
                                        title: t('pages.users.delete.title'),
                                    },
                                    props: true,
                                },
                            ],
                        },
                    ],
                },
            ],
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

// ナビゲーションガード（実行順: 認証 → 管理者権限）
router.beforeEach(async (to, from, next) => {
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

    // すべてのガードを通過
    document.body.style.cursor = '';
    next();
});

// ナビゲーション完了後の処理
router.afterEach((to) => {
    document.body.style.cursor = '';
    document.title = to.meta.title || t('app.tabTitle');

    // メインコンテンツにフォーカスを移動（アクセシビリティ対応）
    const main = document.querySelector('main, [role="main"], #app');
    if (main) {
        main.focus();
    }
});

export default router;
