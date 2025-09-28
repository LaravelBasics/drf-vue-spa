// src/constants/theme.js - テーマ・デザイン統一管理

export const COLORS = Object.freeze({
    // ブランドカラー
    brand: {
        primary: '#1976D2', // メインブルー
        secondary: '#424242', // グレー
        accent: '#FF5722', // アクセントオレンジ
    },

    // 状態カラー
    status: {
        success: '#4CAF50', // 成功・完了・OK
        error: '#F44336', // 失敗・危険・停止
        warning: '#FF9800', // 注意・警告・確認
        info: '#2196F3', // 情報・ヒント・通知
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

// スペーシング統一
export const SPACING = Object.freeze({
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
});

// エレベーション（影）統一
export const ELEVATION = Object.freeze({
    none: 0,
    subtle: 1,
    low: 2,
    medium: 4,
    high: 8,
    highest: 12,
});

// ボーダーRadius統一
export const BORDER_RADIUS = Object.freeze({
    none: 0,
    sm: 4,
    md: 8,
    lg: 12,
    xl: 16,
    round: 50,
});

// ⭐ COMPONENT_CONFIGS を追加
export const COMPONENT_CONFIGS = Object.freeze({
    // ヘッダー設定
    header: {
        height: {
            mobile: 56,
            tablet: 64,
            desktop: 64,
        },
        elevation: ELEVATION.low,
    },

    // カード設定
    card: {
        padding: {
            sm: SPACING.md,
            md: SPACING.lg,
            lg: SPACING.xl,
        },
        elevation: ELEVATION.subtle,
        borderRadius: BORDER_RADIUS.lg,
    },

    // ボタン設定
    button: {
        size: {
            small: { height: 32, fontSize: '0.875rem' },
            default: { height: 40, fontSize: '1rem' },
            large: { height: 48, fontSize: '1.125rem' },
        },
        padding: {
            sm: `${SPACING.xs}px ${SPACING.sm}px`,
            md: `${SPACING.sm}px ${SPACING.md}px`,
            lg: `${SPACING.md}px ${SPACING.lg}px`,
        },
    },

    // フォーム設定
    form: {
        spacing: SPACING.md,
        fieldHeight: 48,
        labelFontSize: '0.875rem',
    },

    // モーダル・ダイアログ設定
    modal: {
        width: {
            sm: 400,
            md: 600,
            lg: 800,
            xl: 1000,
        },
        maxWidth: '90vw',
        elevation: ELEVATION.high,
    },
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
    defaults: {
        VBtn: {
            elevation: ELEVATION.low,
            rounded: BORDER_RADIUS.md,
        },
        VAppBarNavIcon: {
            // 影（浮き上がり）をなくすために elevation を無効化
            elevation: ELEVATION.none,
            // variantをtextにして、背景色をつけないようにする (念のため)
            variant: 'text',
        },
        VCard: {
            elevation: ELEVATION.subtle,
            rounded: BORDER_RADIUS.lg,
        },
        VTextField: {
            variant: 'outlined',
            density: 'default',
        },
    },
};
