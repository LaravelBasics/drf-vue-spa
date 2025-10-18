// src/composables/useValidation.js - 改善版（重複削除）

import { useI18n } from 'vue-i18n';
import { createValidationRules } from '@/utils/validation';

export function useValidation() {
    const { t } = useI18n();
    const rules = createValidationRules();

    // よく使われる組み合わせを定義
    const createRules = {
        // ログイン用社員番号
        loginEmployeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(), // ⭐ utils から使用
            ];
        },

        // ログイン用パスワード
        loginPassword() {
            return [
                rules.required('password'),
                rules.maxLength('password', 13),
            ];
        },

        // ユーザー管理用ユーザー名
        username() {
            return [
                rules.required('username'),
                rules.minLength('username', 3),
                rules.maxLength('username', 20),
            ];
        },

        // ユーザー管理用社員番号
        employeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(), // ⭐ utils から使用
            ];
        },

        // 新規登録用パスワード
        newPassword() {
            return [
                rules.required('password'),
                rules.minLength('password', 8),
                rules.maxLength('password', 128),
                rules.passwordStrength(), // ⭐ utils から使用
            ];
        },

        // パスワード確認用
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
                rules.maxLength('email', 100),
            ];
        },
    };

    return {
        rules,
        createRules,
        t,
    };
}
