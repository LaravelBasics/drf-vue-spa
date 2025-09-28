// src/utils/validation.js - 更新版（i18n対応）

import { useI18n } from 'vue-i18n';

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
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return (value) => {
                if (!value) return true;
                return emailPattern.test(value) || t('form.validation.email');
            };
        },

        // 英数字のみ
        alphaNumeric() {
            const pattern = /^[a-zA-Z0-9]+$/;
            return (value) => {
                if (!value) return true;
                return pattern.test(value) || t('form.validation.alphaNumeric');
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
