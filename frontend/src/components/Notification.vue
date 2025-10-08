<!-- Desktop\template\frontend\src\components\Notification.vue -->
<template>
    <v-snackbar
        v-model="notification.show"
        :timeout="notification.timeout"
        :color="getColor"
        location="top"
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
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const notification = useNotificationStore();

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
