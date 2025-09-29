<template>
    <Header
        :app-title="t('pages.userDelete.title')"
        :breadcrumbs="breadcrumbs"
    ></Header>

    <v-container class="pa-6">
        <v-row justify="center">
            <v-col cols="12" md="8" lg="6">
                <v-card class="elevation-2">
                    <v-card-title class="text-h5 pa-6 bg-error text-white">
                        {{ t('pages.userDelete.title') }}
                    </v-card-title>

                    <v-card-text class="pa-6" v-if="!loading">
                        <!-- 警告メッセージ -->
                        <v-alert
                            type="warning"
                            variant="tonal"
                            class="mb-6"
                            icon="mdi-alert"
                        >
                            {{ t('pages.userDelete.warningMessage') }}
                        </v-alert>

                        <!-- ユーザー情報表示 -->
                        <v-card variant="outlined" class="mb-4">
                            <v-card-text>
                                <v-row>
                                    <v-col cols="4" class="font-weight-bold">
                                        ID:
                                    </v-col>
                                    <v-col cols="8">{{ user.id }}</v-col>
                                </v-row>
                                <v-divider class="my-2"></v-divider>
                                <v-row>
                                    <v-col cols="4" class="font-weight-bold">
                                        {{ t('form.fields.username') }}:
                                    </v-col>
                                    <v-col cols="8">{{ user.username }}</v-col>
                                </v-row>
                                <v-divider class="my-2"></v-divider>
                                <v-row>
                                    <v-col cols="4" class="font-weight-bold">
                                        {{ t('form.fields.employeeId') }}:
                                    </v-col>
                                    <v-col cols="8">{{
                                        user.employee_id
                                    }}</v-col>
                                </v-row>
                                <v-divider class="my-2"></v-divider>
                                <v-row>
                                    <v-col cols="4" class="font-weight-bold">
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
                            icon="mdi-alert-circle"
                        >
                            {{ t('pages.userDelete.lastAdminError') }}
                        </v-alert>

                        <!-- 削除確認メッセージ -->
                        <p class="text-h6 mb-4 text-center">
                            {{
                                t('pages.userDelete.confirmMessage', {
                                    username: user.username,
                                })
                            }}
                        </p>

                        <!-- ボタン -->
                        <div class="d-flex gap-2">
                            <v-btn
                                color="error"
                                size="large"
                                :loading="deleting"
                                :disabled="isLastAdmin"
                                @click="deleteUser"
                            >
                                <v-icon class="me-2">mdi-delete</v-icon>
                                {{ t('common.delete') }}
                            </v-btn>

                            <v-btn
                                variant="outlined"
                                size="large"
                                @click="router.back()"
                            >
                                {{ t('common.cancel') }}
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { userAPI } from '@/api/user';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();

const loading = ref(true);
const deleting = ref(false);
const user = ref({});
const allUsers = ref([]);

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
        title: t('pages.userDelete.title'),
        disabled: true,
    },
]);

// ユーザーIDを取得
const userId = computed(() => route.params.id);

// 最後の管理者かどうかをチェック
const isLastAdmin = computed(() => {
    if (!user.value.is_admin) return false;
    const adminCount = allUsers.value.filter(
        (u) => u.is_admin && u.is_active,
    ).length;
    return adminCount === 1;
});

// ユーザー情報を取得
async function fetchUser() {
    loading.value = true;
    try {
        const [userResponse, usersResponse] = await Promise.all([
            userAPI.get(userId.value),
            userAPI.list(),
        ]);
        user.value = userResponse.data;
        allUsers.value = usersResponse.data;
    } catch (error) {
        console.error('ユーザー情報取得エラー:', error);
        router.push('/management');
    } finally {
        loading.value = false;
    }
}

// ユーザー削除
async function deleteUser() {
    if (isLastAdmin.value) return;

    deleting.value = true;
    try {
        await userAPI.delete(userId.value);
        router.push('/management');
    } catch (error) {
        console.error('ユーザー削除エラー:', error);
        if (error.response?.data) {
            alert(
                error.response.data.error ||
                    error.response.data.detail ||
                    'ユーザーの削除に失敗しました',
            );
        }
    } finally {
        deleting.value = false;
    }
}

// マウント時にデータ取得
onMounted(() => {
    fetchUser();
});
</script>
