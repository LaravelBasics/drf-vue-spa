<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const notification = useNotificationStore();
const auth = useAuthStore();

const getColor = computed(() => {
    const colorMap = {
        success: 'success',
        error: 'error',
        warning: 'warning',
        info: 'info',
    };
    return colorMap[notification.type] || 'info';
});

const getIcon = computed(() => {
    const iconMap = {
        success: ICONS.status.success,
        error: ICONS.status.error,
        warning: ICONS.status.warning,
        info: ICONS.status.info,
    };
    return iconMap[notification.type] || ICONS.status.info;
});

// ⭐ ログイン状態に応じてクラスを切り替え
const snackbarClass = computed(() => {
    return auth.user ? '' : 'snackbar-login-center';
});
</script>

<template>
    <v-snackbar
        v-model="notification.show"
        :timeout="notification.timeout"
        :color="getColor"
        location="top"
        :content-class="snackbarClass"
        :multi-line="false"
        class="custom-snackbar"
    >
        <div class="d-flex align-center">
            <v-icon :icon="getIcon" class="mr-3" />
            <span class="text-body-1">{{ notification.message }}</span>
        </div>

        <template v-slot:actions>
            <v-btn
                variant="text"
                :icon="ICONS.buttons.close"
                size="x-small"
                @click="notification.close()"
            />
        </template>
    </v-snackbar>
</template>

<style scoped>
/* ⭐ ログイン時（ユーザーなし）の中央寄せ */
:deep(.snackbar-login-center) {
    position: fixed !important;
    top: 60px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    max-width: 600px !important;
    width: auto !important;
    margin: 0 !important;
}

/* ⭐ ログイン後（ユーザーあり）の右上配置（デフォルト） */
.custom-snackbar :deep(.v-snackbar__wrapper) {
    max-width: 600px;
    min-width: 300px;
}
</style>
