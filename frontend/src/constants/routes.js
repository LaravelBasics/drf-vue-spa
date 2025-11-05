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
});

// ✅ 汎用化したヘルパー関数
function createResourceRoutes(basePath) {
    return {
        list: () => basePath,
        create: () => `${basePath}/create`,
        detail: (id) => `${basePath}/${id}`,
        update: (id) => `${basePath}/${id}/update`,
        delete: (id) => `${basePath}/${id}/delete`,
    };
}

export const userRoutes = createResourceRoutes('/admin/users');

// 将来的に追加する場合
// export const productRoutes = createResourceRoutes('/admin/products');
// export const orderRoutes = createResourceRoutes('/admin/orders');

/**
 * ルート名定義（router.push({ name }) 用）
 * router/index.js の name と一致させる
 */
export const ROUTE_NAMES = Object.freeze({
    HOME: 'Home',
    LOGIN: 'Login',
    LOGOUT: 'Logout',
    SETTINGS: 'Settings',
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
