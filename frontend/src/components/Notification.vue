<script setup>
import { computed } from 'vue';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const notification = useNotificationStore();

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
</script>

<template>
    <v-snackbar
        v-model="notification.show"
        :timeout="notification.timeout"
        :color="getColor"
        location="top"
        max-width="600"
        min-width="300"
        class="notification-center"
    >
        <div class="d-flex align-center">
            <v-icon :icon="getIcon" class="mr-3" />
            <span class="text-body-1">{{ notification.message }}</span>
        </div>

        <template #actions>
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
.notification-center :deep(.v-overlay__content) {
    left: 50%;
    transform: translateX(-50%);
    top: 60px;
}
</style>
