<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const { t } = useI18n();
const { createRules } = useValidation();
const { showSuccess, handleApiError } = useApiError();

const submitting = ref(false);
const form = ref(null);
const usernameField = ref(null);

const formData = ref({
    username: '',
    employee_id: '',
    password: '',
    is_admin: false,
});

const breadcrumbs = computed(() => [
    { title: t('breadcrumbs.home'), to: routes.HOME, disabled: false },
    { title: t('breadcrumbs.admin'), to: routes.ADMIN, disabled: false },
    { title: t('breadcrumbs.users.list'), to: routes.USERS, disabled: false },
    { title: t('breadcrumbs.users.create'), disabled: true },
]);

const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();
const passwordRules = createRules.newPassword();

// 画面表示時にユーザー名フィールドにフォーカス
onMounted(async () => {
    await nextTick();
    usernameField.value?.focus();
});

async function submitForm() {
    // 重複送信防止
    if (submitting.value) return;

    const { valid } = await form.value.validate();

    if (!valid) {
        // バリデーションエラー時は最初のエラーフィールドにフォーカス
        await nextTick();
        const firstErrorInput = document.querySelector('.v-input--error input');
        if (firstErrorInput) {
            firstErrorInput.focus();
        }
        return;
    }

    submitting.value = true;
    try {
        await usersAPI.create(formData.value);
        showSuccess('pages.users.create.success', {
            username: formData.value.username,
        });
        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error);
    } finally {
        submitting.value = false;
    }
}

function goBack() {
    router.replace(routes.USERS);
}
</script>

<template>
    <div>
        <Header
            :app-title="t('pages.users.create.title')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="10" md="6">
                    <v-card elevation="2">
                        <v-card-text class="pa-6">
                            <v-form ref="form" @submit.prevent="submitForm">
                                <v-text-field
                                    ref="usernameField"
                                    v-model="formData.username"
                                    :label="$t('form.fields.username') + ' *'"
                                    :rules="usernameRules"
                                    variant="outlined"
                                    class="mb-4"
                                    required
                                    :hint="t('form.hint.min', { min: 3 })"
                                    persistent-hint
                                />

                                <v-text-field
                                    v-model="formData.employee_id"
                                    :label="$t('form.fields.employeeId') + ' *'"
                                    :rules="employeeIdRules"
                                    variant="outlined"
                                    type="text"
                                    inputmode="numeric"
                                    class="mb-4"
                                    required
                                    :hint="t('form.hint.employeeIdFormat')"
                                    persistent-hint
                                />

                                <v-text-field
                                    v-model="formData.password"
                                    :label="$t('form.fields.password') + ' *'"
                                    :rules="passwordRules"
                                    variant="outlined"
                                    type="password"
                                    class="mb-4"
                                    required
                                    :hint="t('form.hint.passwordStrength')"
                                    persistent-hint
                                />

                                <v-checkbox
                                    v-model="formData.is_admin"
                                    :label="t('form.fields.isAdmin')"
                                    class="mb-2"
                                    hide-details
                                />

                                <v-divider class="my-4" />

                                <div class="d-flex gap-2">
                                    <v-btn
                                        type="submit"
                                        color="primary"
                                        size="large"
                                        variant="outlined"
                                        :loading="submitting"
                                        :prepend-icon="ICONS.buttons.add"
                                    >
                                        {{ t('buttons.create') }}
                                    </v-btn>

                                    <v-spacer />

                                    <v-btn
                                        variant="outlined"
                                        size="large"
                                        :prepend-icon="ICONS.buttons.arrowBack"
                                        @click="goBack"
                                    >
                                        {{ t('buttons.back') }}
                                    </v-btn>
                                </div>
                            </v-form>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </div>
</template>
