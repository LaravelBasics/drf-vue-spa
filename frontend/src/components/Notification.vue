<!-- Desktop\template\frontend\src\components\Notification.vue -->
<template>
    <v-snackbar
        v-model="notification.show"
        :timeout="notification.timeout"
        :color="getColor"
        :location="auth.user ? 'top' : 'top center'"
        :content-class="!auth.user ? 'snackbar-login-center' : ''"
        :multi-line="false"
    >
        <div class="d-flex align-center">
            <v-icon :icon="getIcon" class="mr-3" />
            <span class="text-body-1">{{ notification.message }}</span>
        </div>

        <template v-slot:actions>
            <v-btn
                variant="text"
                :icon="ICONS.action.close"
                size="x-small"
                @click="notification.close()"
            />
        </template>
    </v-snackbar>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const notification = useNotificationStore();
const auth = useAuthStore(); // ⭐ ユーザーがログイン済みか判定

const getColor = computed(() => {
    const colorMap = {
        success: 'success',
        error: 'error',
        warning: 'amber-darken-1',
        info: 'info',
    };
    return colorMap[notification.type] || 'info';
});

const getIcon = computed(() => {
    const iconMap = {
        success: ICONS.status.success, // check_circle
        error: ICONS.status.error, // error
        warning: ICONS.status.warning, // warning
        info: ICONS.status.info, // info
    };
    return iconMap[notification.type] || ICONS.status.info;
});
</script>

<style scoped>
/* ⭐ Vuetifyの内部要素にスタイルを適用するため、:deep() を使用します */
:deep(.snackbar-login-center) {
    /* 画面全体に固定 */
    position: fixed !important;

    /* 上部からの距離を調整 */
    top: 60px !important;

    /* 水平方向の開始点を画面中央に */
    left: 50% !important;

    /* 要素自身の幅の半分だけ左に戻し、完全な水平中央寄せを実現 */
    transform: translateX(-50%) !important;

    /* Vuetifyのデフォルトの left/right padding を上書きして
       画面幅いっぱいに広がるのを防ぐための調整（必要に応じて） */
    max-width: fit-content !important;
    margin: 0 !important; /* 中央寄せを妨げそうなマージンをリセット */
}
</style>
