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

            // ⭐ 優先順位1: detail（Django が翻訳済み）
            if (errorData.detail) {
                errorMessage = errorData.detail;
            }

            // ⭐ 優先順位2: フィールド別エラー
            if (!errorMessage) {
                errorMessage = extractFirstFieldError(errorData);
            }

            // ⭐ 優先順位3: error_code から翻訳（フォールバック）
            if (!errorMessage && errorData.error_code) {
                const backendErrorKey = `backend.errors.${errorData.error_code}`;
                const translated = t(backendErrorKey);
                if (translated !== backendErrorKey) {
                    errorMessage = translated;
                }
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
        const fieldErrors = ['employee_id', 'username', 'email', 'password'];

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

// # ==================== エラー処理の優先順位（推奨） ====================
// """
// 【優先順位】

// 1. detail（Django が翻訳済み）
//    → バックエンドで gettext_lazy を使って翻訳
//    → フロントエンドはそのまま表示

// 2. フィールド別エラー（employee_id, username など）
//    → Django の ValidationError が翻訳済み

// 3. error_code から翻訳（フォールバック）
//    → Django で翻訳されなかった場合のみ
//    → フロントエンドの ja.json から翻訳

// 【なぜ detail を優先するか】

// ✅ Django が標準で提供する翻訳を活用できる
// ✅ バックエンドでメッセージを管理できる
// ✅ フロントエンドの翻訳ファイルが肥大化しない
// ✅ バックエンドの変更がフロントエンドに影響しにくい

// 【フロントエンドの翻訳が必要なケース】

// - UI独自のメッセージ（例: 「本当に削除しますか？」）
// - バックエンドから返されないメッセージ
// - ネットワークエラー、タイムアウトなど
// """

// # ==================== 実務でのベストプラクティス ====================
// """
// 【小規模プロジェクト】
// → Django の gettext_lazy のみ使用
// → フロントエンドは detail をそのまま表示

// 【中規模プロジェクト】
// → Django + フロントエンドの両方で翻訳
// → error_code はフォールバック用

// 【大規模プロジェクト】
// → Django + フロントエンド + 翻訳管理ツール（Lokalise, Crowdin）
// → エラーコードを統一管理

// 【メンテナンス性】

// バックエンドで翻訳するメリット:
// ✅ メッセージを一箇所で管理
// ✅ バリデーションロジックと翻訳が近い
// ✅ フロントエンドがシンプル

// フロントエンドで翻訳するメリット:
// ✅ API レスポンスが小さい
// ✅ 言語切り替えが即座に反映
// ✅ オフライン対応しやすい

// 【推奨される組み合わせ】

// 1. バックエンドのバリデーションエラー → Django で翻訳
// 2. ビジネスロジックエラー → error_code + フロントエンド翻訳
// 3. UI独自のメッセージ → フロントエンド翻訳のみ
// """
