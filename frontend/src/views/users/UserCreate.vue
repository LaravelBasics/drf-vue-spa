<script setup>
import { ref, computed, onMounted } from 'vue';
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
const { handleApiError, showCreateSuccess } = useApiError();

const submitting = ref(false);
const form = ref(null);

// ⭐ 各フィールドの ref を作成
const usernameField = ref(null);
const employeeIdField = ref(null);
const passwordField = ref(null);

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

// ⭐ マウント時に最初のフィールドにフォーカス
onMounted(() => {
    setTimeout(() => {
        usernameField.value?.focus();
    }, 100);
});

async function submitForm() {
    const { valid, errors } = await form.value.validate();

    if (!valid) {
        // ⭐ バリデーションエラー時、最初のエラーフィールドにフォーカス
        if (errors && errors.length > 0) {
            const firstErrorField = errors[0]?.id;

            if (firstErrorField?.includes('username')) {
                usernameField.value?.focus();
            } else if (firstErrorField?.includes('employee')) {
                employeeIdField.value?.focus();
            } else if (firstErrorField?.includes('password')) {
                passwordField.value?.focus();
            }
        }
        return;
    }

    submitting.value = true;
    try {
        await usersAPI.create(formData.value);
        showCreateSuccess('pages.users.create.success', {
            username: formData.value.username,
        });
        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error, 'pages.users.create.error');
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
                                <!-- ⭐ ref を追加 -->
                                <v-text-field
                                    ref="usernameField"
                                    v-model="formData.username"
                                    :label="t('form.fields.username')"
                                    :rules="usernameRules"
                                    variant="outlined"
                                    class="mb-4"
                                    required
                                    :hint="
                                        t('form.hint.max', {
                                            max: 20,
                                        })
                                    "
                                    persistent-hint
                                />

                                <v-text-field
                                    ref="employeeIdField"
                                    v-model="formData.employee_id"
                                    :label="t('form.fields.employeeId')"
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
                                    ref="passwordField"
                                    v-model="formData.password"
                                    :label="t('form.fields.password')"
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
                                        :loading="submitting"
                                        :prepend-icon="ICONS.buttons.save"
                                    >
                                        {{ t('buttons.create') }}
                                    </v-btn>

                                    <v-spacer></v-spacer>

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
