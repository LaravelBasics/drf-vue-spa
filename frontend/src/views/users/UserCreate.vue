<script setup>
import { ref, computed } from 'vue';
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
const { createRules } = useValidation(); // ⭐ コンポーザブルから取得
const { handleApiError, showSuccess } = useApiError();

const submitting = ref(false);
const form = ref(null); // ⭐ フォーム参照

const formData = ref({
    username: '',
    employee_id: '',
    password: '',
    is_admin: false,
});

// ⭐ ブレッドクラム
const breadcrumbs = computed(() => [
    { title: t('nav.home'), to: routes.HOME, disabled: false },
    { title: t('pages.admin.title'), to: routes.ADMIN, disabled: false },
    { title: t('pages.users.title'), to: routes.USERS, disabled: false },
    { title: t('pages.users.createTitle'), disabled: true },
]);

// ⭐ バリデーションルールは createRules から直接取得
const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();
const passwordRules = createRules.newPassword();

async function submitForm() {
    // ⭐ フォームバリデーション（Login.vueと同じパターン）
    const { valid } = await form.value.validate();
    if (!valid) return;

    submitting.value = true;
    try {
        await usersAPI.create(formData.value);
        showSuccess('pages.users.createSuccess', {
            username: formData.value.username,
        });
        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error, 'pages.users.createError');
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
            :app-title="t('pages.users.createTitle')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container class="pa-6">
            <v-row justify="center">
                <v-col cols="12" md="8" lg="6">
                    <v-card elevation="2">
                        <v-card-title class="text-h5 pa-6 bg-grey-lighten-4">
                            {{ t('pages.users.createTitle') }}
                        </v-card-title>

                        <v-card-text class="pa-6">
                            <!-- ⭐ フォーム参照をセット -->
                            <v-form ref="form" @submit.prevent="submitForm">
                                <!-- ⭐ ルールをバインド -->
                                <v-text-field
                                    v-model="formData.username"
                                    :label="t('form.fields.username')"
                                    :rules="usernameRules"
                                    variant="outlined"
                                    class="mb-4"
                                    required
                                />

                                <v-text-field
                                    v-model="formData.employee_id"
                                    :label="t('form.fields.employeeId')"
                                    :rules="employeeIdRules"
                                    variant="outlined"
                                    type="text"
                                    inputmode="numeric"
                                    class="mb-4"
                                    required
                                    hint="10桁以内の数字"
                                    persistent-hint
                                />

                                <v-text-field
                                    v-model="formData.password"
                                    :label="t('form.fields.password')"
                                    :rules="passwordRules"
                                    variant="outlined"
                                    type="password"
                                    class="mb-4"
                                    required
                                    hint="8文字以上、英字と数字を含む"
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
                                        :prepend-icon="ICONS.action.save"
                                    >
                                        {{ t('common.create') }}
                                    </v-btn>

                                    <v-spacer></v-spacer>

                                    <v-btn
                                        variant="outlined"
                                        size="large"
                                        prepend-icon="arrow_back"
                                        @click="goBack"
                                    >
                                        {{ t('common.back') }}
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
