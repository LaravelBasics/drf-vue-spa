// src/api/auth.js - 認証関連のAPIエンドポイント

import api from '@/plugins/axios';

export const authAPI = {
    // ログイン処理
    login(employeeId, password) {
        return api.post('auth/login/', { employee_id: employeeId, password });
    },

    // ログアウト処理
    logout() {
        return api.post('auth/logout/');
    },

    // 現在のユーザー情報取得
    me() {
        return api.get('auth/me/');
    },
};
