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
</script>

<template>
    <v-app-bar
        :color="surfaceColor"
        :elevation="headerElevation"
        :height="headerHeight"
    >
        <!-- アプリタイトル -->
        <div class="d-flex align-center flex-shrink-1 ml-4">
            <span class="text-h6 font-weight-bold text-truncate">
                {{ appTitle }}
            </span>
        </div>

        <!-- パンくずリスト -->
        <div
            v-if="displayBreadcrumbs && displayBreadcrumbs.length > 0"
            class="flex-grow-1 d-flex justify-center"
        >
            <v-breadcrumbs
                :items="displayBreadcrumbs"
                class="pa-0"
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
                    >
                        {{ item.title }}
                    </v-breadcrumbs-item>
                </template>
            </v-breadcrumbs>
        </div>

        <v-spacer v-else />

        <div class="d-flex align-center ga-4 mr-4 flex-shrink-0">
            <v-btn
                v-for="(button, index) in pageButtons"
                :key="button.id || `btn-${index}`"
                variant="outlined"
                :color="button.type || 'primary'"
                :prepend-icon="button.icon"
                :loading="button.loading"
                :disabled="button.disabled"
                @click="button.action"
            >
                {{ button.name }}
            </v-btn>
        </div>
    </v-app-bar>
</template>

<style scoped>
/* パンくずリンクのスタイル */
:deep(.v-breadcrumbs-item--link) {
    color: rgb(var(--v-theme-primary));
    transition: opacity 0.2s ease;
}

:deep(.v-breadcrumbs-item--link:hover) {
    opacity: 0.7;
}

:deep(.v-breadcrumbs-item[disabled]) {
    color: rgba(var(--v-theme-on-surface), 0.6);
    pointer-events: none;
}

.breadcrumb-divider {
    vertical-align: middle;
    margin-top: -2px;
}
</style>
