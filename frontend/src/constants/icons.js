// src/constants/icons.js - Material Symbols (Google公式) 版

export const ICONS = Object.freeze({
    // ナビゲーション
    nav: {
        menu: 'menu',
        home: 'home',
        dashboard: 'dashboard',
        settings: 'settings',
        profile: 'account_circle',
        logout: 'logout',
        divider: 'chevron_right',
        management: 'admin_panel_settings',
    },

    // アクション
    action: {
        add: 'add',
        edit: 'edit',
        delete: 'delete',
        save: 'save',
        cancel: 'close',
        search: 'search',
        filter: 'filter_list',
        refresh: 'refresh',
        download: 'download',
        upload: 'upload',
        export: 'description', // Excelアイコンの代替
        view: 'visibility',
        detail: 'info',
        close: 'close', // ⭐ 明示的に追加
    },

    // 状態
    status: {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info',
        loading: 'progress_activity',
        admin: 'verified_user',
        check: 'check',
        minus: 'remove',
        alert: 'notification_important', // ⭐ 追加
    },

    // フォーム
    form: {
        user: 'person',
        password: 'lock',
        email: 'email',
        phone: 'phone',
        date: 'calendar_today',
        time: 'schedule',
        visibility: 'visibility',
        visibilityOff: 'visibility_off',
    },

    // ファイル・データ
    file: {
        document: 'description',
        pdf: 'picture_as_pdf',
        excel: 'table_chart', // Excel代替
        image: 'image',
        folder: 'folder',
    },

    // ⭐ ブランド・その他
    brand: {
        deployed_code: 'deployed_code', // GitHubロゴの代替（Material Symbolsにロゴはないため）
        language: 'language', // 言語切り替え用
    },
});
