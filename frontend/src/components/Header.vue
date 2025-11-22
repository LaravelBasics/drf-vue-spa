<!-- src/components/Header.vue -->
<script setup>
import { computed } from 'vue';
import { useBreadcrumbs } from '@/composables/useBreadcrumbs';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES } from '@/constants/theme';

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
        validator: (buttons) => {
            // 全てのボタンにidとtypeが必須
            const isValid = buttons.every((btn) => {
                const hasId = btn.id && typeof btn.id === 'string';
                const hasValidType =
                    btn.type &&
                    [
                        'primary',
                        'secondary',
                        'error',
                        'warning',
                        'info',
                        'success',
                    ].includes(btn.type);

                // 開発環境で詳細エラー出力
                if (import.meta.env.DEV) {
                    if (!hasId) {
                        console.error(
                            '[Header] Button missing required "id" field:',
                            btn,
                        );
                    }
                    if (!hasValidType) {
                        console.error(
                            '[Header] Button missing or invalid "type" field:',
                            btn,
                        );
                    }
                }

                return hasId && hasValidType;
            });

            return isValid;
        },
    },
    breadcrumbs: {
        type: Array,
        default: null,
    },
});

// computedが必要なもの: 条件分岐ロジックあり
const displayBreadcrumbs = computed(() => {
    if (props.breadcrumbs !== null) {
        return props.breadcrumbs;
    }
    return autoBreadcrumbs.value;
});
</script>

<template>
    <v-app-bar
        color="surface"
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
                <template #divider>
                    <v-icon :size="ICON_SIZES.sm" class="breadcrumb-divider">{{
                        ICONS.nav.divider
                    }}</v-icon>
                </template>

                <template #item="{ item }">
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

        <!-- ボタン群 -->
        <div class="d-flex align-center ga-4 mr-4 flex-shrink-0">
            <v-btn
                v-for="button in pageButtons"
                :key="button.id"
                variant="outlined"
                :color="button.type"
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
