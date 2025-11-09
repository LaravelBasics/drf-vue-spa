<script setup>
import { computed } from 'vue';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        default: '確認',
    },
    message: {
        type: String,
        required: true,
    },
    confirmText: {
        type: String,
        default: '実行',
    },
    cancelText: {
        type: String,
        default: 'キャンセル',
    },
    confirmColor: {
        type: String,
        default: 'error',
    },
    icon: {
        type: String,
        default: 'info',
    },
    confirmIcon: {
        type: String,
        default: 'check',
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

const dialog = computed({
    get: () => props.modelValue,
    set: (value) => emit('update:modelValue', value),
});

function handleConfirm() {
    emit('confirm');
}

function handleCancel() {
    emit('cancel');
    dialog.value = false;
}
</script>

<template>
    <v-dialog v-model="dialog" persistent max-width="500">
        <v-card>
            <v-toolbar :color="confirmColor" density="comfortable">
                <v-toolbar-title>
                    <v-icon :icon="icon" class="mr-2" />
                    {{ title }}
                </v-toolbar-title>
            </v-toolbar>

            <v-card-text class="pa-6">
                <p class="text-body-1">{{ message }}</p>
                <slot name="content"></slot>
            </v-card-text>

            <v-divider />

            <v-card-actions class="pa-4">
                <v-btn
                    :prepend-icon="confirmIcon"
                    :color="confirmColor"
                    variant="elevated"
                    @click="handleConfirm"
                    :loading="loading"
                >
                    {{ confirmText }}
                </v-btn>

                <v-spacer />

                <v-btn variant="text" @click="handleCancel" :disabled="loading">
                    {{ cancelText }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>
