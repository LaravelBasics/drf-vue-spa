import api from '@/plugins/axios';

export const authAPI = {
    getCsrf() {
        return api.get('auth/csrf/');
    },

    login(username, password) {
        return api.post('auth/login/', { username, password });
    },

    logout() {
        return api.post('auth/logout/');
    },

    me() {
        return api.get('auth/me/');
    },
};
