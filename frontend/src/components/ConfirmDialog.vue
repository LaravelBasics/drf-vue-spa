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

// 確認ボタンの色に応じてヘッダー背景を切り替え
const headerClass = computed(() => {
    const colorMap = {
        error: 'bg-error text-white',
        warning: 'bg-warning text-white',
        primary: 'bg-primary text-white',
        success: 'bg-success text-white',
    };
    return colorMap[props.confirmColor] || 'bg-grey-lighten-2';
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
    <v-dialog
        v-model="dialog"
        persistent
        max-width="500"
        class="dialog-offset-up"
    >
        <v-card>
            <v-card-title class="text-h5 pa-4" :class="headerClass">
                <v-icon :icon="icon" class="me-2"></v-icon>
                {{ title }}
            </v-card-title>

            <v-card-text class="pa-6">
                <p class="text-body-1">{{ message }}</p>

                <!-- スロットで追加情報を差し込み可能 -->
                <slot name="content"></slot>
            </v-card-text>

            <v-card-actions class="pa-4">
                <v-btn
                    :color="confirmColor"
                    @click="handleConfirm"
                    :loading="loading"
                    class="custom-confirm"
                >
                    <v-icon class="me-2">{{ confirmIcon }}</v-icon>
                    {{ confirmText }}
                </v-btn>

                <v-spacer />

                <v-btn
                    variant="outlined"
                    @click="handleCancel"
                    :disabled="loading"
                >
                    {{ cancelText }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<style scoped>
.v-btn.custom-confirm {
    border: 2px solid;
}

.v-btn.custom-confirm.v-btn--theme-error {
    border-color: rgb(var(--v-theme-error)) !important;
}

.v-btn.custom-confirm.v-btn--theme-warning {
    border-color: rgb(var(--v-theme-warning)) !important;
}

.v-btn.custom-confirm.v-btn--theme-primary {
    border-color: rgb(var(--v-theme-primary)) !important;
}

.v-btn.custom-confirm.v-btn--theme-success {
    border-color: rgb(var(--v-theme-success)) !important;
}

/* ダイアログ位置を上方向にオフセット */
.dialog-offset-up :deep(.v-overlay__content) {
    top: 50px !important;
    width: 80%;
    height: 40%;
}
</style>
