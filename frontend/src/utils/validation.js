// src/utils/validation.js - バリデーションルール定義

import { useI18n } from 'vue-i18n';

// 正規表現パターンの定義
const PATTERNS = {
    EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    ALPHA_NUMERIC: /^[a-zA-Z0-9]+$/,
    EMPLOYEE_ID: /^\d{1,50}$/,
    PASSWORD_STRENGTH: /(?=.*[a-zA-Z])(?=.*\d)/, // 英字+数字の組み合わせ
};

// i18n対応のバリデーションルール作成
export const createValidationRules = () => {
    const { t } = useI18n();

    return {
        // 必須入力チェック
        required(fieldKey) {
            return (value) => {
                return (
                    !!value ||
                    t('form.validation.required', {
                        field: t(`form.fields.${fieldKey}`),
                    })
                );
            };
        },

        // 最大文字数チェック
        maxLength(fieldKey, max) {
            return (value) => {
                if (!value) return true;
                return (
                    value.length <= max ||
                    t('form.validation.maxLength', {
                        field: t(`form.fields.${fieldKey}`),
                        max: max,
                    })
                );
            };
        },

        // 最小文字数チェック
        minLength(fieldKey, min) {
            return (value) => {
                if (!value) return true;
                return (
                    value.length >= min ||
                    t('form.validation.minLength', {
                        field: t(`form.fields.${fieldKey}`),
                        min: min,
                    })
                );
            };
        },

        // メールアドレス形式チェック
        email() {
            return (value) => {
                if (!value) return true;
                return PATTERNS.EMAIL.test(value) || t('form.validation.email');
            };
        },

        // 英数字のみチェック
        alphaNumeric() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.ALPHA_NUMERIC.test(value) ||
                    t('form.validation.alphaNumeric')
                );
            };
        },

        // 社員番号形式チェック（半角数字のみ、50桁以内）
        employeeId() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.EMPLOYEE_ID.test(value) ||
                    t('form.validation.employeeIdFormat')
                );
            };
        },

        // パスワード強度チェック（英字+数字の組み合わせ必須）
        passwordStrength() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.PASSWORD_STRENGTH.test(value) ||
                    t('form.validation.passwordStrength')
                );
            };
        },

        // カスタム正規表現パターン
        pattern(regex, messageKey, params = {}) {
            return (value) => {
                if (!value) return true;
                return regex.test(value) || t(messageKey, params);
            };
        },

        // カスタムバリデーション関数
        custom(validatorFn, messageKey, params = {}) {
            return (value) => {
                return validatorFn(value) || t(messageKey, params);
            };
        },
    };
};
