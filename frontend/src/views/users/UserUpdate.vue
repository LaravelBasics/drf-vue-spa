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
const { createRules } = useValidation(); // ⭐ コンポーザブルから取得
const { handleApiError, showSuccess } = useApiError();

const loading = ref(true);
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

// ⭐ 基本ルール
const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();

// ⭐ パスワード関連ルール（changePassword の状態に応じて切り替え）
const passwordRules = computed(() => {
    // パスワード変更チェックがOFFの場合は、ルールを適用しない
    if (!changePassword.value) return [];
    // ONの場合は新規パスワードルールを適用
    return createRules.newPassword();
});

const passwordConfirmRules = computed(() => {
    if (!changePassword.value) return [];
    // パスワード確認用ルール（一致チェック）
    return createRules.passwordConfirm(formData.value.password);
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
    // ⭐ フォームバリデーション
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

<template>
    <div>
        <Header
            :app-title="t('pages.users.updateTitle')"
            :breadcrumbs="breadcrumbs"
        ></Header>

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="12" md="10">
                    <v-card elevation="2" v-if="!loading">
                        <!-- <v-card-title class="text-h5 pa-6 bg-grey-lighten-4">
                            {{ t('pages.users.updateTitle2') }}
                        </v-card-title> -->

                        <v-card-text class="pa-6">
                            <!-- ⭐ フォーム参照をセット -->
                            <v-form
                                ref="form"
                                @submit.prevent
                                @keypress.enter.prevent
                            >
                                <v-row>
                                    <v-col cols="12" md="6" class="pb-0">
                                        <!-- ⭐ 基本情報 -->
                                        <v-text-field
                                            v-model="formData.username"
                                            :label="t('form.fields.username')"
                                            :rules="usernameRules"
                                            variant="outlined"
                                            class="mb-2"
                                            required
                                        />
                                    </v-col>

                                    <v-col cols="12" md="6" class="pb-0">
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
                                    </v-col>

                                    <v-col cols="12" md="6" class="pt-0">
                                        <!-- ⭐ パスワード変更セクション -->
                                        <div class="mb-0">
                                            <v-checkbox
                                                v-model="changePassword"
                                                label="パスワードを変更する"
                                                hide-details
                                                class="mb-2"
                                            />

                                            <v-expand-transition>
                                                <div v-if="changePassword">
                                                    <!-- ⭐ ルール適用 -->
                                                    <v-text-field
                                                        v-model="
                                                            formData.password
                                                        "
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
                                                            showPassword =
                                                                !showPassword
                                                        "
                                                        variant="outlined"
                                                        class="mb-3"
                                                        hint="8文字以上、英字と数字を含む"
                                                        persistent-hint
                                                    />

                                                    <!-- ⭐ パスワード確認ルール適用 -->
                                                    <v-text-field
                                                        v-model="
                                                            passwordConfirm
                                                        "
                                                        label="新しいパスワード（確認）"
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
                                                        hint="確認のため再度入力してください"
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
