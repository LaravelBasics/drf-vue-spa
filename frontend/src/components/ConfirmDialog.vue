<!-- src/components/ConfirmDialog.vue -->
<template>
    <v-dialog v-model="dialog" max-width="500" persistent>
        <v-card>
            <!-- ヘッダー -->
            <v-card-title class="text-h5 pa-4" :class="headerClass">
                <v-icon :icon="icon" class="me-2"></v-icon>
                {{ title }}
            </v-card-title>

            <!-- メッセージ -->
            <v-card-text class="pa-6">
                <p class="text-body-1">{{ message }}</p>

                <!-- 追加情報（オプション） -->
                <slot name="content"></slot>
            </v-card-text>

            <!-- ボタン -->
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>

                <v-btn
                    variant="outlined"
                    @click="handleCancel"
                    :disabled="loading"
                >
                    {{ cancelText }}
                </v-btn>

                <v-btn
                    :color="confirmColor"
                    @click="handleConfirm"
                    :loading="loading"
                >
                    <v-icon class="me-2">{{ confirmIcon }}</v-icon>
                    {{ confirmText }}
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const props = defineProps({
    // モーダルの表示/非表示
    modelValue: {
        type: Boolean,
        default: false,
    },

    // タイトル
    title: {
        type: String,
        default: '確認',
    },

    // メッセージ
    message: {
        type: String,
        required: true,
    },

    // 確認ボタンのテキスト
    confirmText: {
        type: String,
        default: '実行',
    },

    // キャンセルボタンのテキスト
    cancelText: {
        type: String,
        default: 'キャンセル',
    },

    // 確認ボタンの色（error, warning, primary等）
    confirmColor: {
        type: String,
        default: 'error',
    },

    // アイコン
    icon: {
        type: String,
        default: 'alert-circle',
    },

    // 確認ボタンのアイコン
    confirmIcon: {
        type: String,
        default: 'check',
    },

    // ローディング状態
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

// ヘッダーの色クラス
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
