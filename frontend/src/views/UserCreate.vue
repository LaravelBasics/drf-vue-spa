<template>
    <Header
        :app-title="t('pages.userCreate.title')"
        :breadcrumbs="breadcrumbs"
    ></Header>

    <v-container class="pa-6">
        <v-row justify="center">
            <v-col cols="12" md="8" lg="6">
                <v-card class="elevation-2">
                    <v-card-title class="text-h5 pa-6">
                        {{ t('pages.userCreate.title') }}
                    </v-card-title>

                    <v-card-text class="pa-6">
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

                            <div class="d-flex gap-2">
                                <v-btn
                                    type="submit"
                                    color="primary"
                                    size="large"
                                    :loading="loading"
                                >
                                    {{ t('common.create') }}
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
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import Header from '@/components/Header.vue';
import { userAPI } from '@/api/user';

const router = useRouter();
const { t } = useI18n();
const { createRules } = useValidation();

const loading = ref(false);
const form = ref(null);

// フォームデータ
const formData = ref({
    username: '',
    employee_id: '',
    is_admin: false,
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
        to: '/users',
        disabled: false,
    },
    {
        title: t('pages.userCreate.title'),
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

// メソッド
async function submitForm() {
    const { valid } = await form.value.validate();
    if (!valid) return;

    loading.value = true;
    try {
        await userAPI.create(formData.value);
        router.push('/users');
    } catch (error) {
        console.error('ユーザー作成エラー:', error);
    } finally {
        loading.value = false;
    }
}
</script>
