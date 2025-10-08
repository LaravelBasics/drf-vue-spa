<template>
    <v-container fluid>
        <v-row>
            <v-col
                v-for="(item, index) in items"
                :key="index"
                cols="12"
                sm="6"
                md="4"
                lg="3"
                xl="2"
            >
                <MenuCard
                    :icon="item.icon"
                    :title="item.title"
                    :to="item.to"
                    :href="item.href"
                    :color="item.color || 'primary'"
                    :icon-size="item.iconSize || 64"
                    @click="item.onClick && item.onClick()"
                />
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import MenuCard from './MenuCard.vue';

defineProps({
    items: {
        type: Array,
        required: true,
        // ⭐ 例: [{ icon: 'admin_panel_settings', title: '管理', to: '/admin' }]
        // Material Symbols アイコン名を使用
    },
});
</script>
