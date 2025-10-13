// src/constants/routes.js

export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',

    // メインページ
    HOME: '/',

    // サブページ
    // DASHBOARD: '/dashboard',
    // PROFILE: '/profile',
    SETTINGS: '/settings',

    // 管理機能
    ADMIN: '/admin',
    USERS: '/users',
    USER_CREATE: '/users/create',
    USER_DETAIL: '/users/:id',
    USER_UPDATE: '/users/:id/update',
    USER_DELETE: '/users/:id/delete',

    // ⭐ エラーページ
    UNSUPPORTED_DEVICE: '/unsupported-device',
});
