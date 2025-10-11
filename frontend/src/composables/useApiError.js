// src/composables/useApiError.js

import { useNotificationStore } from '@/stores/notification';
import { useI18n } from 'vue-i18n';

/**
 * API エラーハンドリング用 Composable
 *
 * 使い方:
 * const { handleApiError } = useApiError();
 *
 * try {
 *   await usersAPI.create(data);
 * } catch (error) {
 *   handleApiError(error, 'pages.users.createError'); // フォールバックメッセージ
 * }
 */
export function useApiError() {
    const notification = useNotificationStore();
    const { t } = useI18n();

    /**
     * APIエラーを解析して通知を表示
     *
     * @param {Error} error - Axiosエラーオブジェクト
     * @param {string} fallbackMessageKey - フォールバック用のi18nキー（省略可）
     * @param {number} duration - 通知の表示時間（ミリ秒）
     * @returns {string|null} - 抽出されたエラーメッセージ（デバッグ用）
     */
    function handleApiError(error, fallbackMessageKey = null, duration = 7000) {
        console.error('API Error:', error);

        let errorMessage = null;

        // レスポンスがある場合（サーバーからのエラー）
        if (error.response?.data) {
            const errorData = error.response.data;

            // 1. detail フィールド（DRF標準）
            if (errorData.detail) {
                errorMessage = errorData.detail;
            }
            // 2. error フィールド（カスタム）
            else if (errorData.error) {
                errorMessage = errorData.error;
            }
            // 3. フィールド別エラー（Serializer Validation）
            else {
                // 最初のフィールドエラーを取得
                const firstFieldError = extractFirstFieldError(errorData);
                if (firstFieldError) {
                    errorMessage = firstFieldError;
                }
            }

            // 4. non_field_errors（フォーム全体のエラー）
            if (!errorMessage && errorData.non_field_errors) {
                errorMessage = Array.isArray(errorData.non_field_errors)
                    ? errorData.non_field_errors[0]
                    : errorData.non_field_errors;
            }
        }
        // ネットワークエラー
        else if (error.request) {
            errorMessage =
                'サーバーに接続できません。ネットワーク接続を確認してください。';
        }
        // その他のエラー
        else {
            errorMessage = error.message || '予期しないエラーが発生しました';
        }

        // フォールバックメッセージ
        if (!errorMessage && fallbackMessageKey) {
            errorMessage = t(fallbackMessageKey);
        }

        // 最終的なフォールバック
        if (!errorMessage) {
            errorMessage = 'エラーが発生しました';
        }

        // 通知を表示
        notification.error(errorMessage, duration);

        return errorMessage;
    }

    /**
     * フィールドエラーから最初のエラーメッセージを抽出
     *
     * @param {Object} errorData - エラーデータ
     * @returns {string|null} - エラーメッセージ
     */
    function extractFirstFieldError(errorData) {
        const fieldErrors = [
            'employee_id',
            'username',
            'email',
            'password',
            'name',
            'phone',
            // 他のフィールドも追加可能
        ];

        for (const field of fieldErrors) {
            if (errorData[field]) {
                const message = Array.isArray(errorData[field])
                    ? errorData[field][0]
                    : errorData[field];

                return message;
            }
        }

        // 定義されていないフィールドのエラーも取得
        for (const [key, value] of Object.entries(errorData)) {
            if (Array.isArray(value) && value.length > 0) {
                return value[0];
            } else if (typeof value === 'string') {
                return value;
            }
        }

        return null;
    }

    /**
     * 成功メッセージを表示（便利関数）
     *
     * @param {string} messageKey - i18nキー
     * @param {Object} params - i18nパラメータ
     * @param {number} duration - 表示時間
     */
    function showSuccess(messageKey, params = {}, duration = 5000) {
        const message = t(messageKey, params);
        notification.success(message, duration);
    }

    /**
     * 警告メッセージを表示（便利関数）
     *
     * @param {string} messageKey - i18nキー
     * @param {Object} params - i18nパラメータ
     * @param {number} duration - 表示時間
     */
    function showWarning(messageKey, params = {}, duration = 6000) {
        const message = t(messageKey, params);
        notification.warning(message, duration);
    }

    /**
     * 情報メッセージを表示（便利関数）
     *
     * @param {string} messageKey - i18nキー
     * @param {Object} params - i18nパラメータ
     * @param {number} duration - 表示時間
     */
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
