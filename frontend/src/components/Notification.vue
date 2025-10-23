<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const notification = useNotificationStore();
const auth = useAuthStore();

// 通知タイプに応じた色を返す
const getColor = computed(() => {
    const colorMap = {
        success: 'success',
        error: 'error',
        warning: 'warning',
        info: 'info',
    };
    return colorMap[notification.type] || 'info';
});

// 通知タイプに応じたアイコンを返す
const getIcon = computed(() => {
    const iconMap = {
        success: ICONS.status.success,
        error: ICONS.status.error,
        warning: ICONS.status.warning,
        info: ICONS.status.info,
    };
    return iconMap[notification.type] || ICONS.status.info;
});

// ログイン前（user未設定時）は画面中央、ログイン後は右上に表示
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
/* ログイン画面では中央寄せ表示 */
:deep(.snackbar-login-center) {
    position: fixed !important;
    top: 60px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    max-width: 600px !important;
    width: auto !important;
    margin: 0 !important;
}

/* ログイン後は右上配置（デフォルト動作） */
.custom-snackbar :deep(.v-snackbar__wrapper) {
    max-width: 600px;
    min-width: 300px;
}
</style>
