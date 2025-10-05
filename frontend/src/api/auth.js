import api from '@/plugins/axios';

export const authAPI = {
    getCsrf() {
        return api.get('auth/csrf/');
    },

    login(employeeId, password) {
        return api.post('auth/login/', { employee_id: employeeId, password });
    },

    logout() {
        return api.post('auth/logout/');
    },

    me() {
        return api.get('auth/me/');
    },
};
