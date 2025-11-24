<!-- src/views/Home.vue -->
<script setup>
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ROUTE_NAMES } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const { showWarning } = useApiError();
const { isAdmin } = usePermissions();

// マウント時に権限エラーチェック
onMounted(() => {
    if (route.query.unauthorized === 'admin') {
        showWarning('notifications.unauthorized.admin');
        router.replace({ name: ROUTE_NAMES.HOME, query: {} });
    }
});

const menuItems = computed(() => [
    {
        id: 'admin',
        icon: ICONS.nav.management,
        title: t('pages.admin.title'),
        to: { name: ROUTE_NAMES.ADMIN.MENU },
        color: 'secondary',
        requiresAdmin: true,
    },
    {
        id: 'settings',
        icon: ICONS.nav.settings,
        title: t('pages.settings.title'),
        to: { name: ROUTE_NAMES.SETTINGS },
        color: COLORS.neutral.medium,
    },
]);

// 管理者権限が必要なメニューをフィルタリング
const filteredMenuItems = computed(() => {
    return menuItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});
</script>

<template>
    <Header :app-title="t('pages.home.title')" />

    <MenuCardGrid :items="filteredMenuItems" />
</template>
