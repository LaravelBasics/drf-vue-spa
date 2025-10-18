<template>
    <Header :app-title="t('pages.home.title')" :breadcrumbs="breadcrumbs" />

    <MenuCardGrid :items="filteredMenuItems" />
</template>

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

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('breadcrumbs.home'),
        to: routes.HOME,
        disabled: true,
    },
]);

// ⭐ マウント時に権限エラーチェック
// 🎯 改善案（オプション）
onMounted(() => {
    // ⭐ loading.value がある場合の重複防止
    if (route.query.unauthorized === 'admin') {
        showWarning('notifications.unauthorized.admin');

        // ⭐ nextTick で確実に実行
        nextTick(() => {
            router.replace({ path: routes.HOME, query: {} });
        });
    }
});

// ⭐ 修正: menuItems を computed にして、t() が locale 変更時に再評価されるようにする
const menuItems = computed(() => [
    {
        id: 'admin',
        icon: ICONS.nav.management,
        title: t('pages.admin.title'), // ⭐ locale変更時に再評価される
        to: routes.ADMIN,
        color: 'secondary',
        requiresAdmin: true,
    },
    {
        id: 'settings',
        icon: ICONS.nav.settings,
        title: t('pages.settings.title'), // ⭐ locale変更時に再評価される
        to: routes.SETTINGS,
        color: COLORS.neutral.medium,
    },
]);

// ⭐ 権限に応じてフィルタリング
const filteredMenuItems = computed(() => {
    return menuItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});
</script>
