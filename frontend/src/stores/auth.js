// src/stores/auth.js - エラーハンドリング修正版

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

        // ⭐ 修正: エラーをそのまま throw する
        async function loginSession(employeeId, password) {
            loading.value = true;
            error.value = null;

            try {
                await authAPI.login(employeeId, password);
                await fetchUser();
                // ✅ 成功時のみ明示的に成功を返す（例外は throw）
                return { success: true };
            } catch (e) {
                // ⭐ エラーをキャッチして返さず、そのまま throw
                throw e;
            } finally {
                loading.value = false;
            }
        }

        async function fetchUser() {
            if (loading.value) return;

            loading.value = true;
            try {
                const response = await authAPI.me();
                user.value = response.data;
                error.value = null;
                console.log('✅ ユーザー情報取得成功:', user.value);
            } catch (err) {
                if (err.response?.status === 403) {
                    user.value = null;
                    console.log('ℹ️ 未認証状態を確認');
                } else {
                    console.error('❌ ユーザー情報の取得に失敗:', err);
                    error.value = 'ユーザー情報の取得に失敗しました';
                }
            } finally {
                loading.value = false;
            }
        }

        async function logout(redirect = true) {
            loading.value = true;

            try {
                if (user.value) {
                    await authAPI.logout();
                }
            } catch (e) {
                console.error('Logout API failed:', e);
            } finally {
                user.value = null;
                error.value = null;
                loading.value = false;
                resetCSRFToken();

                if (
                    redirect &&
                    router.currentRoute.value.path !== routes.LOGIN
                ) {
                    router.push(routes.LOGIN).catch((err) => {
                        console.warn('リダイレクトエラー:', err);
                    });
                }
            }
        }

        function clearError() {
            error.value = null;
        }

        async function initialize() {
            if (initialized.value) {
                console.log('ℹ️ 既に初期化済みのためスキップ');
                return;
            }

            console.log('🔄 認証状態の初期化を開始...');
            loading.value = true;

            try {
                if (user.value) {
                    console.log(
                        'ℹ️ 永続化されたユーザー情報を発見 - サーバーと同期します',
                    );

                    try {
                        await fetchUser();
                        console.log('✅ サーバーとの同期完了');
                    } catch (error) {
                        if (error.response?.status === 403) {
                            console.log(
                                '⚠️ セッション無効 - ログアウト処理実行',
                            );
                            user.value = null;
                            error.value = null;
                        } else {
                            console.warn(
                                '⚠️ 一時的なエラー - 永続化データを保持:',
                                error.message,
                            );
                        }
                    }
                } else {
                    console.log(
                        'ℹ️ 永続化されたユーザー情報なし - 未認証状態で開始',
                    );
                }
            } finally {
                initialized.value = true;
                loading.value = false;
                console.log('✅ 認証状態の初期化完了');
            }
        }

        async function validateSession() {
            if (!user.value) {
                console.log(
                    'ℹ️ ユーザー情報がないためセッション検証をスキップ',
                );
                return false;
            }

            console.log('🔄 セッション有効性を検証中...');
            try {
                await fetchUser();
                const isValid = !!user.value;
                console.log(
                    isValid ? '✅ セッション有効' : '❌ セッション無効',
                );
                return isValid;
            } catch (error) {
                console.error('❌ セッション検証エラー:', error);
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
