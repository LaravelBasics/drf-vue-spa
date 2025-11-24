// src/router/modules/auth.js - 認証関連ルート
import { routes } from '@/constants/routes';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

export default [
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
];
