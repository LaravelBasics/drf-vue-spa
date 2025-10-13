<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Footer from '@/components/Footer.vue';
import Notification from '@/components/Notification.vue';
import { routes } from '@/constants/routes';

const auth = useAuthStore();
const route = useRoute();
const appReady = ref(false);

// ⭐ 計算プロパティで現在のルートが非対応デバイス画面かどうかを判定
const isUnsupportedRoute = computed(() => {
    // routes.UNSUPPORTED_DEVICE と一致するかどうかで判定します
    return route.path === routes.UNSUPPORTED_DEVICE;
});

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

<template>
    <v-app>
        <Notification />

        <div
            v-show="appReady"
            :class="['app-content', { 'fade-in': appReady }]"
        >
            <NavBar v-if="auth.user && !isUnsupportedRoute" />

            <SideBar v-if="auth.user && !isUnsupportedRoute" />

            <v-main>
                <router-view />
            </v-main>

            <!-- ⭐ フッター追加 -->
            <Footer v-if="auth.user && !isUnsupportedRoute" />
        </div>

        <div v-show="!appReady" class="loading-screen"></div>
    </v-app>
</template>

<style scoped>
.app-content {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    display: flex;
    flex-direction: column;
    min-height: 100vh; /* ⭐ フッターを下に固定するため */
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
