// src/router/modules/admin.js - 管理画面トップ
import { routes } from '@/constants/routes';
import i18n from '@/plugins/i18n';

const { t } = i18n.global;

export default {
    path: routes.ADMIN.INDEX,
    name: 'AdminMenu',
    component: () => import('@/views/admin/AdminMenu.vue'),
    meta: {
        title: t('pages.admin.title'),
    },
};
