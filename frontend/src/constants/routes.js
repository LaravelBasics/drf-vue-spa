// src/constants/routes.js - ルート定義の一元管理

export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',

    // メインページ
    HOME: '/',

    // サブページ
    SETTINGS: '/settings',

    // 管理機能
    ADMIN: '/admin',
    USERS: '/users',
    USER_CREATE: '/users/create',
    USER_DETAIL: '/users/:id',
    USER_UPDATE: '/users/:id/update',
    USER_DELETE: '/users/:id/delete',

    // エラーページ
    UNSUPPORTED_DEVICE: '/unsupported-device',
});
