// src/main.js - 完全版
import { createApp } from 'vue';
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

// ⭐ グローバルエラーハンドラー - コンポーネント内のエラーをキャッチ
app.config.errorHandler = (err, instance, info) => {
    console.error('Global error:', err);
    console.error('Component:', instance);
    console.error('Error info:', info);

    // ⭐ 通知を表示
    try {
        const notificationStore = useNotificationStore();

        // i18n から翻訳を取得
        const errorMessage = i18n.global.t('notifications.error.unknown');

        // ユーザーにエラーを通知
        notificationStore.error(errorMessage, 7000);
    } catch (notificationError) {
        console.error('Failed to show notification:', notificationError);
        // 最終手段: アラート表示
        if (import.meta.env.DEV) {
            alert('予期しないエラーが発生しました: ' + err.message);
        }
    }
};

// ⭐ 未処理のPromise拒否をキャッチ（async/awaitのエラー）
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);

    // ⭐ 通知を表示
    try {
        const notificationStore = useNotificationStore();
        const errorMessage = i18n.global.t('notifications.error.unknown');

        notificationStore.error(errorMessage, 7000);
    } catch (error) {
        console.error('Failed to show rejection notification:', error);
    }

    // ⭐ デフォルトの警告を抑制（オプション）
    event.preventDefault();
});

// ⭐ アプリケーション初期化
const initializeApp = async () => {
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

        // ⭐ 初期化失敗を通知（アプリマウント後に表示）
        setTimeout(() => {
            try {
                const notificationStore = useNotificationStore();
                notificationStore.warning(
                    i18n.global.t('notifications.warning.initializationFailed'),
                    5000,
                );
            } catch (e) {
                console.error('通知表示失敗:', e);
            }
        }, 100);
    } finally {
        // ⭐ 初期化の成否に関わらずアプリを起動
        app.mount('#app');
        console.log('✅ アプリケーション起動');
    }
};

initializeApp();
