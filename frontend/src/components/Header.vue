<script setup>
import { computed } from 'vue';
import { useTheme } from 'vuetify';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES, THEME_CONFIG, COMPONENT_CONFIGS } from '@/constants/theme';

const theme = useTheme();

const props = defineProps({
    appTitle: {
        type: String,
        default: 'デフォルトのタイトル名',
    },
    headerHeight: {
        type: [String, Number],
        default: 64,
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

const surfaceColor = computed(
    () =>
        theme.global.current.value?.colors?.surface ||
        THEME_CONFIG.colors.light.surface,
);

const elevation = computed(() => COMPONENT_CONFIGS.header?.elevation || 4);

const headerHeight = computed(
    () => COMPONENT_CONFIGS.header?.height?.desktop || 64,
);

function getButtonColor(type = 'primary') {
    const colors = theme.global.current.value?.colors;
    const colorMap = {
        primary: colors?.primary || THEME_CONFIG.colors.light.primary,
        secondary: colors?.secondary || THEME_CONFIG.colors.light.secondary,
        success: colors?.success || THEME_CONFIG.colors.light.success,
        error: colors?.error || THEME_CONFIG.colors.light.error,
        warning: colors?.warning || THEME_CONFIG.colors.light.warning,
        info: colors?.info || THEME_CONFIG.colors.light.info,
    };

    return colorMap[type] || colorMap.primary;
}
</script>

<template>
    <v-app-bar
        :color="surfaceColor"
        :elevation="elevation"
        :height="headerHeight"
        app
    >
        <div
            class="ml-5 d-none d-sm-inline align-center"
            style="min-width: 0; flex-shrink: 1"
        >
            <span class="text-h6 font-weight-bold text-truncate">
                {{ props.appTitle }}
            </span>
        </div>

        <div
            v-if="breadcrumbs && breadcrumbs.length > 0"
            class="flex-grow-1 d-flex justify-center"
        >
            <v-breadcrumbs
                :items="breadcrumbs"
                class="pa-0 d-none d-sm-inline"
                density="compact"
            >
                <template v-slot:divider>
                    <v-icon :size="ICON_SIZES.sm">{{
                        ICONS.nav.divider
                    }}</v-icon>
                </template>

                <template v-slot:item="{ item }">
                    <v-breadcrumbs-item
                        :to="item.to"
                        :disabled="item.disabled"
                        class="text-caption text-sm-subtitle-2"
                        :color="item.disabled ? 'default' : 'primary'"
                    >
                        {{ item.title }}
                    </v-breadcrumbs-item>
                </template>
            </v-breadcrumbs>
        </div>

        <v-spacer v-else></v-spacer>

        <div class="d-flex align-center" style="flex-shrink: 0">
            <v-btn
                v-for="(button, index) in props.pageButtons"
                :key="index"
                variant="outlined"
                :color="getButtonColor(button.type)"
                class="mr-4 px-2 text-subtitle-2"
                @click="button.action"
            >
                <v-icon :icon="button.icon" :size="ICON_SIZES.sm"></v-icon>
                <span>{{ button.name }}</span>
            </v-btn>
        </div>
    </v-app-bar>
</template>
