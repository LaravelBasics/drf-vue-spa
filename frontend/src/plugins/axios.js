// src/plugins/axios.js - Axios設定とCSRF管理

import axios from 'axios';
import Cookies from 'js-cookie';
import { useLocaleStore } from '@/stores/locale';

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10);

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    timeout: API_TIMEOUT,
});

/**
 * CSRFトークン管理クラス
 * 重複リクエストを防ぎ、トークン取得を一度だけ実行
 */
class CSRFManager {
    constructor() {
        this.tokenFetched = false;
        this.fetchingPromise = null;
    }

    async ensureToken() {
        if (this.tokenFetched) return;

        if (this.fetchingPromise) {
            return this.fetchingPromise;
        }

        this.fetchingPromise = this._fetchToken();
        try {
            await this.fetchingPromise;
        } finally {
            this.fetchingPromise = null;
        }
    }

    async _fetchToken() {
        try {
            await api.get('auth/csrf/');
            this.tokenFetched = true;
        } catch (error) {
            throw error;
        }
    }

    reset() {
        this.tokenFetched = false;
        this.fetchingPromise = null;
    }
}

const csrfManager = new CSRFManager();

// リクエストインターセプター（言語ヘッダー + CSRFトークン）
api.interceptors.request.use(async (config) => {
    // 言語設定をヘッダーに追加
    const localeStore = useLocaleStore();
    config.headers['Accept-Language'] = localeStore.locale;

    const method = config.method?.toLowerCase();
    const methodsRequiringCsrf = ['post', 'put', 'patch', 'delete'];

    // 更新系メソッドの場合CSRFトークンを付与
    if (methodsRequiringCsrf.includes(method)) {
        try {
            await csrfManager.ensureToken();
            const csrfToken = Cookies.get('csrftoken');
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            }
        } catch (error) {
            // CSRFトークン取得失敗時はスキップ
        }
    }

    return config;
});

// CSRFトークンリセット関数（ログアウト時などに使用）
export const resetCSRFToken = () => {
    csrfManager.reset();
};

// レスポンスインターセプター（認証エラー処理）
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const { response, config } = error;

        if (response) {
            // 認証エラー（401/403）時の自動ログアウト
            if ([401, 403].includes(response.status)) {
                const isLogoutRequest = config.url?.endsWith('auth/logout/');

                if (!isLogoutRequest) {
                    const { useAuthStore } = await import('@/stores/auth');
                    const auth = useAuthStore();

                    if (auth.isAuthenticated) {
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

export default api;
