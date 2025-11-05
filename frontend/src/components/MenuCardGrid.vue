<script setup>
import MenuCard from './MenuCard.vue';

defineProps({
    items: {
        type: Array,
        required: true,
        // 各アイテムに一意のidが必須（v-forのkey用）
        validator: (items) => items.every((item) => item.id),
    },
});
</script>

<template>
    <!-- ✅ pa-4 でシンプルに -->
    <v-container fluid class="pa-4">
        <v-row class="ga-0">
            <v-col
                v-for="item in items"
                :key="item.id"
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
                    :icon-size="item.iconSize"
                />
            </v-col>
        </v-row>
    </v-container>
</template>
