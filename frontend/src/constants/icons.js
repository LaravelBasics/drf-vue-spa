// src/constants/icons.js - Material Symbols (Google公式) アイコン定義

export const ICONS = Object.freeze({
    // アプリケーションのタイトル・ロゴ
    app: {
        title: 'deployed_code',
    },

    // ナビゲーション
    nav: {
        menu: 'menu',
        home: 'home',
        dashboard: 'dashboard',
        settings: 'settings',
        profile: 'account_circle',
        logout: 'logout',
        divider: 'chevron_right', // パンくずリストの区切り
        management: 'admin_panel_settings',
    },

    // メニュー（機能別アイコン）
    menu: {
        // ユーザー管理
        users: 'group',
        roles: 'security',
        permissions: 'lock_person',

        // ログ・監査
        logs: 'history',
        audit: 'verified_user',
        activity: 'event',

        // システム設定
        settings: 'settings',
        configuration: 'tune',
        maintenance: 'build',

        // レポート・分析
        reports: 'assessment',
        analytics: 'analytics',
        export: 'download',
    },

    // ボタン操作
    buttons: {
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
        export: 'description', // Excel/CSVエクスポート用
        view: 'visibility',
        detail: 'info',
        close: 'close',
        arrowForward: 'arrow_forward',
        arrowBack: 'arrow_back',
        csv: 'table_chart',
        pdf: 'picture_as_pdf',
    },

    // 状態表示
    status: {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info',
        loading: 'progress_activity',
        admin: 'verified_user',
        check: 'check',
        minus: 'remove',
        alert: 'notification_important',
    },

    // フォーム入力
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
        image: 'image',
        folder: 'folder',
    },

    // ブランド・その他
    brand: {
        deployed_code: 'deployed_code',
        language: 'language', // 言語切り替え用
    },
});
