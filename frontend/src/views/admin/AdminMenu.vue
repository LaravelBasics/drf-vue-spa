<!-- src/views/admin/AdminMenu.vue - 管理者メニュー画面 -->
<script setup>
import { computed } from 'vue';
import { routes } from '@/constants/routes';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();

// パンくずリスト定義
const breadcrumbs = computed(() => [
    {
        title: t('breadcrumbs.home'),
        to: routes.HOME,
        disabled: false,
    },
    {
        title: t('breadcrumbs.admin'),
        to: routes.ADMIN,
        disabled: true,
    },
]);

// 管理者メニューカードの定義
const adminMenuItems = computed(() => [
    {
        id: 'users',
        icon: ICONS.menu.users,
        title: t('pages.users.list.title'),
        to: routes.USERS,
        color: 'primary',
    },
]);
</script>

<template>
    <Header :app-title="t('pages.admin.title')" :breadcrumbs="breadcrumbs" />

    <MenuCardGrid :items="adminMenuItems" />
</template>
