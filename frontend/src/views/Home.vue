<template>
    <!-- ヘッダーコンポーネント -->
    <Header :app-title="t('pages.home.title')" :page-buttons="headerButtons">
    </Header>

    <!-- メニューカードグリッド -->
    <MenuCardGrid :items="filteredMenuItems" />
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useDesignSystem } from '@/composables/useDesignSystem';
import { usePermissions } from '@/composables/usePermissions';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { routes } from '@/constants/routes';

const { t } = useI18n();
const router = useRouter();
const { isAdmin } = usePermissions();
const { colors, getIcon, getSize, getComponentConfig } = useDesignSystem();

const headerButtons = [
    {
        name: t('actions.search'),
        action: openOrderSearch,
        icon: 'mdi-magnify',
        type: 'primary',
    },
    {
        name: t('actions.export'),
        action: exportToCSV,
        icon: 'mdi-file-excel',
        type: 'success',
    },
    {
        name: t('actions.add'),
        action: createNewOrder,
        icon: 'mdi-plus',
        type: 'primary',
    },
];

// メニューカードの定義
const menuItems = [
    {
        icon: 'mdi-account-cog',
        title: '管理者メニュー',
        to: routes.ADMIN,
        color: 'primary',
        requiresAdmin: true, // ⭐ 管理者のみ
    },
    {
        icon: 'mdi-account-group',
        title: 'ユーザー管理',
        to: '/users',
        color: 'blue',
        requiresAdmin: true, // ⭐ 管理者のみ
    },
    {
        icon: 'mdi-shopping',
        title: '注文',
        to: '/orders',
        color: 'success',
    },
    {
        icon: 'mdi-package-variant',
        title: '商品',
        to: '/products',
        color: 'orange',
    },
    {
        icon: 'mdi-chart-line',
        title: '分析',
        to: '/analytics',
        color: 'purple',
    },
    {
        icon: 'mdi-cog',
        title: '設定',
        to: '/settings',
        color: 'grey-darken-1',
    },
    {
        icon: 'mdi-shield-account',
        title: '権限',
        onClick: () => {
            console.log('権限管理を開く');
            router.push('/permissions');
        },
        color: 'red',
        requiresAdmin: true,
    },
    {
        icon: 'mdi-file-document',
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
