// src/stores/notification.js - 通知メッセージ管理

import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useNotificationStore = defineStore('notification', () => {
    const show = ref(false);
    const message = ref('');
    const type = ref('success');
    const timeout = ref(5000);

    function showNotification(
        msg,
        notificationType = 'success',
        duration = 5000,
    ) {
        message.value = msg;
        type.value = notificationType;
        timeout.value = duration;
        show.value = true;
    }

    // 通知タイプ別のヘルパー関数
    function success(msg, duration = 5000) {
        showNotification(msg, 'success', duration);
    }

    function error(msg, duration = 7000) {
        // エラーは長めに表示
        showNotification(msg, 'error', duration);
    }

    function warning(msg, duration = 5000) {
        showNotification(msg, 'warning', duration);
    }

    function info(msg, duration = 5000) {
        showNotification(msg, 'info', duration);
    }

    function close() {
        show.value = false;
    }

    return {
        show,
        message,
        type,
        timeout,
        showNotification,
        success,
        error,
        warning,
        info,
        close,
    };
});
