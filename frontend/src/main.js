// src/main.js
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

// ==================== プラグイン登録 ====================
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(vuetify);
app.use(i18n);

// ==================== アプリ状態管理 ====================
let isAppMounted = false;

const showErrorNotification = (messageKey) => {
    if (!isAppMounted) return;

    try {
        const notificationStore = useNotificationStore();
        const errorMessage = i18n.global.t(messageKey);
        notificationStore.error(errorMessage, 7000);
    } catch (error) {
        console.error('Failed to show notification:', error);
    }
};

// ==================== エラーハンドリング ====================
app.config.errorHandler = (err, instance, info) => {
    if (import.meta.env.DEV) {
        console.error('Global error:', err);
        console.error('Component:', instance);
        console.error('Error info:', info);
    } else {
        console.error('Error:', err.message);
    }

    showErrorNotification('notifications.error.unknown');
};

window.addEventListener('unhandledrejection', (event) => {
    if (import.meta.env.DEV) {
        console.error('Unhandled promise rejection:', event.reason);
    } else {
        console.error('Promise rejection:', event.reason?.message);
    }

    showErrorNotification('notifications.error.unknown');
    event.preventDefault();
});

// ==================== アプリケーション初期化 ====================
const initializeApp = async () => {
    let initializationError = null;

    try {
        const authStore = useAuthStore();
        useLocaleStore(); // ← これでlocalStorage自動復元+i18n同期

        // 認証状態を初期化
        await authStore.initialize();

        // ✅ 削除: vuetify.locale.current の手動設定は不要!
        // createVueI18nAdapterが自動的にi18nと同期する
    } catch (error) {
        console.error('Initialization error:', error);
        initializationError = error;
    } finally {
        app.mount('#app');
        isAppMounted = true;

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
