<template>
    <Header
        :app-title="t('pages.userEdit.title')"
        :breadcrumbs="breadcrumbs"
    ></Header>

    <v-container class="pa-6">
        <v-row justify="center">
            <v-col cols="12" md="8" lg="6">
                <v-card class="elevation-2">
                    <v-card-title class="text-h5 pa-6">
                        {{ t('pages.userEdit.title') }}
                    </v-card-title>

                    <v-card-text class="pa-6" v-if="!loading">
                        <v-form ref="form" @submit.prevent="submitForm">
                            <v-text-field
                                v-model="formData.username"
                                :label="t('form.fields.username')"
                                :rules="usernameRules"
                                variant="outlined"
                                class="mb-4"
                            />

                            <v-text-field
                                v-model="formData.employee_id"
                                :label="t('form.fields.employeeId')"
                                :rules="employeeIdRules"
                                variant="outlined"
                                type="number"
                                class="mb-4"
                            />

                            <v-checkbox
                                v-model="formData.is_admin"
                                :label="t('form.fields.isAdmin')"
                                class="mb-4"
                            />

                            <v-checkbox
                                v-model="formData.is_active"
                                :label="t('form.fields.isActive')"
                                class="mb-4"
                            />

                            <div class="d-flex gap-2">
                                <v-btn
                                    type="submit"
                                    color="primary"
                                    size="large"
                                    :loading="submitting"
                                >
                                    {{ t('common.save') }}
                                </v-btn>

                                <v-btn
                                    variant="outlined"
                                    size="large"
                                    @click="router.back()"
                                >
                                    {{ t('common.back') }}
                                </v-btn>
                            </div>
                        </v-form>
                    </v-card-text>

                    <!-- ローディング表示 -->
                    <v-card-text v-else class="pa-6 text-center">
                        <v-progress-circular
                            indeterminate
                            color="primary"
                        ></v-progress-circular>
                        <p class="mt-4">{{ t('app.loading') }}</p>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import Header from '@/components/Header.vue';
import { userAPI } from '@/api/user';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();

const loading = ref(true);
const submitting = ref(false);
const form = ref(null);

// フォームデータ
const formData = ref({
    username: '',
    employee_id: '',
    is_admin: false,
    is_active: true,
});

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('nav.home'),
        to: '/',
        disabled: false,
    },
    {
        title: t('nav.management'),
        to: '/management',
        disabled: false,
    },
    {
        title: t('pages.userManagement.title'),
        to: '/management',
        disabled: false,
    },
    {
        title: t('pages.userEdit.title'),
        disabled: true,
    },
]);

// バリデーションルール
const usernameRules = createRules.username();
const employeeIdRules = [
    (v) =>
        !!v ||
        t('form.validation.required', { field: t('form.fields.employeeId') }),
    (v) => /^\d{1,10}$/.test(v) || t('form.validation.employeeIdFormat'),
];

// ユーザーIDを取得
const userId = computed(() => route.params.id);

// ユーザー情報を取得
async function fetchUser() {
    loading.value = true;
    try {
        const response = await userAPI.get(userId.value);
        formData.value = {
            username: response.data.username,
            employee_id: response.data.employee_id,
            is_admin: response.data.is_admin,
            is_active: response.data.is_active,
        };
    } catch (error) {
        console.error('ユーザー情報取得エラー:', error);
        router.push('/management');
    } finally {
        loading.value = false;
    }
}

// フォーム送信
async function submitForm() {
    const { valid } = await form.value.validate();
    if (!valid) return;

    submitting.value = true;
    try {
        await userAPI.update(userId.value, formData.value);
        router.push('/management');
    } catch (error) {
        console.error('ユーザー更新エラー:', error);
        if (error.response?.data) {
            alert(
                error.response.data.error ||
                    error.response.data.detail ||
                    'ユーザーの更新に失敗しました',
            );
        }
    } finally {
        submitting.value = false;
    }
}

// マウント時にデータ取得
onMounted(() => {
    fetchUser();
});
</script>
