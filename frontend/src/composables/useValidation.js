// =====================================
// src/composables/useValidation.js
// =====================================

import { validationRules } from '@/utils/validation';

export function useValidation() {
    // よく使われる組み合わせを定義
    const createRules = {
        // ログイン用ユーザー名
        loginUsername() {
            return [
                validationRules.required('username'),
                validationRules.maxLength('username', 10),
            ];
        },

        // ログイン用パスワード
        loginPassword() {
            return [
                validationRules.required('password'),
                validationRules.maxLength('password', 13),
            ];
        },

        // 一般的なユーザー名（より厳しい）
        username() {
            return [
                validationRules.required('username'),
                validationRules.minLength('username', 3),
                validationRules.maxLength('username', 20),
                validationRules.alphaNumeric('username'),
            ];
        },

        // 新規登録用パスワード
        newPassword() {
            return [
                validationRules.required('password'),
                validationRules.minLength('password', 8),
                validationRules.maxLength('password', 128),
                validationRules.custom(
                    (value) => /(?=.*[a-zA-Z])(?=.*\d)/.test(value),
                    'パスワードは英字と数字を含む必要があります',
                ),
            ];
        },

        // メールアドレス
        email() {
            return [
                validationRules.required('email'),
                validationRules.email(),
                validationRules.maxLength('email', 100),
            ];
        },

        // 名前
        name() {
            return [
                validationRules.required('name'),
                validationRules.maxLength('name', 50),
            ];
        },
    };

    return {
        rules: validationRules,
        createRules,
    };
}
