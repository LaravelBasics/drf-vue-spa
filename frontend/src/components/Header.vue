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

const displayBreadcrumbs = computed(() => {
    if (props.breadcrumbs !== null) {
        return props.breadcrumbs;
    }
    return autoBreadcrumbs.value;
});
</script>

<template>
    <v-toolbar
        color="surface"
        :elevation="headerElevation"
        :height="headerHeight"
    >
        <!-- ✅ Grid Systemで明確な構造 -->
        <v-row no-gutters align="center">
            <!-- タイトル(xs:全幅、sm以上:3列) -->
            <v-col cols="12" sm="3">
                <v-toolbar-title class="text-truncate ml-2">
                    {{ appTitle }}
                </v-toolbar-title>
            </v-col>

            <!-- パンくずリスト(xs:全幅、sm以上:6列、中央配置) -->
            <v-col
                v-if="displayBreadcrumbs && displayBreadcrumbs.length > 0"
                cols="12"
                sm="6"
                class="d-flex justify-center"
            >
                <v-breadcrumbs
                    :items="displayBreadcrumbs"
                    class="pa-0"
                    density="compact"
                >
                    <template #divider>
                        <v-icon
                            :size="ICON_SIZES.sm"
                            class="breadcrumb-divider"
                        >
                            {{ ICONS.nav.divider }}
                        </v-icon>
                    </template>

                    <template #item="{ item }">
                        <v-breadcrumbs-item
                            :to="item.to"
                            :disabled="item.disabled"
                            class="text-caption"
                        >
                            {{ item.title }}
                        </v-breadcrumbs-item>
                    </template>
                </v-breadcrumbs>
            </v-col>

            <!-- パンくずリストない時の余白 -->
            <v-col v-else cols="0" sm="6"></v-col>

            <!-- ボタン群(xs:非表示、sm以上:3列、右寄せ) -->
            <v-col
                v-if="pageButtons.length > 0"
                cols="12"
                sm="3"
                class="d-none d-sm-flex justify-end"
            >
                <v-btn
                    v-for="button in pageButtons"
                    :key="button.id"
                    variant="outlined"
                    :color="button.type"
                    :prepend-icon="button.icon"
                    :loading="button.loading"
                    :disabled="button.disabled"
                    class="ml-2"
                    @click="button.action"
                >
                    {{ button.name }}
                </v-btn>
            </v-col>
        </v-row>
    </v-toolbar>
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
