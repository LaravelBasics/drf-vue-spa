import { useI18n } from 'vue-i18n';
import { createValidationRules } from '@/utils/validation';

export function useValidation() {
    const { t } = useI18n();
    const rules = createValidationRules();

    // よく使われる組み合わせを定義
    const createRules = {
        // ログイン用ユーザー名（employeeIdに名前を変更）
        loginUseremployeeId() {
            // ★★★ 関数名を一致させる ★★★
            return [
                rules.required('employeeId'), // 'username' も 'employeeId' に変更
                rules.maxLength('employeeId', 10),
            ];
        },

        // ログイン用パスワード
        loginPassword() {
            return [
                rules.required('password'),
                rules.maxLength('password', 13),
            ];
        },

        // 一般的なユーザー名
        username() {
            return [
                rules.required('username'),
                rules.minLength('username', 3),
                rules.maxLength('username', 20),
                rules.alphaNumeric(),
            ];
        },

        // 新規登録用パスワード
        newPassword() {
            return [
                rules.required('password'),
                rules.minLength('password', 8),
                rules.maxLength('password', 128),
                rules.custom(
                    (value) => /(?=.*[a-zA-Z])(?=.*\d)/.test(value),
                    'form.validation.passwordStrength',
                ),
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
        t, // 翻訳関数も提供
    };
}
