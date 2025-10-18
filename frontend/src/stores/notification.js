//　Desktop\template\frontend\src\stores\notification.js
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

    function success(msg, duration = 5000) {
        // ⭐ 通常の成功メッセージ5秒
        showNotification(msg, 'success', duration);
    }

    function error(msg, duration = 7000) {
        // ⭐ エラーは長めに7秒
        showNotification(msg, 'error', duration);
    }

    function warning(msg, duration = 5000) {
        // ⭐ 警告5秒
        showNotification(msg, 'warning', duration);
    }

    function info(msg, duration = 5000) {
        // ⭐ 情報5秒
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
