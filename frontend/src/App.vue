<template>
    <v-app>
        <Notification></Notification>

        <div
            v-show="appReady"
            :class="['app-content', { 'fade-in': appReady }]"
        >
            <NavBar v-if="auth.user" />

            <SideBar v-if="auth.user" />

            <v-main>
                <router-view></router-view>
            </v-main>
        </div>

        <div v-show="!appReady" class="loading-screen"></div>
    </v-app>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Notification from '@/components/Notification.vue';

const auth = useAuthStore();
const appReady = ref(false);

const waitForFontsAndIcons = () => {
    return new Promise((resolve) => {
        // Material Design Icons の読み込み完了を待つ
        if (document.fonts) {
            document.fonts.ready.then(resolve);
        } else {
            // document.fonts がサポートされていない場合は固定時間待機
            setTimeout(resolve, 200);
        }
    });
};

onMounted(async () => {
    try {
        console.log('🔄 UI準備開始...');

        // ⭐ 並列で複数の準備を実行
        await Promise.all([
            // 認証初期化（main.jsで済んでいればすぐ終わる）
            auth.initialized ? Promise.resolve() : auth.initialize(),
            // フォント・アイコン読み込み
            waitForFontsAndIcons(),
            // 最小表示時間（チラつき防止）
            new Promise((resolve) => setTimeout(resolve, 100)), // 少し短縮
        ]);

        // ⭐ Vue の DOM 更新を待つ
        await nextTick();

        console.log('✅ UI準備完了 - 表示開始');

        // ⭐ 一気に表示
        appReady.value = true;
    } catch (error) {
        console.error('❌ UI準備エラー:', error);
        // エラーが発生しても表示する
        appReady.value = true;
    }
});
</script>

<style scoped>
.app-content {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
}

.app-content.fade-in {
    opacity: 1;
}

.loading-screen {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: #ffffff;
    z-index: 9999;
}
</style>

<style>
/* ⭐ グローバルなページ遷移スタイル */

/* 通常のページ遷移（ホーム等） */
.page-transition-enter-active,
.page-transition-leave-active {
    transition: all 0.25s ease-out;
}

.page-transition-enter-from {
    opacity: 0;
    transform: translateY(10px);
}

.page-transition-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* ログインページ専用の遷移 */
.login-page-transition-enter-active,
.login-page-transition-leave-active {
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.login-page-transition-enter-from {
    opacity: 0;
    transform: scale(0.95);
}

.login-page-transition-leave-to {
    opacity: 0;
    transform: scale(1.05);
}

/* ⭐ ちらつき防止 */
.v-main {
    min-height: 100vh;
    background-color: #fafafa;
}

/* レイアウトシフト防止 */
*,
*::before,
*::after {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

/* Vue Router link遷移も滑らかに */
.router-link-active {
    transition: all 0.2s ease;
}
</style>
