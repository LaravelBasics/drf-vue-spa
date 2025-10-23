// src/api/users.js - ユーザー管理のAPIエンドポイント

import api from '@/plugins/axios';

export const usersAPI = {
    // ユーザー一覧取得（フィルタ・ページネーション対応）
    list(params = {}) {
        return api.get('users/', { params });
    },

    // 特定ユーザーの詳細取得
    get(id) {
        return api.get(`users/${id}/`);
    },

    // 新規ユーザー作成
    create(data) {
        return api.post('users/', data);
    },

    // ユーザー情報更新
    update(id, data) {
        return api.put(`users/${id}/`, data);
    },

    // ユーザー削除
    delete(id) {
        return api.delete(`users/${id}/`);
    },

    // ユーザー統計情報取得
    stats() {
        return api.get('users/stats/');
    },

    // 管理者数取得（最後の管理者削除防止用）
    adminCount() {
        return api.get('users/admin-count/');
    },
};
