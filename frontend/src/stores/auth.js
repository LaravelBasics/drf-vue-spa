// src/stores/auth.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api, { resetCSRFToken } from '@/plugins/axios';
import router from '@/router';

export const useAuthStore = defineStore(
    'auth',
    () => {
        const user = ref(null);
        const loading = ref(false);
        const error = ref(null);
        const initialized = ref(false); // ⭐ 初期化フラグ追加

        const isAuthenticated = computed(() => !!user.value);
        const isLoading = computed(() => loading.value);

        async function loginSession(username, password) {
            loading.value = true;
            error.value = null;

            try {
                await api.post('auth/login/', { username, password });
                await fetchUser();
                return { success: true };
            } catch (e) {
                const errorMessage =
                    e.response?.data?.message ||
                    e.response?.data?.detail ||
                    'ログインに失敗しました';
                error.value = errorMessage;
                console.error('Login failed:', e);
                return { success: false, error: errorMessage };
            } finally {
                loading.value = false;
            }
        }

        async function fetchUser() {
            if (loading.value) return;

            loading.value = true;
            try {
                const response = await api.get('auth/me/');
                user.value = response.data;
                error.value = null;
                console.log('✅ ユーザー情報取得成功:', user.value);
            } catch (err) {
                if (err.response?.status === 403) {
                    // ⭐ 403は未認証状態（想定内）- ユーザー情報をクリア
                    user.value = null;
                    console.log('ℹ️ 未認証状態を確認');
                } else {
                    console.error('❌ ユーザー情報の取得に失敗:', err);
                    error.value = 'ユーザー情報の取得に失敗しました';
                    // ⭐ ネットワークエラーなど、一時的なエラーの場合はuser.valueを保持
                }
            } finally {
                loading.value = false;
            }
        }

        async function logout(redirect = true) {
            loading.value = true;

            try {
                if (user.value) {
                    await api.post('auth/logout/');
                }
            } catch (e) {
                console.error('Logout API failed:', e);
            } finally {
                user.value = null;
                error.value = null;
                loading.value = false;
                resetCSRFToken();

                if (redirect && router.currentRoute.value.path !== '/login') {
                    router.push('/login').catch((err) => {
                        console.warn('リダイレクトエラー:', err);
                    });
                }
            }
        }

        function clearError() {
            error.value = null;
        }

        // stores/auth.js の initialize() メソッド部分（改善版）

        async function initialize() {
            if (initialized.value) {
                console.log('ℹ️ 既に初期化済みのためスキップ');
                return;
            }

            console.log('🔄 認証状態の初期化を開始...');
            loading.value = true; // ⭐ 初期化中はローディング状態に

            try {
                // ⭐ 永続化されたユーザー情報がある場合のみサーバーと同期
                if (user.value) {
                    console.log(
                        'ℹ️ 永続化されたユーザー情報を発見 - サーバーと同期します',
                    );

                    try {
                        await fetchUser(); // この中でloading制御される
                        console.log('✅ サーバーとの同期完了');
                    } catch (error) {
                        if (error.response?.status === 403) {
                            // セッション無効 - ユーザー情報をクリア
                            console.log(
                                '⚠️ セッション無効 - ログアウト処理実行',
                            );
                            user.value = null;
                            error.value = null;
                        } else {
                            // その他のエラー - 一時的な問題の可能性があるため永続化データを保持
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
                loading.value = false; // ⭐ 初期化完了
                console.log('✅ 認証状態の初期化完了');
            }
        }

        // ⭐ セッション検証（必要に応じて手動実行）
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
            validateSession, // ⭐ 追加
        };
    },
    {
        persist: {
            // ⭐ 永続化を有効にする（userのみ）
            paths: ['user'],
        },
    },
);
