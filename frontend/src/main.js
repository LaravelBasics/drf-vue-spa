// src/main.js - アプリケーションのエントリーポイント
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

// Piniaセットアップ（永続化プラグイン有効化）
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(vuetify);
app.use(i18n);

// Vuetifyインスタンスをグローバルに登録（locale.jsで使用）
window.$vuetify = vuetify;

/**
 * グローバルエラーハンドラー
 * - 開発環境: 詳細なログを出力
 * - 本番環境: 簡潔なログのみ出力し、ユーザーに通知を表示
 */
app.config.errorHandler = (err, instance, info) => {
    if (import.meta.env.DEV) {
        console.error('Global error:', err);
        console.error('Component:', instance);
        console.error('Error info:', info);
    } else {
        console.error('Error:', err.message);
    }

    // アプリがマウント済みの場合のみ通知表示
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

/**
 * 未処理のPromise拒否をキャッチ
 * async/awaitやPromiseチェーンで捕捉されなかったエラーを処理
 */
window.addEventListener('unhandledrejection', (event) => {
    if (import.meta.env.DEV) {
        console.error('Unhandled promise rejection:', event.reason);
    } else {
        console.error('Promise rejection:', event.reason?.message);
    }

    // アプリがマウント済みの場合のみ通知表示
    if (app._container) {
        try {
            const notificationStore = useNotificationStore();
            const errorMessage = i18n.global.t('notifications.error.unknown');
            notificationStore.error(errorMessage, 7000);
        } catch (error) {
            console.error('Failed to show rejection notification:', error);
        }
    }

    event.preventDefault();
});

/**
 * アプリケーション初期化
 * - 認証状態の復元
 * - 言語設定の適用
 * - 初期化失敗時もアプリを起動（部分的な機能提供）
 */
const initializeApp = async () => {
    let initializationError = null;

    try {
        const authStore = useAuthStore();
        const localeStore = useLocaleStore();

        // 認証状態を初期化（セッション復元）
        await authStore.initialize();

        // Vuetifyの初期言語を設定
        vuetify.locale.current = localeStore.locale;
    } catch (error) {
        initializationError = error;
    } finally {
        // 初期化の成否に関わらずアプリを起動
        app.mount('#app');

        // マウント後に初期化エラーを通知
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
