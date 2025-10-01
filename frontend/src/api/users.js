import api from '@/plugins/axios';

export const usersAPI = {
    list(params = {}) {
        return api.get('users/', { params });
    },

    get(id) {
        return api.get(`users/${id}/`);
    },

    create(data) {
        return api.post('users/', data);
    },

    update(id, data) {
        return api.put(`users/${id}/`, data);
    },

    delete(id) {
        return api.delete(`users/${id}/`);
    },

    stats() {
        return api.get('users/stats/');
    },
};
