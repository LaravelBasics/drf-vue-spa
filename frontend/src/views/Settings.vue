<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const { t } = useI18n();

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

function openOrderSearch() {
    // TODO: 検索処理を実装
}
</script>

<template>
    <Header
        :app-title="t('pages.settings.title')"
        :breadcrumbs="breadcrumbs"
        :page-buttons="headerButtons"
    />

    <!-- TODO: 設定画面のコンテンツを実装 -->
</template>
