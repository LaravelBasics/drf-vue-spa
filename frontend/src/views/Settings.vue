<template>
    <Header
        :app-title="t('pages.settings.title')"
        :breadcrumbs="breadcrumbs"
        :page-buttons="headerButtons"
    />

    <!-- <MenuCardGrid :items="filteredMenuItems" /> -->
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const { isAdmin } = usePermissions();

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('breadcrumbs.home'),
        to: routes.HOME,
        disabled: false,
    },
    {
        title: t('breadcrumbs.settings'),
        to: routes.SETTINGS,
        disabled: true,
    },
]);

const headerButtons = computed(() => [
    {
        name: t('buttons.search'),
        action: openOrderSearch,
        icon: ICONS.buttons.search,
    },
]);

// const menuItems = computed(() => [
//     {
//         id: 'admin',
//         icon: ICONS.nav.management,
//         title: t('pages.admin.title'),
//         to: routes.ADMIN,
//         color: 'secondary',
//         requiresAdmin: true,
//     },
//     {
//         id: 'settings',
//         icon: ICONS.nav.settings,
//         title: t('pages.settings.title'),
//         to: routes.SETTINGS,
//         color: COLORS.neutral.medium,
//     },
// ]);

// ⭐ 権限に応じてフィルタリング
// const filteredMenuItems = computed(() => {
//     return menuItems.value.filter((item) => {
//         if (item.requiresAdmin) {
//             return isAdmin.value;
//         }
//         return true;
//     });
// });

function openOrderSearch() {
    console.log('検索する');
}
</script>
