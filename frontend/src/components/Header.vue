<!-- src/components/Header.vue -->
<script setup>
import { computed } from 'vue';
import { useTheme } from 'vuetify';
import { useBreadcrumbs } from '@/composables/useBreadcrumbs';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES, THEME_CONFIG } from '@/constants/theme';

const theme = useTheme();
const { breadcrumbs: autoBreadcrumbs } = useBreadcrumbs();

const props = defineProps({
    appTitle: {
        type: String,
        default: 'デフォルトのタイトル名',
    },
    headerHeight: {
        type: [String, Number],
        default: 64,
    },
    headerElevation: {
        type: [String, Number],
        default: 2,
    },
    pageButtons: {
        type: Array,
        default: () => [],
    },
    breadcrumbs: {
        type: Array,
        default: null,
    },
});

const surfaceColor = computed(
    () =>
        theme.global.current.value?.colors?.surface ||
        THEME_CONFIG.colors.light.surface,
);

const displayBreadcrumbs = computed(() => {
    if (props.breadcrumbs !== null) {
        return props.breadcrumbs;
    }
    return autoBreadcrumbs.value;
});

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
        :elevation="props.headerElevation"
        :height="props.headerHeight"
        app
    >
        <!-- アプリタイトル -->
        <div class="d-none d-md-flex align-center flex-shrink-1 ml-4">
            <span class="text-h6 font-weight-bold text-truncate">
                {{ props.appTitle }}
            </span>
        </div>

        <!-- パンくずリスト -->
        <div
            v-if="displayBreadcrumbs && displayBreadcrumbs.length > 0"
            class="flex-grow-1 d-flex justify-center"
        >
            <v-breadcrumbs
                :items="displayBreadcrumbs"
                class="pa-0 d-none d-sm-inline"
                density="compact"
            >
                <template v-slot:divider>
                    <v-icon :size="ICON_SIZES.sm" class="breadcrumb-divider">{{
                        ICONS.nav.divider
                    }}</v-icon>
                </template>

                <template v-slot:item="{ item }">
                    <v-breadcrumbs-item
                        :to="item.to"
                        :disabled="item.disabled"
                        class="text-caption text-sm-subtitle-2"
                        :class="{
                            'breadcrumb-link': !item.disabled,
                            'breadcrumb-current': item.disabled,
                        }"
                    >
                        {{ item.title }}
                    </v-breadcrumbs-item>
                </template>
            </v-breadcrumbs>
        </div>

        <v-spacer v-else></v-spacer>

        <div class="d-flex align-center ga-5 mr-4" style="flex-shrink: 0">
            <v-btn
                v-for="(button, index) in props.pageButtons"
                :key="index"
                variant="outlined"
                :color="getButtonColor(button.type)"
                :prepend-icon="button.icon"
                :loading="button.loading"
                @click="button.action"
            >
                {{ button.name }}
            </v-btn>
        </div>
    </v-app-bar>
</template>

<style scoped>
.breadcrumb-link {
    color: #0d6efd !important;
    text-decoration: underline !important;
    cursor: pointer !important;
    transition: color 0.15s ease-in-out;
}

.breadcrumb-link:hover {
    color: #0a58ca !important;
    text-decoration: underline !important;
}

.breadcrumb-link:active {
    color: #084298 !important;
}

.breadcrumb-current {
    color: rgba(var(--v-theme-on-surface), 0.87) !important;
    text-decoration: none !important;
    cursor: default !important;
}

.breadcrumb-divider {
    vertical-align: middle !important;
    margin-top: -3px !important;
}
</style>
