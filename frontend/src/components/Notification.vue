<!-- C:\Users\pvufx\Desktop\template\frontend\src\components\Notification.vue -->
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
                icon="mdi-close"
                @click="notification.close()"
            />
        </template>
    </v-snackbar>
</template>

<script setup>
import { computed } from 'vue';
import { useNotificationStore } from '@/stores/notification';

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
        success: 'mdi-check-circle',
        error: 'mdi-alert-circle',
        warning: 'mdi-alert',
        info: 'mdi-information',
    };
    return iconMap[notification.type] || 'mdi-information';
});
</script>
