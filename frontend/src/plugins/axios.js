// src/plugins/axios.js - Axios設定とCSRF管理（環境別対応版）

import axios from 'axios';
import { useLocaleStore } from '@/stores/locale';

// 環境変数の取得
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT, 10) || 10000;

// 開発環境でのバリデーション
if (import.meta.env.DEV && !API_BASE_URL) {
    console.error(
        '⚠️ VITE_API_BASE_URL is not defined. Please check your .env file.',
    );
}

// Axiosインスタンス作成
const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    timeout: API_TIMEOUT,
    // Axios組み込みのCSRF保護機能を活用
    xsrfCookieName: 'csrftoken',
    xsrfHeaderName: 'X-CSRFToken',
    /**
     * withXSRFToken設定:
     * - 開発環境: true（localhost:5173 → localhost:8000 はクロスオリジン）
     * - 本番環境: undefined（リバースプロキシで同一オリジン）
     */
    withXSRFToken: import.meta.env.DEV ? true : undefined,
});

/**
 * CSRFトークン管理クラス
 * 初回リクエスト前にトークンを取得し、重複リクエストを防ぐ
 */
class CSRFManager {
    constructor() {
        this.tokenFetched = false;
        this.fetchingPromise = null; // ✅ 重複リクエスト防止
    }

    /**
     * CSRFトークンの取得を保証
     * 既に取得済み、または取得中の場合は重複リクエストを防ぐ
     */
    async ensureToken() {
        if (this.tokenFetched) return; // ✅ キャッシュ

        if (this.fetchingPromise) {
            return this.fetchingPromise; // ✅ 並列リクエスト対策
        }

        this.fetchingPromise = this._fetchToken();
        await this.fetchingPromise;
        this.fetchingPromise = null;
    }

    /**
     * CSRFトークン取得API呼び出し
     */
    async _fetchToken() {
        await api.get('auth/csrf/');
        this.tokenFetched = true;
    }

    /**
     * トークン状態をリセット（ログアウト時などに使用）
     */
    reset() {
        this.tokenFetched = false;
        this.fetchingPromise = null;
    }
}

const csrfManager = new CSRFManager();

// リクエストインターセプター（言語ヘッダー + CSRF事前取得）
api.interceptors.request.use(async (config) => {
    // Accept-Languageヘッダーの設定
    const localeStore = useLocaleStore();
    config.headers['Accept-Language'] = localeStore.locale;

    // CSRFトークンが必要なメソッドの場合、事前取得
    const method = config.method.toLowerCase();
    const methodsRequiringCsrf = ['post', 'put', 'patch', 'delete'];

    if (methodsRequiringCsrf.includes(method)) {
        try {
            await csrfManager.ensureToken();
        } catch (error) {
            // CSRFトークン取得失敗時もリクエストは続行
            // （サーバー側で403エラーとなる）
            console.warn('Failed to fetch CSRF token:', error);
        }
    }

    return config;
});

// レスポンスインターセプター（認証エラー処理）
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const { response, config } = error;

        if (response) {
            // 認証エラー時の自動ログアウト処理
            if ([401, 403].includes(response.status)) {
                const isLogoutRequest = config.url?.endsWith('auth/logout/');

                // ログアウトリクエスト自体のエラーは無視
                if (!isLogoutRequest) {
                    // 動的importで循環依存を回避
                    const { useAuthStore } = await import('@/stores/auth');
                    const { useNotificationStore } = await import(
                        '@/stores/notification'
                    );
                    const auth = useAuthStore();

                    if (auth.isAuthenticated) {
                        const notification = useNotificationStore();
                        notification.warning(response.data?.detail, 5000);
                        await auth.logout(true);
                    }
                }
            }

            // CSRFエラー時はトークンをリセット
            if (
                response.status === 403 &&
                response.data?.detail?.toLowerCase().includes('csrf')
            ) {
                csrfManager.reset();
            }
        }

        return Promise.reject(error);
    },
);

/**
 * CSRFトークンをリセットする公開関数
 * ログアウト時などに使用
 */
export const resetCSRFToken = () => {
    csrfManager.reset();
};

export default api;
