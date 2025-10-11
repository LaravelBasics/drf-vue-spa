<template>
    <div>
        <Header
            :app-title="t('pages.users.updateTitle')"
            :breadcrumbs="breadcrumbs"
        ></Header>

        <v-container class="pa-6">
            <v-row justify="center">
                <v-col cols="12" md="8" lg="8">
                    <v-card elevation="2" v-if="!loading">
                        <v-card-title class="text-h5 pa-6 bg-grey-lighten-4">
                            {{ t('pages.users.updateTitle2') }}
                        </v-card-title>

                        <v-card-text class="pa-6">
                            <v-form
                                ref="form"
                                @submit.prevent
                                @keypress.enter.prevent
                            >
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
                                    type="number"
                                    class="mb-4"
                                    required
                                    hint="10桁以内の数字"
                                    persistent-hint
                                />

                                <v-checkbox
                                    v-model="formData.is_admin"
                                    :label="t('form.fields.isAdmin')"
                                    class="mb-2"
                                    hide-details
                                />

                                <v-checkbox
                                    v-model="formData.is_active"
                                    :label="t('form.fields.isActive')"
                                    class="mb-2"
                                    hide-details
                                />

                                <v-divider class="my-6" />

                                <!-- パスワード変更セクション -->
                                <div class="mb-4">
                                    <v-checkbox
                                        v-model="changePassword"
                                        label="パスワードを変更する"
                                        hide-details
                                        class="mb-3"
                                    />

                                    <v-expand-transition>
                                        <div v-if="changePassword">
                                            <v-text-field
                                                v-model="formData.password"
                                                label="新しいパスワード"
                                                :rules="passwordRules"
                                                :type="
                                                    showPassword
                                                        ? 'text'
                                                        : 'password'
                                                "
                                                :append-inner-icon="
                                                    showPassword
                                                        ? 'visibility'
                                                        : 'visibility_off'
                                                "
                                                @click:append-inner="
                                                    showPassword = !showPassword
                                                "
                                                variant="outlined"
                                                class="mb-3"
                                                hint="8文字以上で入力してください"
                                                persistent-hint
                                            />

                                            <v-text-field
                                                v-model="passwordConfirm"
                                                label="新しいパスワード（確認）"
                                                :rules="passwordConfirmRules"
                                                :type="
                                                    showPasswordConfirm
                                                        ? 'text'
                                                        : 'password'
                                                "
                                                :append-inner-icon="
                                                    showPasswordConfirm
                                                        ? 'visibility'
                                                        : 'visibility_off'
                                                "
                                                @click:append-inner="
                                                    showPasswordConfirm =
                                                        !showPasswordConfirm
                                                "
                                                variant="outlined"
                                                hint="確認のため再度入力してください"
                                                persistent-hint
                                            />
                                        </div>
                                    </v-expand-transition>
                                </div>

                                <v-divider class="my-4" />

                                <div class="d-flex gap-2">
                                    <v-btn
                                        type="submit"
                                        @click="submitForm"
                                        color="primary"
                                        size="large"
                                        :loading="submitting"
                                        prepend-icon="save"
                                    >
                                        {{ t('common.save') }}
                                    </v-btn>

                                    <v-spacer></v-spacer>

                                    <v-btn
                                        variant="outlined"
                                        size="large"
                                        prepend-icon="arrow_back"
                                        @click="router.back()"
                                        type="button"
                                    >
                                        {{ t('common.back') }}
                                    </v-btn>
                                </div>
                            </v-form>
                        </v-card-text>
                    </v-card>

                    <!-- ローディング表示 -->
                    <v-card elevation="2" v-else>
                        <v-card-text class="pa-6 text-center">
                            <v-progress-circular
                                indeterminate
                                color="primary"
                            />
                            <p class="mt-4">{{ t('app.loading') }}</p>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { handleApiError, showSuccess } = useApiError();

const loading = ref(true);
const submitting = ref(false);
const form = ref(null);

const changePassword = ref(false);
const showPassword = ref(false);
const showPasswordConfirm = ref(false);
const passwordConfirm = ref('');

const formData = ref({
    username: '',
    employee_id: '',
    is_admin: false,
    is_active: true,
    password: '',
});

const breadcrumbs = computed(() => [
    { title: t('nav.home'), to: routes.HOME, disabled: false },
    { title: t('pages.admin.title'), to: routes.ADMIN, disabled: false },
    { title: t('pages.users.title'), to: routes.USERS, disabled: false },
    {
        title: t('pages.users.detailTitle2'),
        to: routes.USER_DETAIL,
        disabled: true,
    },
    { title: t('pages.users.updateTitle2'), disabled: true },
]);

const usernameRules = createRules.username();
const employeeIdRules = [
    (v) =>
        !!v ||
        t('form.validation.required', { field: t('form.fields.employeeId') }),
    (v) => /^\d{1,10}$/.test(v) || t('form.validation.employeeIdFormat'),
];

const passwordRules = computed(() => {
    if (!changePassword.value) return [];
    return [
        (v) => !!v || 'パスワードを入力してください',
        (v) =>
            (v && v.length >= 8) || 'パスワードは8文字以上で入力してください',
        (v) =>
            (v && v.length <= 128) ||
            'パスワードは128文字以内で入力してください',
    ];
});

const passwordConfirmRules = computed(() => {
    if (!changePassword.value) return [];
    return [
        (v) => !!v || '確認用パスワードを入力してください',
        (v) => v === formData.value.password || 'パスワードが一致しません',
    ];
});

const userId = computed(() => route.params.id);

async function fetchUser() {
    loading.value = true;
    try {
        const response = await usersAPI.get(userId.value);
        formData.value = {
            username: response.data.username,
            employee_id: response.data.employee_id,
            is_admin: response.data.is_admin,
            is_active: response.data.is_active,
            password: '',
        };
    } catch (error) {
        handleApiError(error, 'pages.users.fetchError');
        router.push(routes.USERS);
    } finally {
        loading.value = false;
    }
}

async function submitForm() {
    const { valid } = await form.value.validate();
    if (!valid) return;

    submitting.value = true;
    try {
        const updateData = {
            username: formData.value.username,
            employee_id: formData.value.employee_id,
            is_admin: formData.value.is_admin,
            is_active: formData.value.is_active,
        };

        // パスワード変更が選択されている場合のみ送信
        if (changePassword.value && formData.value.password) {
            updateData.password = formData.value.password;
        }

        await usersAPI.update(userId.value, updateData);

        showSuccess('pages.users.updateSuccess', {
            username: formData.value.username,
        });

        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error, 'pages.users.updateError');
    } finally {
        submitting.value = false;
    }
}

onMounted(() => {
    fetchUser();
});
</script>
