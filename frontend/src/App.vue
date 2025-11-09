<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useAuthStore } from '@/stores/auth';
import NavBar from '@/components/NavBar.vue';
import SideBar from '@/components/SideBar.vue';
import Footer from '@/components/Footer.vue';
import Notification from '@/components/Notification.vue';

const auth = useAuthStore();
const appReady = ref(false);

/**
 * フォント・アイコンの読み込み待機
 * ✅ Cumulative Layout Shift (CLS) 対策
 */
const waitForFontsAndIcons = () => {
    return new Promise((resolve) => {
        if (document.fonts) {
            document.fonts.ready.then(resolve);
        } else {
            // フォールバック: 200ms待機
            setTimeout(resolve, 200);
        }
    });
};

onMounted(async () => {
    try {
        // ✅ フォント読み込み待機（main.jsで認証初期化済み）
        await waitForFontsAndIcons();
    } catch (error) {
        // フォント読み込み失敗は無視（アプリは動く）
        console.warn('Font loading failed:', error);
    } finally {
        // ✅ フォントの成否に関わらずアプリ起動
        await nextTick();
        appReady.value = true;
    }
});
</script>

<template>
    <v-app>
        <!-- 通知コンポーネント（全画面共通） -->
        <Notification />

        <!-- メインコンテンツ（フェードイン） -->
        <v-fade-transition>
            <div v-if="appReady" class="app-content">
                <NavBar v-if="auth.user" />
                <SideBar v-if="auth.user" />

                <v-main>
                    <router-view />
                </v-main>

                <Footer v-if="auth.user" />
            </div>
        </v-fade-transition>

        <!-- ローディング画面 -->
        <v-overlay
            :model-value="!appReady"
            persistent
            class="align-center justify-center"
        >
            <v-progress-circular indeterminate size="64" color="primary" />
        </v-overlay>
    </v-app>
</template>

<style scoped>
.app-content {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}
</style>
