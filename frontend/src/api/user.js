import api from '@/plugins/axios';

export const userAPI = {
    // 一覧取得
    list() {
        return api.get('users/');
    },

    // 詳細取得
    get(id) {
        return api.get(`users/${id}/`);
    },

    // 作成
    create(data) {
        return api.post('users/', data);
    },

    // 更新
    update(id, data) {
        return api.put(`users/${id}/`, data);
    },

    // 削除
    delete(id) {
        return api.delete(`users/${id}/`);
    },
};
