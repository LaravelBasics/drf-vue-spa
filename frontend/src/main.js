// src/main.js
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
import { useLocaleStore } from '@/stores/locale'; // ⭐ 追加

const app = createApp(App);

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(vuetify);
app.use(i18n);

// ⭐ Vuetify インスタンスをグローバルに登録
window.$vuetify = vuetify;

// ⭐ グローバルエラーハンドラー - ユーザーに通知も表示
app.config.errorHandler = (err, instance, info) => {
    console.error('Global error:', err);
    console.error('Component:', instance);
    console.error('Error info:', info);

    // ⭐ Piniaストアにアクセスして通知を表示
    try {
        const notificationStore = useNotificationStore();
        const { t } = app.config.globalProperties.$i18n || {};

        // エラーメッセージを抽出
        let errorMessage = err?.message || 'Unknown error occurred';

        // i18n が利用可能なら翻訳を使用
        if (t) {
            errorMessage = t('notifications.error.unknown');
        }

        // ユーザーにエラーを通知
        notificationStore.error(errorMessage, 7000);
    } catch (notificationError) {
        console.error('Failed to show notification:', notificationError);
        // 通知の表示に失敗してもアプリは動作する
    }
};

// ⭐ 未処理のPromise拒否もキャッチ（重要）
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);

    try {
        const notificationStore = useNotificationStore();
        const { t } = app.config.globalProperties.$i18n || {};

        let errorMessage = 'An unexpected error occurred';
        if (t) {
            errorMessage = t('notifications.error.unknown');
        }

        notificationStore.error(errorMessage, 7000);
    } catch (error) {
        console.error('Failed to show rejection notification:', error);
    }
});

// ⭐ 事前初期化
const initializeApp = async () => {
    try {
        console.log('🔄 アプリケーション事前初期化...');

        const authStore = useAuthStore();
        const localeStore = useLocaleStore(); // ⭐ 追加

        await authStore.initialize();

        // ⭐ Vuetify の初期言語を設定
        vuetify.locale.current = localeStore.locale;

        console.log('✅ 事前初期化完了');
    } catch (error) {
        console.error('❌ 事前初期化エラー（継続します）:', error);
    } finally {
        app.mount('#app');
        console.log('✅ アプリケーション起動');
    }
};

initializeApp();
