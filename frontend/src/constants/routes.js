// src/constants/routes.js - シンプルなパス定義 + ヘルパー関数

/**
 * ルートパス定義
 * - パラメータなしのパスは直接使用
 * - パラメータありのパスはヘルパー関数を使用
 */
export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',

    // メインページ
    HOME: '/',

    // サブページ
    SETTINGS: '/settings',

    // 管理機能 - children構造用
    ADMIN: {
        ROOT: '/admin',
        INDEX: '', // children用の空パス
        USERS: {
            SEGMENT: 'users', // children用の相対パス
            INDEX: '', // /admin/users のインデックス
            CREATE: 'create', // /admin/users/create
            DETAIL: ':id', // /admin/users/:id (動的パラメータ)
            UPDATE: ':id/update', // /admin/users/:id/update
            DELETE: ':id/delete', // /admin/users/:id/delete
        },
    },

    // エラーページ
    UNSUPPORTED_DEVICE: '/unsupported-device',
});

/**
 * ユーザー関連のパスヘルパー
 * パラメータを含むパスを簡単に生成
 */
export const userRoutes = {
    list: () => '/admin/users',
    create: () => '/admin/users/create',
    detail: (id) => `/admin/users/${id}`,
    update: (id) => `/admin/users/${id}/update`,
    delete: (id) => `/admin/users/${id}/delete`,
};

/**
 * ルート名定義（router.push({ name }) 用）
 * router/index.js の name と一致させる
 */
export const ROUTE_NAMES = Object.freeze({
    HOME: 'Home',
    LOGIN: 'Login',
    LOGOUT: 'Logout',
    SETTINGS: 'Settings',
    UNSUPPORTED_DEVICE: 'UnsupportedDevice',
    NOT_FOUND: 'NotFound',

    ADMIN: {
        MENU: 'AdminMenu',
        USERS: {
            LIST: 'UserList',
            CREATE: 'UserCreate',
            DETAIL: 'UserDetail',
            UPDATE: 'UserUpdate',
            DELETE: 'UserDelete',
        },
    },
});
