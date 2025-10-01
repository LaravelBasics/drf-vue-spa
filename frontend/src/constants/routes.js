// src/constants/routes.js (更新版)

export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/login',
    LOGOUT: '/logout',

    // メインページ
    HOME: '/',

    // サブページ
    DASHBOARD: '/dashboard',
    PROFILE: '/profile',
    SETTINGS: '/settings',

    // 管理機能
    USERS: '/users',
    USER_CREATE: '/users/create',
    USER_EDIT: '/users/:id/edit',
    USER_DELETE: '/users/:id/delete',
});
