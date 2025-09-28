<template>
    <!-- ヘッダーコンポーネント -->
    <Header :app-title="t('pages.home.title')" :page-buttons="headerButtons">
    </Header>

    <!-- メインコンテンツ -->
    <v-container>
        <v-row>
            <v-col cols="12">
                <h1>{{ t('pages.home.orderList') }}</h1>
            </v-col>
        </v-row>

        <!-- デモ用カード -->
        <v-row>
            <v-col cols="12" md="6" lg="4">
                <v-card
                    :elevation="getComponentConfig('card', 'elevation')"
                    :rounded="getComponentConfig('card', 'borderRadius')"
                >
                    <v-card-title class="d-flex align-center">
                        <v-icon
                            :color="colors.current.success"
                            :size="getSize('md')"
                            class="me-2"
                        >
                            {{ getIcon('status', 'success') }}
                        </v-icon>
                        {{ t('status.success') }}
                    </v-card-title>
                    <v-card-text>
                        Lorem ipsum dolor sit amet consectetur.
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { useDesignSystem } from '@/composables/useDesignSystem';
import Header from '@/components/Header.vue';

const { t } = useI18n();
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
