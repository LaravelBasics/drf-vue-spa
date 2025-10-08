<template>
    <Header app-title="設定" :page-buttons="headerButtons"> </Header>
</template>

<script setup>
import Header from '@/components/Header.vue';
import { ICONS } from '@/constants/icons';

const headerButtons = [
    {
        name: '検索',
        action: openOrderSearch,
        icon: ICONS.action.search,
    },
    {
        name: 'CSV',
        action: exportToCSV,
        icon: ICONS.file.excel,
    },
    {
        name: '新規',
        action: createNewOrder,
        icon: ICONS.action.add,
    },
];

function openOrderSearch() {
    // console.log('検索する');
}
function exportToCSV() {
    // console.log('CSV出力処理');
}
function createNewOrder() {
    // console.log('新規受注画面へ遷移');
}
</script>
