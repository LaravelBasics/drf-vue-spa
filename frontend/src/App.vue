<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Footer from '@/components/Footer.vue';
import Notification from '@/components/Notification.vue';

const auth = useAuthStore();
const appReady = ref(false);

// フォント・アイコン読み込み待機
const waitForFontsAndIcons = () => {
    return new Promise((resolve) => {
        if (document.fonts) {
            document.fonts.ready.then(resolve);
        } else {
            setTimeout(resolve, 200);
        }
    });
};

onMounted(async () => {
    try {
        await Promise.all([
            auth.initialized ? Promise.resolve() : auth.initialize(),
            waitForFontsAndIcons(),
        ]);

        await nextTick();
        appReady.value = true;
    } catch (error) {
        console.error('App initialization error:', error);
        appReady.value = true;
    }
});
</script>

<template>
    <v-app>
        <!-- 通知コンポーネント（全画面共通） -->
        <Notification />

        <!-- メインコンテンツ（フェードインアニメーション付き） -->
        <div
            v-show="appReady"
            :class="['app-content', { 'fade-in': appReady }]"
        >
            <!-- ログイン済みでナビゲーションを表示 -->
            <NavBar v-if="auth.user" />
            <SideBar v-if="auth.user" />

            <v-main>
                <router-view />
            </v-main>

            <Footer v-if="auth.user" />
        </div>

        <!-- ローディング画面 -->
        <div v-show="!appReady" class="loading-screen"></div>
    </v-app>
</template>

<style scoped>
.app-content {
    opacity: 0;
    transition: opacity 0.2s ease-in-out;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
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
