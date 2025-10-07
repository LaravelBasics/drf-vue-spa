// src/constants/routes.js (詳細画面追加版)

export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',

    // メインページ
    HOME: '/',

    // サブページ
    DASHBOARD: '/dashboard',
    PROFILE: '/profile',
    SETTINGS: '/settings',

    // 管理機能
    ADMIN: '/admin',
    USERS: '/users',
    USER_CREATE: '/users/create',
    USER_DETAIL: '/users/:id', // ⭐ 詳細画面（新規）
    USER_UPDATE: '/users/:id/update', // ⭐ 更新画面（リネーム）
    USER_DELETE: '/users/:id/delete',
});
