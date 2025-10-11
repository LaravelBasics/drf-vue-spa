<template>
    <div>
        <Header
            :app-title="t('pages.users.deleteTitle')"
            :breadcrumbs="breadcrumbs"
        ></Header>

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="10" md="6">
                    <v-card class="elevation-2">
                        <!-- <v-card-title class="text-h5 pa-6 bg-error text-white">
                            {{ t('pages.users.deleteTitle2') }}
                        </v-card-title> -->

                        <v-card-text class="pa-6" v-if="!loading">
                            <!-- 警告メッセージ -->
                            <v-alert
                                type="warning"
                                variant="tonal"
                                class="mb-6"
                            >
                                {{ t('pages.userDelete.warningMessage') }}
                            </v-alert>

                            <!-- ユーザー情報表示 -->
                            <v-card variant="outlined" class="mb-4">
                                <v-card-text>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            ID:
                                        </v-col>
                                        <v-col cols="8">{{ user.id }}</v-col>
                                    </v-row>
                                    <v-divider class="my-2"></v-divider>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            {{ t('form.fields.username') }}:
                                        </v-col>
                                        <v-col cols="8">{{
                                            user.username
                                        }}</v-col>
                                    </v-row>
                                    <v-divider class="my-2"></v-divider>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            {{ t('form.fields.employeeId') }}:
                                        </v-col>
                                        <v-col cols="8">{{
                                            user.employee_id
                                        }}</v-col>
                                    </v-row>
                                    <v-divider class="my-2"></v-divider>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            {{ t('form.fields.isAdmin') }}:
                                        </v-col>
                                        <v-col cols="8">
                                            <v-chip
                                                :color="
                                                    user.is_admin
                                                        ? 'success'
                                                        : 'default'
                                                "
                                                size="small"
                                            >
                                                {{
                                                    user.is_admin
                                                        ? t('common.yes')
                                                        : t('common.no')
                                                }}
                                            </v-chip>
                                        </v-col>
                                    </v-row>
                                </v-card-text>
                            </v-card>

                            <!-- 管理者最後の1人の場合の警告 -->
                            <v-alert
                                v-if="isLastAdmin"
                                type="error"
                                variant="tonal"
                                class="mb-4"
                            >
                                {{ t('pages.userDelete.lastAdminError') }}
                            </v-alert>

                            <v-divider class="my-4" />

                            <!-- ボタン -->
                            <div class="d-flex gap-2">
                                <!-- 削除ボタン: モーダルを開く -->
                                <v-btn
                                    color="error"
                                    size="large"
                                    variant="outlined"
                                    :disabled="isLastAdmin"
                                    @click="showConfirmDialog = true"
                                >
                                    <v-icon class="me-2">delete</v-icon>
                                    {{ t('common.delete') }}
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

        <!-- 削除確認モーダル -->
        <ConfirmDialog
            v-model="showConfirmDialog"
            :title="t('pages.userDelete.confirmTitle')"
            :message="
                t('pages.userDelete.confirmMessage', {
                    employee_id: user.employee_id,
                })
            "
            :confirm-text="t('common.delete')"
            :cancel-text="t('common.cancel')"
            confirm-color="error"
            icon="info"
            confirm-icon="delete"
            :loading="deleting"
            @confirm="deleteUser"
        >
            <!-- 追加情報（オプション） -->
            <template #content>
                <v-alert type="error" variant="tonal" class="mt-4">
                    この操作は取り消せません
                </v-alert>
            </template>
        </ConfirmDialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { handleApiError, showSuccess } = useApiError();

const loading = ref(true);
const deleting = ref(false);
const user = ref({});
const allUsers = ref([]);
const showConfirmDialog = ref(false);

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('nav.home'),
        to: routes.HOME,
        disabled: false,
    },
    {
        title: t('pages.admin.title'),
        to: routes.ADMIN,
        disabled: false,
    },
    {
        title: t('pages.users.title'),
        to: routes.USERS,
        disabled: false,
    },
    { title: t('pages.users.detailTitle2'), disabled: true },
    {
        title: t('pages.users.deleteTitle2'),
        disabled: true,
    },
]);

const userId = computed(() => route.params.id);

const isLastAdmin = computed(() => {
    if (!user.value.is_admin) return false;
    const adminCount = allUsers.value.filter(
        (u) => u.is_admin && u.is_active,
    ).length;
    return adminCount === 1;
});

async function fetchUser() {
    loading.value = true;
    try {
        const [userResponse, usersResponse] = await Promise.all([
            usersAPI.get(userId.value),
            usersAPI.list(),
        ]);
        user.value = userResponse.data;
        allUsers.value = usersResponse.data.results || usersResponse.data;
    } catch (error) {
        handleApiError(error, 'pages.users.fetchError');
        router.push(routes.USERS);
    } finally {
        loading.value = false;
    }
}

async function deleteUser() {
    if (isLastAdmin.value) return;

    deleting.value = true;
    try {
        await usersAPI.delete(userId.value);

        showSuccess('pages.users.deleteSuccess', {
            username: user.value.username,
        });

        showConfirmDialog.value = false;
        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error, 'pages.users.deleteError');
    } finally {
        deleting.value = false;
    }
}

onMounted(() => {
    fetchUser();
});
</script>
