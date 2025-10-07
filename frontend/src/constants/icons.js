// src/constants/icons.js - アイコン統一管理

export const ICONS = Object.freeze({
    // ナビゲーション
    nav: {
        menu: 'mdi-menu',
        home: 'mdi-home',
        dashboard: 'mdi-view-dashboard',
        settings: 'mdi-cog',
        profile: 'mdi-account',
        logout: 'mdi-power',
        divider: 'mdi-chevron-right',
        management: 'mdi-account-cog',
    },

    // アクション
    action: {
        add: 'mdi-plus',
        edit: 'mdi-pencil',
        delete: 'mdi-delete',
        save: 'mdi-content-save',
        cancel: 'mdi-close',
        search: 'mdi-magnify',
        filter: 'mdi-filter',
        refresh: 'mdi-refresh',
        download: 'mdi-download',
        upload: 'mdi-upload',
        export: 'mdi-file-excel',
        view: 'mdi-eye-outline', // ← 追加
        detail: 'mdi-information-outline', // ← 別の選択肢
    },

    // 状態
    status: {
        success: 'mdi-check-circle',
        error: 'mdi-alert-circle',
        warning: 'mdi-alert',
        info: 'mdi-information',
        loading: 'mdi-loading',
        admin: 'mdi-shield-check',
        check: 'mdi-check-bold',
        minus: 'mdi-minus',
    },

    // フォーム
    form: {
        user: 'mdi-account',
        password: 'mdi-lock',
        email: 'mdi-email',
        phone: 'mdi-phone',
        date: 'mdi-calendar',
        time: 'mdi-clock',
        visibility: 'mdi-eye',
        visibilityOff: 'mdi-eye-off',
    },

    // ファイル・データ
    file: {
        document: 'mdi-file-document',
        pdf: 'mdi-file-pdf-box',
        excel: 'mdi-file-excel',
        image: 'mdi-file-image',
        folder: 'mdi-folder',
    },
});
