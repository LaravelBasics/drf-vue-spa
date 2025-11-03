// src/constants/theme.js - テーマ・デザイン統一管理

// カラーパレット定義
export const COLORS = Object.freeze({
    // ブランドカラー
    brand: {
        primary: '#1976D2',
        secondary: '#424242',
        accent: '#FF5722',
    },

    // 状態カラー
    status: {
        success: '#4CAF50', // 成功・完了
        error: '#F44336', // 失敗・危険
        warning: '#FF9800', // 注意・警告
        info: '#2196F3', // 情報・通知
    },

    // グレースケール
    neutral: {
        white: '#FFFFFF',
        light: '#F5F5F5',
        medium: '#9E9E9E',
        dark: '#424242',
        black: '#212121',
    },

    // 背景色
    background: {
        default: '#FAFAFA',
        surface: '#FFFFFF',
        card: '#FFFFFF',
    },
});

// アイコンサイズ統一
export const ICON_SIZES = Object.freeze({
    xs: 16,
    sm: 20,
    md: 24,
    lg: 32,
    xl: 40,
});

// Vuetifyテーマ設定
export const THEME_CONFIG = {
    colors: {
        light: {
            primary: COLORS.brand.primary,
            secondary: COLORS.brand.secondary,
            accent: COLORS.brand.accent,
            success: COLORS.status.success,
            error: COLORS.status.error,
            warning: COLORS.status.warning,
            info: COLORS.status.info,
            background: COLORS.background.default,
            surface: COLORS.background.surface,
        },
        dark: {
            primary: '#90CAF9',
            secondary: '#616161',
            accent: '#FF7043',
            success: '#81C784',
            error: '#E57373',
            warning: '#FFB74D',
            info: '#64B5F6',
            background: '#121212',
            surface: '#1E1E1E',
        },
    },
};
