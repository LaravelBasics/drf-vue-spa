<script setup>
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const { showWarning } = useApiError();
const { isAdmin } = usePermissions();

const breadcrumbs = computed(() => [
    {
        title: t('breadcrumbs.home'),
        to: routes.HOME,
        disabled: true,
    },
]);

// ⭐ マウント時に権限エラーチェック（nextTick 不要）
onMounted(() => {
    if (route.query.unauthorized === 'admin') {
        showWarning('notifications.unauthorized.admin');
        // ⭐ nextTick 不要（router.replace は非同期だが await 不要）
        router.replace({ path: routes.HOME, query: {} });
    }
});

const menuItems = computed(() => [
    {
        id: 'admin',
        icon: ICONS.nav.management,
        title: t('pages.admin.title'),
        to: routes.ADMIN,
        color: 'secondary',
        requiresAdmin: true,
    },
    {
        id: 'settings',
        icon: ICONS.nav.settings,
        title: t('pages.settings.title'),
        to: routes.SETTINGS,
        color: COLORS.neutral.medium,
    },
]);

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
    <Header :app-title="t('pages.home.title')" :breadcrumbs="breadcrumbs" />

    <MenuCardGrid :items="filteredMenuItems" />
</template>
