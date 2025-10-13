<template>
    <Header :app-title="t('pages.home.title')" :breadcrumbs="breadcrumbs" />

    <MenuCardGrid :items="filteredMenuItems" />
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { useNotificationStore } from '@/stores/notification';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const notification = useNotificationStore();
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
onMounted(() => {
    // クエリパラメータに unauthorized=admin がある場合
    if (route.query.unauthorized === 'admin') {
        // 警告通知を表示
        notification.warning(t('notifications.unauthorized.admin'), 5000);

        // ⭐ URLをクリーンにする（クエリパラメータ削除）
        router.replace({ path: routes.HOME, query: {} });
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
