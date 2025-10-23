<script setup>
import {
    ref,
    onMounted,
    nextTick,
    computed,
    onBeforeUnmount,
    watch,
} from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute, useRouter } from 'vue-router';
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Footer from '@/components/Footer.vue';
import Notification from '@/components/Notification.vue';
import { routes } from '@/constants/routes';
import { BREAKPOINTS } from '@/constants/breakpoints';

const auth = useAuthStore();
const route = useRoute();
const router = useRouter();
const appReady = ref(false);

// リサイズ監視用
const windowWidth = ref(window.innerWidth);
let resizeTimer = null;

const isUnsupportedRoute = computed(() => {
    return route.path === routes.UNSUPPORTED_DEVICE;
});

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

// デバウンス付きリサイズハンドラー（250ms待機）
function handleResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        windowWidth.value = window.innerWidth;
    }, 250);
}

// 画面サイズ変更時の自動遷移処理
watch(windowWidth, (newWidth) => {
    const isLarge = newWidth >= BREAKPOINTS.LARGE_SCREEN;

    // パターン1: 大画面必須ページで画面が小さくなった → UNSUPPORTED_DEVICEへ
    if (
        route.meta?.requiresLargeScreen &&
        !isLarge &&
        route.path !== routes.UNSUPPORTED_DEVICE
    ) {
        router.push({ path: routes.UNSUPPORTED_DEVICE, replace: true });
        return;
    }

    // パターン2: UNSUPPORTED_DEVICEで画面が大きくなった → 適切なページへ
    if (route.path === routes.UNSUPPORTED_DEVICE && isLarge) {
        const targetRoute = auth.isAuthenticated ? routes.HOME : routes.LOGIN;
        router.push({ path: targetRoute, replace: true });
    }
});

onMounted(async () => {
    try {
        await Promise.all([
            auth.initialized ? Promise.resolve() : auth.initialize(),
            waitForFontsAndIcons(),
        ]);

        await nextTick();
        appReady.value = true;

        // リサイズイベントリスナー登録
        window.addEventListener('resize', handleResize);

        // 初回チェック
        windowWidth.value = window.innerWidth;
    } catch (error) {
        appReady.value = true;
    }
});

// クリーンアップ
onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
    if (resizeTimer) {
        clearTimeout(resizeTimer);
        resizeTimer = null;
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
            <!-- ログイン済み & UNSUPPORTED_DEVICE以外でナビゲーションを表示 -->
            <NavBar v-if="auth.user && !isUnsupportedRoute" />
            <SideBar v-if="auth.user && !isUnsupportedRoute" />

            <v-main>
                <router-view />
            </v-main>

            <Footer v-if="auth.user && !isUnsupportedRoute" />
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
