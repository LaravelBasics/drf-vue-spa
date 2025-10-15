// src/plugins/axios.js (改善版)

import axios from 'axios';
import Cookies from 'js-cookie';
import { useLocaleStore } from '@/stores/locale';

const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '10000', 10); // デフォルト10秒

const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    timeout: API_TIMEOUT,
});

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
            console.error('CSRFトークンの取得に失敗:', error);
            throw error;
        }
    }

    reset() {
        this.tokenFetched = false;
        this.fetchingPromise = null;
    }
}

const csrfManager = new CSRFManager();

// リクエストインターセプター
api.interceptors.request.use(async (config) => {
    // ⭐ 言語ヘッダーを追加
    const localeStore = useLocaleStore();
    config.headers['Accept-Language'] = localeStore.locale;

    const method = config.method?.toLowerCase();
    const methodsRequiringCsrf = ['post', 'put', 'patch', 'delete'];

    if (methodsRequiringCsrf.includes(method)) {
        try {
            await csrfManager.ensureToken();
            const csrfToken = Cookies.get('csrftoken');
            if (csrfToken) {
                config.headers['X-CSRFToken'] = csrfToken;
            }
        } catch (error) {
            console.warn('CSRFトークンの設定をスキップ:', error);
        }
    }

    return config;
});

// ⭐ CSRFトークンリセット関数をエクスポート
export const resetCSRFToken = () => {
    csrfManager.reset();
};

// レスポンスインターセプター（改善版）
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const { response, config } = error;

        if (response) {
            // 認証エラーハンドリング
            if ([401, 403].includes(response.status)) {
                const isLogoutRequest = config.url?.endsWith('auth/logout/');

                if (!isLogoutRequest) {
                    // ⭐ 直接ストアを呼び出し（コールバック不要）
                    const { useAuthStore } = await import('@/stores/auth');
                    const auth = useAuthStore();

                    if (auth.isAuthenticated) {
                        console.warn(
                            '認証エラーが発生しました - 自動ログアウトします',
                        );
                        await auth.logout(true);
                    }
                }
            }

            // CSRFエラーの場合はトークンをリセット
            if (
                response.status === 403 &&
                response.data?.detail?.toLowerCase().includes('csrf')
            ) {
                console.warn('CSRFトークンエラー - リセットします');
                csrfManager.reset();
            }
        }

        return Promise.reject(error);
    },
);

export default api;
