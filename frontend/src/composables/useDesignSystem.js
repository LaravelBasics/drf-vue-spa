// src/composables/useDesignSystem.js - 修正版（防御的コーディング）

import { computed } from 'vue';
import { useTheme } from 'vuetify';
import {
    COLORS,
    ICON_SIZES,
    SPACING,
    THEME_CONFIG,
    COMPONENT_CONFIGS,
} from '@/constants/theme';
import { ICONS } from '@/constants/icons';

export function useDesignSystem() {
    const theme = useTheme();

    // テーマ切り替え
    const toggleTheme = () => {
        theme.global.name.value = theme.global.current.value.dark
            ? 'light'
            : 'dark';
    };

    // 現在のテーマ色を取得（防御的コーディング）
    const colors = computed(() => {
        // Vuetifyテーマが初期化されていない場合のフォールバック
        const currentColors = theme.global.current.value?.colors || {};

        return {
            ...COLORS,
            current: {
                // デフォルト値を設定して undefined エラーを防ぐ
                primary: currentColors.primary || COLORS.brand.primary,
                secondary: currentColors.secondary || COLORS.brand.secondary,
                accent: currentColors.accent || COLORS.brand.accent,
                success: currentColors.success || COLORS.status.success,
                error: currentColors.error || COLORS.status.error,
                warning: currentColors.warning || COLORS.status.warning,
                info: currentColors.info || COLORS.status.info,
                background:
                    currentColors.background || COLORS.background.default,
                surface: currentColors.surface || COLORS.background.surface,
                // 他の色もフォールバック
                ...currentColors,
            },
        };
    });

    // アイコンヘルパー
    const getIcon = (category, name) => {
        return ICONS[category]?.[name] || 'mdi-help-circle';
    };

    // サイズヘルパー
    const getSize = (size) => {
        return ICON_SIZES[size] || ICON_SIZES.md;
    };

    // スペーシングヘルパー
    const getSpacing = (size) => {
        return SPACING[size] || SPACING.md;
    };

    // コンポーネント設定ヘルパー（防御的コーディング）
    const getComponentConfig = (component, property = null) => {
        const config = COMPONENT_CONFIGS[component];
        if (!config) {
            console.warn(`Component config not found: ${component}`);
            return property ? undefined : {};
        }
        return property ? config[property] : config;
    };

    return {
        // テーマ
        theme: theme.global,
        colors,
        toggleTheme,

        // アイコン・サイズ
        getIcon,
        getSize,
        getSpacing,
        getComponentConfig,

        // 定数への直接アクセス
        COLORS,
        ICONS,
        ICON_SIZES,
        SPACING,
        THEME_CONFIG,
        COMPONENT_CONFIGS,
    };
}
