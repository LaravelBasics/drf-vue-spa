// src/stores/auth.js - 認証状態管理

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI } from '@/api/auth';
import { resetCSRFToken } from '@/plugins/axios';
import router from '@/router';
import { routes } from '@/constants/routes';

export const useAuthStore = defineStore(
    'auth',
    () => {
        const user = ref(null);
        const loading = ref(false);
        const error = ref(null);
        const initialized = ref(false);

        const isAuthenticated = computed(() => !!user.value);
        const isLoading = computed(() => loading.value);

        // ログイン処理（セッションベース）
        async function loginSession(employeeId, password) {
            loading.value = true;
            error.value = null;

            try {
                await authAPI.login(employeeId, password);
                await fetchUser();
            } finally {
                loading.value = false;
            }
        }

        // ユーザー情報取得
        async function fetchUser() {
            if (loading.value) return;

            loading.value = true;
            try {
                const response = await authAPI.me();
                user.value = response.data;
                error.value = null;
            } catch (err) {
                if (err.response?.status === 403) {
                    user.value = null;
                } else {
                    error.value = 'ユーザー情報の取得に失敗しました';
                }
            } finally {
                loading.value = false;
            }
        }

        // ログアウト処理
        async function logout(redirect = true) {
            loading.value = true;

            try {
                if (user.value) {
                    await authAPI.logout();
                }
            } catch (e) {
                // ログアウトAPIが失敗してもクライアント側の状態はクリア
            } finally {
                user.value = null;
                error.value = null;
                loading.value = false;
                resetCSRFToken();

                if (
                    redirect &&
                    router.currentRoute.value.path !== routes.LOGIN
                ) {
                    router.push(routes.LOGIN).catch(() => {});
                }
            }
        }

        function clearError() {
            error.value = null;
        }

        // 初期化処理（アプリ起動時に実行）
        async function initialize() {
            if (initialized.value) {
                return;
            }

            loading.value = true;

            try {
                if (user.value) {
                    // 永続化されたユーザー情報がある場合はサーバーと同期
                    try {
                        await fetchUser();
                    } catch (error) {
                        if (error.response?.status === 403) {
                            // セッション無効の場合はログアウト
                            user.value = null;
                            error.value = null;
                        }
                    }
                }
            } finally {
                initialized.value = true;
                loading.value = false;
            }
        }

        // セッション有効性チェック
        async function validateSession() {
            if (!user.value) {
                return false;
            }

            try {
                await fetchUser();
                return !!user.value;
            } catch (error) {
                return false;
            }
        }

        return {
            // State
            user,
            loading,
            error,
            initialized,

            // Computed
            isAuthenticated,
            isLoading,

            // Actions
            loginSession,
            fetchUser,
            logout,
            clearError,
            initialize,
            validateSession,
        };
    },
    {
        persist: {
            paths: ['user'],
        },
    },
);
