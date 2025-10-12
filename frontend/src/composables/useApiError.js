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

            if (errorData.detail) {
                errorMessage = errorData.detail;
            } else if (errorData.error) {
                errorMessage = errorData.error;
            } else {
                const firstFieldError = extractFirstFieldError(errorData);
                if (firstFieldError) {
                    errorMessage = firstFieldError;
                }
            }

            if (!errorMessage && errorData.non_field_errors) {
                errorMessage = Array.isArray(errorData.non_field_errors)
                    ? errorData.non_field_errors[0]
                    : errorData.non_field_errors;
            }
        } else if (error.request) {
            // ⭐ ネットワークエラーメッセージをi18nから取得
            errorMessage = t('notifications.error.network');
        } else {
            // ⭐ 予期しないエラーメッセージをi18nから取得
            errorMessage = t('notifications.error.unknown');
        }

        if (!errorMessage && fallbackMessageKey) {
            errorMessage = t(fallbackMessageKey);
        }

        if (!errorMessage) {
            errorMessage = t('notifications.error.unknown');
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

    // ✅ 推奨: 目的別の関数
    function showLoginSuccess(messageKey, params = {}, duration = 3000) {
        // ログイン成功は「情報」（青）で表示
        const message = t(messageKey, params);
        notification.info(message, duration);
    }

    function showCreateSuccess(messageKey, params = {}, duration = 5000) {
        // 作成成功は「成功」（緑）で表示
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showUpdateSuccess(messageKey, params = {}, duration = 5000) {
        // 更新成功は「成功」（緑）で表示
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showDeleteSuccess(messageKey, params = {}, duration = 5000) {
        // 削除成功は「成功」（緑）で表示
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showWarning(messageKey, params = {}, duration = 6000) {
        const message = t(messageKey, params);
        notification.warning(message, duration);
    }

    function showInfo(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.info(message, duration);
    }

    return {
        handleApiError,
        showLoginSuccess,
        showCreateSuccess,
        showUpdateSuccess,
        showDeleteSuccess,
        showWarning,
        showInfo,
    };
}
