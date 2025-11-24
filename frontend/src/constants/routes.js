// src/constants/routes.js - Vue Routerのpath定義 + 名前ベースナビゲーション用の定数

/**
 * ルートパス定義（router/index.jsで使用）
 * - children構造用のセグメント定義
 * - パラメータなしのパスは直接使用
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
            UPDATE: 'update', // ⚠️ 修正: ':id/update' → 'update' (Wrapperの子なので:id不要)
            DELETE: 'delete', // ⚠️ 修正: ':id/delete' → 'delete'
        },
    },
});

/**
 * ルート名定義（名前ベースナビゲーション用）
 *
 * 使用例:
 *   router.push({ name: ROUTE_NAMES.ADMIN.USERS.UPDATE, params: { id: 123 } })
 *   <router-link :to="{ name: ROUTE_NAMES.ADMIN.USERS.DETAIL, params: { id: user.id } }">
 *
 * 利点:
 *   - パス変更に強い（一箇所修正すればOK）
 *   - IDEの自動補完が効く
 *   - タイポを防げる
 *   - params継承が自動
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
            DETAIL_WRAPPER: 'UserDetailWrapper',
            LIST: 'UserList',
            CREATE: 'UserCreate',
            DETAIL: 'UserDetail',
            UPDATE: 'UserUpdate',
            DELETE: 'UserDelete',
        },
    },
});
