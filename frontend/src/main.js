// src/main.js (初期化併用版 - より安全)

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import App from './App.vue';
import router from './router';
import vuetify from './plugins/vuetify';
import i18n from './plugins/i18n';

import '@mdi/font/css/materialdesignicons.css';
import './assets/style/main.scss';

import { useAuthStore } from '@/stores/auth';

const app = createApp(App);

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);
app.use(vuetify);
app.use(i18n);

app.config.errorHandler = (err, instance, info) => {
    console.error('Global error:', err);
    console.error('Component:', instance);
    console.error('Error info:', info);
};

// ⭐ 事前初期化（App.vueでの重複実行は自動的に回避される）
const initializeApp = async () => {
    try {
        console.log('🔄 アプリケーション事前初期化...');

        const authStore = useAuthStore();

        // ⭐ 事前に認証状態を初期化（App.vueでの処理を軽くする）
        await authStore.initialize();

        console.log('✅ 事前初期化完了');
    } catch (error) {
        console.error('❌ 事前初期化エラー（継続します）:', error);
        // エラーが発生してもアプリは起動する
    } finally {
        // ⭐ 初期化結果に関係なくマウント
        app.mount('#app');
        console.log('✅ アプリケーション起動');
    }
};

// 初期化実行
initializeApp();
