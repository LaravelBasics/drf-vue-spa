<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons.js';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { showSuccess, handleApiError } = useApiError();

// ⭐ 修正: true → false
const loading = ref(false);
const submitting = ref(false);
const form = ref(null);

// ⭐ フィールド参照
const usernameField = ref(null);
const employeeIdField = ref(null);
const passwordField = ref(null);

const changePassword = ref(false);
const showPassword = ref(false);
const showPasswordConfirm = ref(false);

const formData = ref({
    username: '',
    employee_id: '',
    is_admin: false,
    is_active: true,
    password: '',
});

const passwordConfirm = ref('');

const breadcrumbs = computed(() => [
    { title: t('breadcrumbs.home'), to: routes.HOME, disabled: false },
    { title: t('breadcrumbs.admin'), to: routes.ADMIN, disabled: false },
    { title: t('breadcrumbs.users.list'), to: routes.USERS, disabled: false },
    {
        title: t('breadcrumbs.users.detail'),
        to: routes.USER_DETAIL,
        disabled: true,
    },
    { title: t('breadcrumbs.users.update'), disabled: true },
]);

const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();

const passwordRules = computed(() => {
    if (!changePassword.value) return [];
    return createRules.newPassword();
});

const passwordConfirmRules = computed(() => {
    if (!changePassword.value) return [];
    return createRules.passwordConfirm(formData.value.password);
});

const userId = computed(() => route.params.id);

async function fetchUser() {
    // ⭐ 追加: 重複リクエスト防止
    if (loading.value) return;

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
        // ⭐ 読み込み後にフォーカス
        setTimeout(() => {
            usernameField.value?.focus();
        }, 100);
    } catch (error) {
        handleApiError(error, 'pages.users.detail.error');
        router.push(routes.USERS);
    } finally {
        loading.value = false;
    }
}

async function submitForm() {
    const { valid, errors } = await form.value.validate();

    if (!valid) {
        // ⭐ バリデーションエラー時にフォーカス
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

    // ⭐ 追加: 重複送信防止
    if (submitting.value) return;

    submitting.value = true;
    try {
        const updateData = {
            username: formData.value.username,
            employee_id: formData.value.employee_id,
            is_admin: formData.value.is_admin,
            is_active: formData.value.is_active,
        };

        if (changePassword.value && formData.value.password) {
            updateData.password = formData.value.password;
        }

        await usersAPI.update(userId.value, updateData);

        showSuccess('pages.users.update.success', {
            username: formData.value.username,
        });

        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error);
    } finally {
        submitting.value = false;
    }
}

onMounted(() => {
    fetchUser();
});
</script>

<template>
    <div>
        <Header
            :app-title="t('pages.users.update.title')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="12" md="10">
                    <!-- ⭐ 修正: loading 状態を先に表示 -->
                    <v-card elevation="2" v-if="loading">
                        <v-card-text class="pa-6 text-center">
                            <v-progress-circular
                                indeterminate
                                color="primary"
                            />
                            <p class="mt-4">{{ t('app.loading') }}</p>
                        </v-card-text>
                    </v-card>

                    <!-- ⭐ 修正: データ取得後に表示 -->
                    <v-card elevation="2" v-else>
                        <v-card-text class="pa-6">
                            <v-form
                                ref="form"
                                @submit.prevent
                                @keypress.enter.prevent
                            >
                                <v-row>
                                    <v-col cols="12" md="6" class="pb-0">
                                        <v-text-field
                                            ref="usernameField"
                                            v-model="formData.username"
                                            :label="t('form.fields.username')"
                                            :rules="usernameRules"
                                            variant="outlined"
                                            class="mb-2"
                                            required
                                            :hint="
                                                t('form.hint.max', { max: 20 })
                                            "
                                            persistent-hint
                                        />
                                    </v-col>

                                    <v-col cols="12" md="6" class="pb-0">
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
                                            :hint="
                                                t('form.hint.employeeIdFormat')
                                            "
                                            persistent-hint
                                        />
                                    </v-col>

                                    <v-col cols="12" md="6" class="pt-0">
                                        <div class="mb-0">
                                            <v-checkbox
                                                v-model="changePassword"
                                                :label="
                                                    t(
                                                        'form.labels.changePassword',
                                                    )
                                                "
                                                hide-details
                                                class="mb-2"
                                            />

                                            <v-expand-transition>
                                                <div v-if="changePassword">
                                                    <v-text-field
                                                        ref="passwordField"
                                                        v-model="
                                                            formData.password
                                                        "
                                                        :label="
                                                            t(
                                                                'form.labels.newPassword',
                                                            )
                                                        "
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
                                                            showPassword =
                                                                !showPassword
                                                        "
                                                        variant="outlined"
                                                        class="mb-3"
                                                        :hint="
                                                            t(
                                                                'form.hint.passwordStrength',
                                                            )
                                                        "
                                                        persistent-hint
                                                    />

                                                    <v-text-field
                                                        v-model="
                                                            passwordConfirm
                                                        "
                                                        :label="
                                                            t(
                                                                'form.labels.newPasswordConfirmation',
                                                            )
                                                        "
                                                        :rules="
                                                            passwordConfirmRules
                                                        "
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
                                                        :hint="
                                                            t(
                                                                'form.hint.newPasswordConfirmation',
                                                            )
                                                        "
                                                        persistent-hint
                                                    />
                                                </div>
                                            </v-expand-transition>
                                        </div>
                                    </v-col>
                                </v-row>

                                <v-row>
                                    <v-col cols="12" md="6" class="pt-0">
                                        <v-checkbox
                                            v-model="formData.is_admin"
                                            :label="t('form.fields.isAdmin')"
                                            class="mb-2"
                                            hide-details
                                        />
                                    </v-col>

                                    <v-col cols="12" md="6" class="pt-0">
                                        <v-checkbox
                                            v-model="formData.is_active"
                                            :label="t('form.fields.isActive')"
                                            class="mb-2"
                                            hide-details
                                        />
                                    </v-col>
                                </v-row>

                                <v-divider class="my-4" />

                                <div class="d-flex gap-2">
                                    <v-btn
                                        type="submit"
                                        @click="submitForm"
                                        color="primary"
                                        size="large"
                                        variant="outlined"
                                        :loading="submitting"
                                        :prepend-icon="ICONS.buttons.save"
                                    >
                                        {{ t('buttons.save') }}
                                    </v-btn>

                                    <v-spacer />

                                    <v-btn
                                        variant="outlined"
                                        size="large"
                                        :prepend-icon="ICONS.buttons.arrowBack"
                                        @click="router.back()"
                                        type="button"
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
