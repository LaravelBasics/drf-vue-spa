<script setup>
import { ref, onMounted, nextTick, computed, onBeforeUnmount } from 'vue'; // ⭐ onBeforeUnmount 追加
import { useAuthStore } from '@/stores/auth';
import { useRoute, useRouter } from 'vue-router'; // ⭐ useRouter 追加
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Footer from '@/components/Footer.vue';
import Notification from '@/components/Notification.vue';
import { routes } from '@/constants/routes';
import { BREAKPOINTS } from '@/constants/breakpoints'; // ⭐ 追加

const auth = useAuthStore();
const route = useRoute();
const router = useRouter(); // ⭐ 追加
const appReady = ref(false);

// ⭐ 計算プロパティで現在のルートが非対応デバイス画面かどうかを判定
const isUnsupportedRoute = computed(() => {
    return route.path === routes.UNSUPPORTED_DEVICE;
});

const waitForFontsAndIcons = () => {
    return new Promise((resolve) => {
        if (document.fonts) {
            document.fonts.ready.then(resolve);
        } else {
            setTimeout(resolve, 200);
        }
    });
};

// ⭐ グローバルな画面サイズ監視（追加）
const handleGlobalResize = () => {
    const windowWidth = window.innerWidth;

    console.log('📱 Global Resize:', {
        width: windowWidth,
        threshold: BREAKPOINTS.LARGE_SCREEN,
        currentRoute: route.path,
        requiresLargeScreen: route.meta?.requiresLargeScreen,
    });

    // ⭐ パターン1: 大画面必須のページで画面が小さくなった
    if (
        route.meta?.requiresLargeScreen &&
        windowWidth < BREAKPOINTS.LARGE_SCREEN
    ) {
        console.warn('📱 画面が小さくなりました - UNSUPPORTED_DEVICE へ遷移');
        router.push({ path: routes.UNSUPPORTED_DEVICE, replace: true });
        return;
    }

    // ⭐ パターン2: UNSUPPORTED_DEVICE で画面が大きくなった
    if (
        route.path === routes.UNSUPPORTED_DEVICE &&
        windowWidth >= BREAKPOINTS.LARGE_SCREEN
    ) {
        console.log('✅ 画面が大きくなりました - 適切なページへ遷移');
        const targetRoute = auth.isAuthenticated ? routes.HOME : routes.LOGIN;
        router.push({ path: targetRoute, replace: true });
    }
};

onMounted(async () => {
    try {
        console.log('🔄 UI準備開始...');

        await Promise.all([
            auth.initialized ? Promise.resolve() : auth.initialize(),
            waitForFontsAndIcons(),
            new Promise((resolve) => setTimeout(resolve, 50)),
        ]);

        await nextTick();

        console.log('✅ UI準備完了 - 表示開始');
        appReady.value = true;

        // ⭐ グローバルな resize 監視を開始
        window.addEventListener('resize', handleGlobalResize);

        // ⭐ 初回チェック
        handleGlobalResize();
    } catch (error) {
        console.error('❌ UI準備エラー:', error);
        appReady.value = true;
    }
});

// ⭐ クリーンアップ（追加）
onBeforeUnmount(() => {
    window.removeEventListener('resize', handleGlobalResize);
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
