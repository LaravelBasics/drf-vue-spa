// src/utils/validation.js - 改善版（正規表現を関数化）

import { useI18n } from 'vue-i18n';

// ⭐ 正規表現パターンを定数化
const PATTERNS = {
    EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    ALPHA_NUMERIC: /^[a-zA-Z0-9]+$/,
    EMPLOYEE_ID: /^\d{1,50}$/, // ⭐ 追加
    PASSWORD_STRENGTH: /(?=.*[a-zA-Z])(?=.*\d)/, // ⭐ 追加
};

// i18n対応バリデーションルール
export const createValidationRules = () => {
    const { t } = useI18n();

    return {
        // 必須チェック
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

        // 最大文字数
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

        // 最小文字数
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

        // メールアドレス
        email() {
            return (value) => {
                if (!value) return true;
                return PATTERNS.EMAIL.test(value) || t('form.validation.email');
            };
        },

        // 英数字のみ
        alphaNumeric() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.ALPHA_NUMERIC.test(value) ||
                    t('form.validation.alphaNumeric')
                );
            };
        },

        // ⭐ 社員番号（半角数字、○桁以内）
        employeeId() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.EMPLOYEE_ID.test(value) ||
                    t('form.validation.employeeIdFormat')
                );
            };
        },

        // ⭐ パスワード強度（英字+数字）
        passwordStrength() {
            return (value) => {
                if (!value) return true;
                return (
                    PATTERNS.PASSWORD_STRENGTH.test(value) ||
                    t('form.validation.passwordStrength')
                );
            };
        },

        // カスタムパターン
        pattern(regex, messageKey, params = {}) {
            return (value) => {
                if (!value) return true;
                return regex.test(value) || t(messageKey, params);
            };
        },

        // カスタム関数
        custom(validatorFn, messageKey, params = {}) {
            return (value) => {
                return validatorFn(value) || t(messageKey, params);
            };
        },
    };
};
