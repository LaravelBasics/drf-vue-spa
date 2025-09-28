// src/constants/routes.js (更新版)

export const routes = Object.freeze({
    // 認証関連
    LOGIN: '/login',
    LOGOUT: '/logout',

    // メインページ
    HOME: '/', // ⭐ / をホームページに

    // サブページ
    SAMPLE: '/sample',
    PROFILE: '/profile',
    SETTINGS: '/settings',
    DASHBOARD: '/dashboard',
    // REGISTER: '/register',
    // DASHBOARD: '/dashboard',

    // // ユーザー関連
    // PROFILE: '/profile',
    // SETTINGS: '/settings',

    // // その他
    // ABOUT: '/about',
    // CONTACT: '/contact',

    // // 管理者用（必要に応じて）
    // ADMIN: '/admin',
    // USERS: '/admin/users',
});

// ⭐ ルートのメタ情報も定義
// export const routeMetadata = Object.freeze({
//     [routes.HOME]: {
//         title: 'ホーム',
//         requiresAuth: true,
//         icon: 'mdi-home',
//     },
//     [routes.PROFILE]: {
//         title: 'プロフィール',
//         requiresAuth: true,
//         icon: 'mdi-account',
//     },
//     [routes.LOGIN]: {
//         title: 'ログイン',
//         hideForAuth: true,
//         icon: 'mdi-login',
//     },
//     [routes.SETTINGS]: {
//         title: '設定',
//         requiresAuth: true,
//         icon: 'mdi-cog',
//     },
// });

// ⭐ ナビゲーション用のルート配列
// export const navigationRoutes = [
//     {
//         path: routes.HOME,
//         name: 'ホーム',
//         icon: 'mdi-home',
//         requiresAuth: true,
//     },
//     {
//         path: routes.PROFILE,
//         name: 'プロフィール',
//         icon: 'mdi-account',
//         requiresAuth: true,
//     },
//     {
//         path: routes.SETTINGS,
//         name: '設定',
//         icon: 'mdi-cog',
//         requiresAuth: true,
//     },
// ];

// ⭐ ルート検証用のヘルパー関数
// export const isValidRoute = (path) => {
//     return Object.values(routes).includes(path);
// };

// export const getRouteMetadata = (path) => {
//     return routeMetadata[path] || {};
// };
