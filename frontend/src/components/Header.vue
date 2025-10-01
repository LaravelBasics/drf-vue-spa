<template>
    <v-app-bar
        :color="safeColors.surface"
        :elevation="safeElevation"
        :height="safeHeight"
        app
    >
        <v-app-bar-title class="d-flex align-center">
            <span class="text-h6 font-weight-bold">{{ props.appTitle }}</span>
        </v-app-bar-title>

        <!-- パンくずリスト -->
        <v-breadcrumbs
            v-if="breadcrumbs && breadcrumbs.length > 0"
            :items="breadcrumbs"
            class="pa-0 mx-4"
            density="compact"
        >
            <template v-slot:divider>
                <v-icon :size="ICON_SIZES.md">{{ ICONS.nav.divider }}</v-icon>
            </template>

            <template v-slot:item="{ item }">
                <v-breadcrumbs-item
                    :to="item.to"
                    :disabled="item.disabled"
                    class="text-subtitle-2"
                >
                    {{ item.title }}
                </v-breadcrumbs-item>
            </template>
        </v-breadcrumbs>

        <v-spacer></v-spacer>

        <v-btn
            v-for="(button, index) in props.pageButtons"
            :key="index"
            variant="outlined"
            :color="getButtonColor(button.type)"
            class="mx-1 px-2 text-subtitle-2"
            @click="button.action"
        >
            <v-icon :icon="button.icon" :size="safeIconSize"></v-icon>
            {{ button.name }}
        </v-btn>
    </v-app-bar>
</template>

<script setup>
import { computed } from 'vue';
import { useDesignSystem } from '@/composables/useDesignSystem';
import { ICONS } from '@/constants/icons.js';
import { ICON_SIZES } from '../constants/theme';

const props = defineProps({
    appTitle: {
        type: String,
        default: 'デフォルトのタイトル名',
    },
    headerHeight: {
        type: [String, Number],
        default: 64, // パンくず分少し高く
    },
    pageButtons: {
        type: Array,
        default: () => [],
    },
    breadcrumbs: {
        type: Array,
        default: () => [],
    },
});

const { colors, getSize, getComponentConfig } = useDesignSystem();

const safeColors = computed(() => ({
    surface:
        colors.value.current?.surface ||
        colors.value.background?.surface ||
        '#FFFFFF',
}));

const safeElevation = computed(() => {
    const headerConfig = getComponentConfig('header');
    return headerConfig?.elevation || 4;
});

const safeHeight = computed(() => {
    const headerConfig = getComponentConfig('header');
    return headerConfig?.height?.desktop || 64;
});

const safeIconSize = computed(() => {
    return getSize('sm') || 20;
});

function getButtonColor(type = 'primary') {
    if (!colors.value.current) {
        return 'grey-darken-3';
    }

    const colorMap = {
        primary: colors.value.current.primary || '#1976D2',
        secondary: colors.value.current.secondary || '#424242',
        success: colors.value.current.success || '#4CAF50',
        error: colors.value.current.error || '#F44336',
        warning: colors.value.current.warning || '#FF9800',
        info: colors.value.current.info || '#2196F3',
    };

    return colorMap[type] || colorMap.primary;
}
</script>
