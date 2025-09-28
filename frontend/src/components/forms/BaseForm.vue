<template>
    <v-form ref="form" @submit.prevent="handleSubmit" :disabled="loading">
        <slot
            :rules="rules"
            :loading="loading"
            :error="error"
            :validate="validate"
            :reset="reset"
        ></slot>
    </v-form>
</template>

<script setup>
import { ref } from 'vue';
import { useValidation } from '@/composables/useValidation';

const props = defineProps({
    loading: { type: Boolean, default: false },
});

const emit = defineEmits(['submit']);

const { createRules } = useValidation();
const form = ref(null);
const error = ref('');

const rules = createRules;

async function handleSubmit() {
    const { valid } = await form.value.validate();
    if (valid) {
        emit('submit');
    }
}

async function validate() {
    return await form.value.validate();
}

function reset() {
    form.value?.reset();
    error.value = '';
}

defineExpose({
    validate,
    reset,
    setError: (msg) => {
        error.value = msg;
    },
});
</script>
