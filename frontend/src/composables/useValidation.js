// src/composables/useValidation.js
// バリデーションルールの組み合わせを提供するComposable

import { useI18n } from 'vue-i18n';
import { createValidationRules } from '@/utils/validation';

/**
 * よく使われるバリデーションルールの組み合わせを提供
 * 各画面で個別にルールを組み立てる手間を省き、統一したバリデーションを実現
 */
export function useValidation() {
    const { t } = useI18n();
    const rules = createValidationRules();

    const createRules = {
        /**
         * ログイン画面用の社員番号バリデーション
         * - 必須チェック
         * - フォーマットチェック（数値のみ）
         * - 最大長チェック
         */
        loginEmployeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(),
                rules.maxLength('employeeId', 50),
            ];
        },

        /**
         * ログイン画面用のパスワードバリデーション
         * - 必須チェック
         * - 最大長チェック
         * ※ログイン時は強度チェックなし
         */
        loginPassword() {
            return [
                rules.required('password'),
                rules.maxLength('password', 128),
            ];
        },

        /**
         * ユーザー管理用のユーザー名バリデーション
         * - 必須チェック
         * - 最小3文字
         * - 最大50文字
         */
        username() {
            return [
                rules.required('username'),
                rules.minLength('username', 3),
                rules.maxLength('username', 50),
            ];
        },

        /**
         * ユーザー管理用の社員番号バリデーション
         * - 必須チェック
         * - フォーマットチェック（数値のみ）
         * - 最大長チェック
         */
        employeeId() {
            return [
                rules.required('employeeId'),
                rules.employeeId(),
                rules.maxLength('employeeId', 50),
            ];
        },

        /**
         * 新規登録・パスワード変更用のパスワードバリデーション
         * - 必須チェック
         * - 最小8文字
         * - 最大128文字
         * - 強度チェック（英字+数字の組み合わせ必須）
         */
        newPassword() {
            return [
                rules.required('password'),
                rules.minLength('password', 8),
                rules.maxLength('password', 128),
                rules.passwordStrength(),
            ];
        },

        /**
         * パスワード確認入力用のバリデーション
         * - 必須チェック
         * - 元のパスワードとの一致チェック
         * @param {string} originalPassword - 比較元のパスワード
         */
        passwordConfirm(originalPassword) {
            return [
                rules.required('password'),
                (value) =>
                    value === originalPassword ||
                    t('form.validation.passwordMismatch'),
            ];
        },

        /**
         * メールアドレス用のバリデーション
         * - 必須チェック
         * - メールフォーマットチェック
         * - 最大255文字
         */
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
