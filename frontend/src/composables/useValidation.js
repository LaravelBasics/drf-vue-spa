// src/composables/useValidation.js - フォームバリデーション

import { useI18n } from 'vue-i18n';
import { createValidationRules } from '@/utils/validation';

export function useValidation() {
    const { t } = useI18n();
    const rules = createValidationRules();

    // よく使われるバリデーションルールの組み合わせ
    const createRules = {
        // ログイン用社員番号（既存ユーザー向け）
        loginEmployeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(),
                rules.maxLength('employeeId', 50),
            ];
        },

        // ログイン用パスワード（強度チェックなし）
        loginPassword() {
            return [
                rules.required('password'),
                rules.maxLength('password', 128),
            ];
        },

        // ユーザー管理用ユーザー名
        username() {
            return [
                rules.required('username'),
                rules.minLength('username', 3),
                rules.maxLength('username', 50),
            ];
        },

        // ユーザー管理用社員番号
        employeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(),
                rules.maxLength('employeeId', 50),
            ];
        },

        // 新規登録用パスワード（強度チェックあり）
        newPassword() {
            return [
                rules.required('password'),
                rules.minLength('password', 8),
                rules.maxLength('password', 128),
                rules.passwordStrength(), // 英字+数字の組み合わせ必須
            ];
        },

        // パスワード確認用（元のパスワードと一致チェック）
        passwordConfirm(originalPassword) {
            return [
                rules.required('password'),
                (value) =>
                    value === originalPassword ||
                    t('form.validation.passwordMismatch'),
            ];
        },

        // メールアドレス
        email() {
            return [
                rules.required('email'),
                rules.email(),
                rules.maxLength('email', 255),
            ];
        },
    };

    return {
        rules,
        createRules,
        t,
    };
}
