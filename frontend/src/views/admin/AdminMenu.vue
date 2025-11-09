<!-- src/views/admin/AdminMenu.vue - 管理者メニュー画面 -->
<script setup>
import { computed } from 'vue';
import { userRoutes } from '@/constants/routes';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();

// 管理者メニューカードの定義
const adminMenuItems = computed(() => [
    {
        id: 'users',
        icon: ICONS.menu.users,
        title: t('pages.users.list.title'),
        to: userRoutes.list(),
        color: 'primary',
    },
]);
</script>

<template>
    <Header :app-title="t('pages.admin.title')" />

    <MenuCardGrid :items="adminMenuItems" />
</template>
