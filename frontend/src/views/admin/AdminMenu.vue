<template>
    <!-- ヘッダーコンポーネント -->
    <Header :app-title="t('pages.admin.title')" :page-buttons="headerButtons">
    </Header>

    <!-- 管理者メニューカードグリッド -->
    <MenuCardGrid :items="adminMenuItems" />
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();
const router = useRouter();

// ヘッダーボタン（必要に応じて）
const headerButtons = [];
// const headerButtons = [
//     {
//         name: t('actions.back'),
//         action: goBack,
//         icon: ICONS.nav.divider, // または適切なアイコン
//         type: 'secondary',
//     },
// ];

// 管理者メニューのカード定義
const adminMenuItems = [
    {
        icon: 'group', // ⭐ Material Symbols: ユーザーグループ
        title: 'ユーザー管理',
        to: '/users',
        color: 'blue',
    },
    {
        icon: 'shield', // ⭐ Material Symbols: シールド（権限）
        title: '権限',
        to: '/permissions',
        color: 'red',
    },
    {
        icon: 'settings', // ⭐ Material Symbols: 設定
        title: '設定',
        to: '/admin/settings',
        color: 'grey-darken-1',
    },
    {
        icon: 'analytics', // ⭐ Material Symbols: 分析・ログ
        title: 'ログ',
        to: '/admin/logs',
        color: 'orange',
    },
];

// function goBack() {
//     router.push('/');
// }
</script>
