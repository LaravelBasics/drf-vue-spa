<script setup>
import MenuCard from './MenuCard.vue';

defineProps({
    items: {
        type: Array,
        required: true,
        validator: (items) => items.every((item) => item.id),
        // ⭐ 例: [{ id: 'admin', icon: 'admin_panel_settings', title: '管理', to: '/admin' }]
        // ⭐ id プロパティを追加することで、keyの問題を解決
    },
});
</script>

<template>
    <v-container fluid class="pa-6">
        <v-row>
            <v-col
                v-for="item in items"
                :key="item.id"
                cols="9"
                sm="4"
                md="3"
                lg="2"
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
