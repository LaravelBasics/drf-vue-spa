// src/main.js - 最終改善版
import { createApp, nextTick } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';

import 'material-symbols/outlined.css';
import './assets/style/main.scss';

import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { useLocaleStore } from '@/stores/locale';

const app = createApp(App);

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(vuetify);
app.use(i18n);

// ⭐ Vuetify インスタンスをグローバルに登録
window.$vuetify = vuetify;

// ⭐ グローバルエラーハンドラー（環境変数対応 + マウントチェック）
app.config.errorHandler = (err, instance, info) => {
    // ⭐ 開発環境でのみ詳細ログ
    if (import.meta.env.DEV) {
        console.error('Global error:', err);
        console.error('Component:', instance);
        console.error('Error info:', info);
    } else {
        // ⭐ 本番環境では簡潔に
        console.error('Error:', err.message);
    }

    // ⭐ アプリがマウント済みの場合のみ通知
    if (app._container) {
        try {
            const notificationStore = useNotificationStore();
            const errorMessage = i18n.global.t('notifications.error.unknown');
            notificationStore.error(errorMessage, 7000);
        } catch (notificationError) {
            console.error('Failed to show notification:', notificationError);
        }
    }
};

// ⭐ 未処理のPromise拒否をキャッチ（環境変数対応 + マウントチェック）
window.addEventListener('unhandledrejection', (event) => {
    // ⭐ 開発環境でのみ詳細ログ
    if (import.meta.env.DEV) {
        console.error('Unhandled promise rejection:', event.reason);
    } else {
        console.error('Promise rejection:', event.reason?.message);
    }

    // ⭐ アプリがマウント済みの場合のみ通知
    if (app._container) {
        try {
            const notificationStore = useNotificationStore();
            const errorMessage = i18n.global.t('notifications.error.unknown');
            notificationStore.error(errorMessage, 7000);
        } catch (error) {
            console.error('Failed to show rejection notification:', error);
        }
    }

    // ⭐ デフォルトの警告を抑制
    event.preventDefault();
});

// ⭐ アプリケーション初期化
const initializeApp = async () => {
    let initializationError = null;

    try {
        console.log('🔄 アプリケーション事前初期化...');

        const authStore = useAuthStore();
        const localeStore = useLocaleStore();

        // ⭐ 認証状態を初期化
        await authStore.initialize();

        // ⭐ Vuetify の初期言語を設定
        vuetify.locale.current = localeStore.locale;

        console.log('✅ 事前初期化完了');
    } catch (error) {
        console.error('❌ 事前初期化エラー（継続します）:', error);
        initializationError = error;
    } finally {
        // ⭐ 初期化の成否に関わらずアプリを起動
        app.mount('#app');
        console.log('✅ アプリケーション起動');

        // ⭐ マウント後に初期化エラーを通知（nextTick で確実に）
        if (initializationError) {
            await nextTick();
            try {
                const notificationStore = useNotificationStore();
                notificationStore.warning(
                    i18n.global.t('notifications.warning.initializationFailed'),
                    5000,
                );
            } catch (e) {
                console.error('通知表示失敗:', e);
            }
        }
    }
};

initializeApp();
