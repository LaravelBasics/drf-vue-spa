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
                            {{ t('pages.users.updateTitle') }}
                        </v-card-title>

                        <v-card-text class="pa-6">
                            <v-form ref="form" @submit.prevent="submitForm">
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

                                <v-divider class="my-4" />

                                <div class="d-flex gap-2">
                                    <v-btn
                                        type="submit"
                                        color="primary"
                                        size="large"
                                        :loading="submitting"
                                        :prepend-icon="ICONS.action.save"
                                    >
                                        {{ t('common.save') }}
                                    </v-btn>

                                    <v-spacer></v-spacer>

                                    <v-btn
                                        variant="outlined"
                                        size="large"
                                        prepend-icon="arrow_back"
                                        @click="router.back()"
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
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const notification = useNotificationStore();

const loading = ref(true);
const submitting = ref(false);
const form = ref(null);

const formData = ref({
    username: '',
    employee_id: '',
    is_admin: false,
    is_active: true,
});

const breadcrumbs = computed(() => [
    { title: t('nav.home'), to: routes.HOME, disabled: false },
    { title: t('pages.admin.title'), to: routes.ADMIN, disabled: false },
    { title: t('pages.users.title'), to: routes.USERS, disabled: false },
    { title: t('pages.users.updateTitle'), disabled: true },
]);

const usernameRules = createRules.username();
const employeeIdRules = [
    (v) =>
        !!v ||
        t('form.validation.required', { field: t('form.fields.employeeId') }),
    (v) => /^\d{1,10}$/.test(v) || t('form.validation.employeeIdFormat'),
];

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
        };
    } catch (error) {
        console.error('ユーザー情報取得エラー:', error);
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
        await usersAPI.update(userId.value, formData.value);
        // ⭐ 成功通知
        notification.success(
            t('pages.users.updateSuccess', {
                username: formData.value.username,
            }),
        );
        router.replace(routes.USERS);
    } catch (error) {
        console.error('ユーザー更新エラー:', error);
        // ⭐ エラー通知
        const errorMessage =
            error.response?.data?.error ||
            error.response?.data?.detail ||
            t('pages.users.updateError');

        notification.error(errorMessage);
    } finally {
        submitting.value = false;
    }
}

onMounted(() => {
    fetchUser();
});
</script>
