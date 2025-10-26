<!-- src/components/Header.vue - パンくずリスト対応（リンク強調版） -->
<script setup>
import { computed } from 'vue';
import { useTheme } from 'vuetify';
import { useBreadcrumbs } from '@/composables/useBreadcrumbs';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES, THEME_CONFIG, COMPONENT_CONFIGS } from '@/constants/theme';

const theme = useTheme();
const { breadcrumbs: autoBreadcrumbs } = useBreadcrumbs(); // 自動生成

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
        default: null, // null にすることで「未指定」を判定可能に
    },
});

const surfaceColor = computed(
    () =>
        theme.global.current.value?.colors?.surface ||
        THEME_CONFIG.colors.light.surface,
);

const elevation = computed(() => COMPONENT_CONFIGS.header?.elevation || 4);

const headerHeight = computed(
    () => COMPONENT_CONFIGS.header.height.desktop || 64,
);

// 🎯 重要！propsが渡されてなければ自動生成を使う
const displayBreadcrumbs = computed(() => {
    // props.breadcrumbs が明示的に渡された場合はそれを使う
    if (props.breadcrumbs !== null) {
        return props.breadcrumbs;
    }
    // 渡されてない場合は自動生成を使う
    return autoBreadcrumbs.value;
});

// ボタンの色を動的に取得（デフォルトはprimary）
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
        <!-- アプリタイトル（PC以上で表示） -->
        <div
            class="ml-5 d-none d-sm-inline align-center"
            style="min-width: 0; flex-shrink: 1"
        >
            <span class="text-h6 font-weight-bold text-truncate">
                {{ props.appTitle }}
            </span>
        </div>

        <!-- パンくずリスト（displayBreadcrumbsが存在する場合のみ表示） -->
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
                    <v-icon :size="ICON_SIZES.sm">{{
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

        <!-- ページ固有のアクションボタン群 -->
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

<style scoped>
/* クリック可能なパンくずリンク（モダンなBootstrapスタイル） */
.breadcrumb-link {
    color: #0d6efd !important; /* Bootstrap 5のリンク色（明るい青） */
    text-decoration: underline !important;
    cursor: pointer !important;
    transition: color 0.15s ease-in-out;
}

.breadcrumb-link:hover {
    color: #0a58ca !important; /* ホバー時の濃い青 */
    text-decoration: underline !important;
}

.breadcrumb-link:active {
    color: #084298 !important; /* クリック時のさらに濃い青 */
}

/* 現在のページ（クリック不可） */
.breadcrumb-current {
    color: rgba(var(--v-theme-on-surface), 0.87) !important;
    text-decoration: none !important;
    cursor: default !important;
}
</style>
