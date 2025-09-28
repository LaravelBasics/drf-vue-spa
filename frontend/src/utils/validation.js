// =====================================
// src/utils/validation.js
// =====================================

import { messages } from '@/constants/messages';

// メッセージのプレースホルダーを置換するヘルパー関数
function formatMessage(template, params = {}) {
    return template.replace(/{(\w+)}/g, (match, key) => {
        return params[key] !== undefined ? params[key] : match;
    });
}

// 基本的なバリデーションルール
export const validationRules = {
    // 必須チェック
    required(fieldName) {
        return (value) => {
            return (
                !!value ||
                formatMessage(messages.required, {
                    name: messages.fields[fieldName] || fieldName,
                })
            );
        };
    },

    // 最大文字数
    maxLength(fieldName, max) {
        return (value) => {
            if (!value) return true; // 空の場合はスキップ（requiredと組み合わせて使用）
            return (
                value.length <= max ||
                formatMessage(messages.maxLength, {
                    name: messages.fields[fieldName] || fieldName,
                    max: max,
                })
            );
        };
    },

    // 最小文字数
    minLength(fieldName, min) {
        return (value) => {
            if (!value) return true;
            return (
                value.length >= min ||
                formatMessage(messages.minLength, {
                    name: messages.fields[fieldName] || fieldName,
                    min: min,
                })
            );
        };
    },

    // メールアドレス形式
    email(fieldName = 'email') {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return (value) => {
            if (!value) return true;
            return emailPattern.test(value) || messages.pattern.email;
        };
    },

    // 英数字のみ
    alphaNumeric(fieldName) {
        const pattern = /^[a-zA-Z0-9]+$/;
        return (value) => {
            if (!value) return true;
            return pattern.test(value) || messages.pattern.alphaNumeric;
        };
    },

    // カスタムパターン
    pattern(regex, message) {
        return (value) => {
            if (!value) return true;
            return regex.test(value) || message;
        };
    },

    // 値の範囲チェック
    range(fieldName, min, max) {
        return (value) => {
            if (!value) return true;
            const num = Number(value);
            if (isNaN(num)) return '数値を入力してください';
            return (
                (num >= min && num <= max) ||
                `${min}から${max}の間で入力してください`
            );
        };
    },

    // カスタム関数
    custom(validatorFn, message) {
        return (value) => {
            return validatorFn(value) || message;
        };
    },
};
