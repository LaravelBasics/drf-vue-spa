<!-- src/views/users/UserUpdate.vue - ユーザー更新画面 -->
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { userRoutes } from '@/constants/routes'; // ✅ userRoutesをインポート
import { ICONS } from '@/constants/icons.js';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { showSuccess, handleApiError } = useApiError();

const loading = ref(false);
const submitting = ref(false);
const form = ref(null);

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
const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();

// パスワード変更時のみバリデーション適用
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
    } catch (error) {
        handleApiError(error, 'pages.users.detail.error');
        router.push(userRoutes.list()); // ✅ ヘルパー関数を使用
    } finally {
        loading.value = false;
    }
}

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
        const updateData = {
            username: formData.value.username,
            employee_id: formData.value.employee_id,
            is_admin: formData.value.is_admin,
            is_active: formData.value.is_active,
        };

        // パスワード変更時のみパスワードを含める
        if (changePassword.value && formData.value.password) {
            updateData.password = formData.value.password;
        }

        await usersAPI.update(userId.value, updateData);

        showSuccess('pages.users.update.success', {
            username: formData.value.username,
        });

        router.replace(userRoutes.list()); // ✅ ヘルパー関数を使用
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
        <Header :app-title="t('pages.users.update.title')" />

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="12" md="10">
                    <v-card elevation="2" v-if="loading">
                        <v-card-text class="pa-6 text-center">
                            <v-progress-circular
                                indeterminate
                                color="primary"
                            />
                            <p class="mt-4">{{ t('app.loading') }}</p>
                        </v-card-text>
                    </v-card>

                    <v-card elevation="2" v-else>
                        <v-card-text class="pa-6">
                            <v-form ref="form" @submit.prevent="submitForm">
                                <v-row>
                                    <v-col cols="12" md="6" class="pb-0">
                                        <v-text-field
                                            v-model="formData.username"
                                            :label="
                                                $t('form.fields.username') +
                                                ' *'
                                            "
                                            :rules="usernameRules"
                                            variant="outlined"
                                            class="mb-2"
                                            required
                                            :hint="
                                                t('form.hint.min', { min: 3 })
                                            "
                                            persistent-hint
                                        />
                                    </v-col>

                                    <v-col cols="12" md="6" class="pb-0">
                                        <v-text-field
                                            v-model="formData.employee_id"
                                            :label="
                                                $t('form.fields.employeeId') +
                                                ' *'
                                            "
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
