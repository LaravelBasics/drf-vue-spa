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

            // ⭐ 1. エラーコードを優先的にチェック
            if (errorData.error_code) {
                // まず、ページ固有のエラーコードを探す（例: pages.users.create.errors.EMPLOYEE_ID_EXISTS）
                if (fallbackMessageKey) {
                    const pageErrorKey = `${fallbackMessageKey.replace('.error', '.errors')}.${errorData.error_code}`;
                    if (t(pageErrorKey) !== pageErrorKey) {
                        errorMessage = t(pageErrorKey);
                    }
                }

                // なければ、共通エラーコードを探す（例: notifications.error.NOT_FOUND）
                if (!errorMessage) {
                    const commonErrorKey = `notifications.error.${errorData.error_code}`;
                    if (t(commonErrorKey) !== commonErrorKey) {
                        errorMessage = t(commonErrorKey);
                    }
                }

                // 認証エラーの場合は auth.errors も確認
                if (!errorMessage) {
                    const authErrorKey = `auth.errors.${errorData.error_code}`;
                    if (t(authErrorKey) !== authErrorKey) {
                        errorMessage = t(authErrorKey);
                    }
                }
            }

            // ⭐ 2. error_code がない、または翻訳が見つからない場合は detail を使用
            if (!errorMessage && errorData.detail) {
                errorMessage = errorData.detail;
            } else if (!errorMessage && errorData.error) {
                errorMessage = errorData.error;
            } else if (!errorMessage) {
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
            errorMessage = t('notifications.error.network');
        } else {
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

    function showLoginSuccess(messageKey, params = {}, duration = 3000) {
        const message = t(messageKey, params);
        notification.info(message, duration);
    }

    function showCreateSuccess(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showUpdateSuccess(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    function showDeleteSuccess(messageKey, params = {}, duration = 5000) {
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
