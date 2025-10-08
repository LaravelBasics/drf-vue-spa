<template>
    <!-- ヘッダーコンポーネント -->
    <Header :app-title="t('pages.home.title')" :page-buttons="headerButtons">
    </Header>

    <!-- メニューカードグリッド -->
    <MenuCardGrid :items="filteredMenuItems" />
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { useDesignSystem } from '@/composables/useDesignSystem';
import { usePermissions } from '@/composables/usePermissions';
import { useNotificationStore } from '@/stores/notification';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const notification = useNotificationStore();
const { isAdmin } = usePermissions();
const { colors, getIcon, getSize, getComponentConfig } = useDesignSystem();

// ⭐ マウント時に権限エラーチェック
onMounted(() => {
    // クエリパラメータに unauthorized=admin がある場合
    if (route.query.unauthorized === 'admin') {
        // 警告通知を表示
        notification.warning('この機能は管理者のみ利用できます', 5000);

        // ⭐ URLをクリーンにする（クエリパラメータ削除）
        router.replace({ path: routes.HOME, query: {} });
    }
});

const headerButtons = [
    {
        name: t('actions.search'),
        action: openOrderSearch,
        icon: ICONS.action.search,
        type: 'primary',
    },
    {
        name: t('actions.export'),
        action: exportToCSV,
        icon: ICONS.file.excel,
        type: 'success',
    },
    {
        name: t('actions.add'),
        action: createNewOrder,
        icon: ICONS.action.add,
        type: 'primary',
    },
];

// メニューカードの定義
const menuItems = [
    {
        icon: ICONS.nav.management, // ⭐ 管理者メニュー
        title: '管理者メニュー',
        to: routes.ADMIN,
        color: 'primary',
        requiresAdmin: true,
    },
    {
        icon: 'group', // ⭐ ユーザーグループ
        title: 'ユーザー管理',
        to: '/users',
        color: 'blue',
        requiresAdmin: true,
    },
    {
        icon: 'shopping_cart', // ⭐ 注文
        title: '注文',
        to: '/orders',
        color: 'success',
    },
    {
        icon: 'inventory_2', // ⭐ 商品・在庫
        title: '商品',
        to: '/products',
        color: 'orange',
    },
    {
        icon: 'analytics', // ⭐ 分析
        title: '分析',
        to: '/analytics',
        color: 'purple',
    },
    {
        icon: 'settings', // ⭐ 設定
        title: '設定',
        to: '/settings',
        color: 'grey-darken-1',
    },
    {
        icon: 'shield', // ⭐ 権限
        title: '権限',
        onClick: () => {
            console.log('権限管理を開く');
            router.push('/permissions');
        },
        color: 'red',
        requiresAdmin: true,
    },
    {
        icon: 'description', // ⭐ レポート
        title: 'レポート',
        to: '/reports',
        color: 'teal',
    },
];

// ⭐ 権限に応じてフィルタリング
const filteredMenuItems = computed(() => {
    return menuItems.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});

function openOrderSearch() {
    console.log('Search orders');
}

function exportToCSV() {
    console.log('Export to CSV');
}

function createNewOrder() {
    console.log('Create new order');
}
</script>
