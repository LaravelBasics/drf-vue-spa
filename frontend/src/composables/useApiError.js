// src/composables/useApiError.js

import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';

export function useApiError() {
    const notification = useNotificationStore();
    const { t } = useI18n();

    /**
     * APIエラーを処理し、適切な通知を表示
     *
     * エラーメッセージの優先順位:
     * 1. detail（Djangoが翻訳済み）
     * 2. フィールド別エラー（employee_id, usernameなど）
     * 3. error_codeから翻訳（フォールバック）
     * 4. fallbackMessageKey（指定された場合）
     * 5. 汎用エラーメッセージ
     */
    function handleApiError(error, fallbackMessageKey = null, duration = 7000) {
        let errorMessage = null;

        if (error.response?.data) {
            const errorData = error.response.data;

            // 優先順位1: Djangoが翻訳済みのdetail
            if (errorData.detail) {
                errorMessage = errorData.detail;
            }

            // 優先順位2: フィールド別のバリデーションエラー
            if (!errorMessage) {
                errorMessage = extractFirstFieldError(errorData);
            }

            // 優先順位3: error_codeをフロントで翻訳（フォールバック）
            if (!errorMessage && errorData.error_code) {
                const backendErrorKey = `backend.errors.${errorData.error_code}`;
                const translated = t(backendErrorKey);
                if (translated !== backendErrorKey) {
                    errorMessage = translated;
                }
            }
        } else if (error.request) {
            // ネットワークエラー（サーバー到達不可）
            errorMessage = t('backend.errors.NETWORK_ERROR');
        } else {
            // 予期しないエラー（リクエスト設定ミスなど）
            errorMessage = t('backend.errors.UNKNOWN_ERROR');
        }

        // 最終フォールバック
        if (!errorMessage && fallbackMessageKey) {
            errorMessage = t(fallbackMessageKey);
        }

        if (!errorMessage) {
            errorMessage = t('backend.errors.UNKNOWN_ERROR');
        }

        notification.error(errorMessage, duration);

        return errorMessage;
    }

    /**
     * エラーオブジェクトから最初のフィールドエラーを抽出
     * 優先的に処理するフィールド: employee_id, username, email, password
     */
    function extractFirstFieldError(errorData) {
        const fieldErrors = ['employee_id', 'username', 'email', 'password'];

        // 優先フィールドから順に探索
        for (const field of fieldErrors) {
            if (errorData[field]) {
                const message = Array.isArray(errorData[field])
                    ? errorData[field][0]
                    : errorData[field];

                return message;
            }
        }

        // 優先フィールド以外のエラーを探索
        for (const [key, value] of Object.entries(errorData)) {
            if (Array.isArray(value) && value.length > 0) {
                return value[0];
            } else if (typeof value === 'string') {
                return value;
            }
        }

        return null;
    }

    function showSuccess(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showWarning(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.warning(message, duration);
    }

    function showInfo(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.info(message, duration);
    }

    return {
        handleApiError,
        showSuccess,
        showWarning,
        showInfo,
    };
}
