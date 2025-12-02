// src/api/auth.js - グループ認証対応

import api from '@/plugins/axios';

export const authAPI = {
    /**
     * ログイン（グループ認証版）
     * @param {string} groupId - グループID
     * @param {string} userId - ユーザーID
     * @param {string} password - パスワード
     */
    async login(groupId, userId, password) {
        const response = await api.post('auth/login/', {
            group_id: groupId,
            user_id: userId,
            password,
        });
        return response;
    },

    /**
     * ログアウト
     */
    async logout() {
        const response = await api.post('auth/logout/');
        return response;
    },

    /**
     * 現在のユーザー情報取得
     */
    async me() {
        const response = await api.get('auth/me/');
        return response;
    },

    /**
     * グループ一覧取得
     */
    async getGroups() {
        const response = await api.get('auth/groups/');
        return response;
    },
};
