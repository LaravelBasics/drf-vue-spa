// src/stores/auth.js - グループ認証対応（is_admin対応版）

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI } from '@/api/auth';
import { resetCSRFToken } from '@/plugins/axios';
import router from '@/router';
import { ROUTE_NAMES } from '@/constants/routes';

export const useAuthStore = defineStore(
    'auth',
    () => {
        const user = ref(null);
        const loading = ref(false);
        const error = ref(null);
        const initialized = ref(false);
        const currentGroupId = ref(null);
        const currentGroupName = ref(null);

        const isAuthenticated = computed(() => !!user.value);
        const isLoading = computed(() => loading.value);

        // ✅ 管理者権限チェック（バックエンドのis_adminフィールドを参照）
        const isAdmin = computed(() => user.value?.is_admin ?? false);

        // ログイン処理（グループ認証版）
        async function loginSession(groupId, userId, password) {
            loading.value = true;
            error.value = null;

            try {
                await authAPI.login(groupId, userId, password);
                currentGroupId.value = groupId;
                await fetchUser(); // ユーザー情報取得（is_adminも含まれる）
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

                // バックエンドから返されたグループ情報を保存
                if (response.data.current_group) {
                    currentGroupId.value = response.data.current_group.group_id;
                    currentGroupName.value =
                        response.data.current_group.group_name;
                }
                error.value = null;
            } catch (err) {
                if (err.response?.status === 403) {
                    user.value = null;
                    currentGroupId.value = null;
                    currentGroupName.value = null;
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
                currentGroupId.value = null;
                currentGroupName.value = null;
                loading.value = false;
                resetCSRFToken();

                if (
                    redirect &&
                    router.currentRoute.value.name !== ROUTE_NAMES.LOGIN
                ) {
                    router.push({ name: ROUTE_NAMES.LOGIN }).catch(() => {});
                }
            }
        }

        function clearError() {
            error.value = null;
        }

        // 初期化処理
        async function initialize() {
            if (initialized.value) {
                return;
            }

            loading.value = true;

            try {
                if (user.value) {
                    try {
                        await fetchUser();
                    } catch (error) {
                        if (error.response?.status === 403) {
                            user.value = null;
                            error.value = null;
                            currentGroupId.value = null;
                            currentGroupName.value = null;
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
            currentGroupId,
            currentGroupName,

            // Computed
            isAuthenticated,
            isLoading,
            isAdmin, // ✅ 管理者権限チェック用

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
            paths: ['user', 'currentGroupId', 'currentGroupName'],
        },
    },
);
