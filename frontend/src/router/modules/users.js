// src/router/modules/users.js - ユーザー管理ルート
import { routes } from '@/constants/routes';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

export default {
    path: routes.ADMIN.USERS.SEGMENT, // 'users'
    meta: {
        breadcrumb: 'breadcrumbs.users.list',
    },
    children: [
        // ① ユーザー一覧
        {
            path: routes.ADMIN.USERS.INDEX, // ''
            name: 'UserList',
            component: () => import('@/views/users/UserList.vue'),
            meta: {
                title: t('pages.users.list.title'),
            },
        },

        // ② 新規作成
        {
            path: routes.ADMIN.USERS.CREATE, // 'create'
            name: 'UserCreate',
            component: () => import('@/views/users/UserCreate.vue'),
            meta: {
                breadcrumb: 'breadcrumbs.users.create',
                title: t('pages.users.create.title'),
            },
        },

        // ③ 特定ユーザーのコンテキスト（Wrapper）
        {
            path: routes.ADMIN.USERS.DETAIL, // ':id'
            component: () => import('@/views/users/UserWrapper.vue'),
            meta: {
                breadcrumb: 'breadcrumbs.users.detail',
            },
            children: [
                // ③-a: 詳細画面
                {
                    path: '', // /admin/users/:id
                    name: 'UserDetail',
                    component: () => import('@/views/users/UserDetail.vue'),
                    meta: {
                        breadcrumb: false,
                        title: t('pages.users.detail.title'),
                    },
                    props: true,
                },

                // ③-b: 編集画面
                {
                    path: routes.ADMIN.USERS.UPDATE, // 'update'
                    name: 'UserUpdate',
                    component: () => import('@/views/users/UserUpdate.vue'),
                    meta: {
                        breadcrumb: 'breadcrumbs.users.update',
                        title: t('pages.users.update.title'),
                    },
                    props: true,
                },

                // ③-c: 削除画面
                {
                    path: routes.ADMIN.USERS.DELETE, // 'delete'
                    name: 'UserDelete',
                    component: () => import('@/views/users/UserDelete.vue'),
                    meta: {
                        breadcrumb: 'breadcrumbs.users.delete',
                        title: t('pages.users.delete.title'),
                    },
                    props: true,
                },
            ],
        },
    ],
};
