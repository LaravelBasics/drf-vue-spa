// src/composables/useApiError.js

import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';

export function useApiError() {
    const notification = useNotificationStore();
    const { t } = useI18n();

    function handleApiError(error, fallbackMessageKey = null, duration = 7000) {
        console.error('API Error:', error);

        let errorMessage = null;

        if (error.response?.data) {
            const errorData = error.response.data;

            // ⭐ 優先順位1: error_code があれば backend.errors から翻訳
            if (errorData.error_code) {
                const backendErrorKey = `backend.errors.${errorData.error_code}`;
                if (t(backendErrorKey) !== backendErrorKey) {
                    errorMessage = t(backendErrorKey);
                }
            }

            // ⭐ 優先順位2: 翻訳がなければ detail をそのまま使用
            if (!errorMessage && errorData.detail) {
                errorMessage = errorData.detail;
            }

            // ⭐ 優先順位3: フィールド別エラーを抽出
            if (!errorMessage) {
                errorMessage = extractFirstFieldError(errorData);
            }

            // ⭐ 優先順位4: non_field_errors
            if (!errorMessage && errorData.non_field_errors) {
                errorMessage = Array.isArray(errorData.non_field_errors)
                    ? errorData.non_field_errors[0]
                    : errorData.non_field_errors;
            }
        } else if (error.request) {
            // ネットワークエラー
            errorMessage = t('backend.errors.NETWORK_ERROR');
        } else {
            // 予期しないエラー
            errorMessage = t('backend.errors.UNKNOWN_ERROR');
        }

        // ⭐ 最終的なフォールバック
        if (!errorMessage && fallbackMessageKey) {
            errorMessage = t(fallbackMessageKey);
        }

        if (!errorMessage) {
            errorMessage = t('backend.errors.UNKNOWN_ERROR');
        }

        notification.error(errorMessage, duration);

        return errorMessage;
    }

    function extractFirstFieldError(errorData) {
        const fieldErrors = [
            'employee_id',
            'username',
            'email',
            'password',
            'name',
            'phone',
        ];

        for (const field of fieldErrors) {
            if (errorData[field]) {
                const message = Array.isArray(errorData[field])
                    ? errorData[field][0]
                    : errorData[field];

                return message;
            }
        }

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
