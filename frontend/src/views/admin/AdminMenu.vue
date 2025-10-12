<template>
    <!-- ヘッダーコンポーネント -->
    <Header :app-title="t('pages.admin.title')" :breadcrumbs="breadcrumbs">
    </Header>

    <!-- 管理者メニューカードグリッド -->
    <MenuCardGrid :items="adminMenuItems" />
</template>

<script setup>
import { computed } from 'vue';
import { routes } from '@/constants/routes';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();

// パンくずリスト
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

// 管理者メニューのカード定義
const adminMenuItems = computed(() => [
    {
        icon: ICONS.menu.users,
        title: t('pages.users.list.title'),
        to: routes.USERS,
        color: 'primary',
    },
]);
</script>
