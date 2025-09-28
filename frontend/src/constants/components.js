// src/constants/components.js - コンポーネント設定値

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
