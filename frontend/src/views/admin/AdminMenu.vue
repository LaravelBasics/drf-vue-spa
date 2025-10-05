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

const { t } = useI18n();
const router = useRouter();

// ヘッダーボタン（必要に応じて）
// const headerButtons = [
//     {
//         name: t('actions.back'),
//         action: goBack,
//         icon: 'mdi-arrow-left',
//         type: 'secondary',
//     },
// ];

// 管理者メニューのカード定義
const adminMenuItems = [
    {
        icon: 'mdi-account-group',
        title: 'ユーザー管理',
        to: '/users',
        color: 'blue',
    },
    {
        icon: 'mdi-shield-account',
        title: '権限',
        to: '/permissions',
        color: 'red',
    },
    {
        icon: 'mdi-cog',
        title: '設定',
        to: '/admin/settings',
        color: 'grey-darken-1',
    },
    {
        icon: 'mdi-chart-box',
        title: 'ログ',
        to: '/admin/logs',
        color: 'orange',
    },
];

function goBack() {
    router.push('/');
}
</script>
