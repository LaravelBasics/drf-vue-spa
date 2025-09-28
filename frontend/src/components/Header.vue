<!-- src/components/Header.vue - 修正版（防御的コーディング） -->
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

        <v-btn
            v-for="(button, index) in props.pageButtons"
            :key="index"
            variant="outlined"
            :color="getButtonColor(button.type)"
            class="mx-3 px-2 text-subtitle-2"
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

const props = defineProps({
    appTitle: {
        type: String,
        default: 'デフォルトのタイトル名',
    },
    headerHeight: {
        type: [String, Number],
        default: 56,
    },
    pageButtons: {
        type: Array,
        default: () => [],
    },
});

const { colors, getSize, getComponentConfig } = useDesignSystem();

// 防御的コーディング: 安全な値を計算
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
    // colors.current が存在するかチェック
    if (!colors.value.current) {
        return 'grey-darken-3'; // フォールバック色
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
