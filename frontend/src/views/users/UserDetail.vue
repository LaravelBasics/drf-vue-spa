<template>
    <div>
        <Header
            :app-title="t('pages.users.detailTitle')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container class="pa-6">
            <v-row justify="center">
                <v-col cols="12" md="8" lg="6">
                    <v-card elevation="2" v-if="!loading">
                        <v-card-title class="text-h5 pa-6 bg-grey-lighten-4">
                            {{ t('pages.users.detailTitle2') }}
                        </v-card-title>

                        <v-card-text class="pa-6">
                            <!-- ユーザー情報表示 -->
                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
                                >
                                    ID:
                                </v-col>
                                <v-col cols="8">
                                    {{ user.id }}
                                </v-col>
                            </v-row>

                            <v-divider class="my-3"></v-divider>

                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
                                >
                                    {{ t('form.fields.username') }}:
                                </v-col>
                                <v-col cols="8">
                                    {{ user.username }}
                                </v-col>
                            </v-row>

                            <v-divider class="my-3"></v-divider>

                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
                                >
                                    {{ t('form.fields.employeeId') }}:
                                </v-col>
                                <v-col cols="8">
                                    {{ user.employee_id }}
                                </v-col>
                            </v-row>

                            <v-divider class="my-3"></v-divider>

                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
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

                            <v-divider class="my-3"></v-divider>

                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
                                >
                                    {{ t('form.fields.isActive') }}:
                                </v-col>
                                <v-col cols="8">
                                    <v-chip
                                        :color="
                                            user.is_active ? 'primary' : 'grey'
                                        "
                                        size="small"
                                    >
                                        {{
                                            user.is_active
                                                ? t('common.yes')
                                                : t('common.no')
                                        }}
                                    </v-chip>
                                </v-col>
                            </v-row>

                            <v-divider class="my-3"></v-divider>

                            <v-row class="mb-3">
                                <v-col
                                    cols="4"
                                    class="font-weight-bold text-grey-darken-1"
                                >
                                    {{ t('form.fields.createdAt') }}:
                                </v-col>
                                <v-col cols="8">
                                    {{ formatDate(user.created_at) }}
                                </v-col>
                            </v-row>

                            <v-divider class="my-4"></v-divider>

                            <!-- アクションボタン -->
                            <div class="d-flex gap-2">
                                <v-btn
                                    color="primary"
                                    size="large"
                                    :prepend-icon="ICONS.action.edit"
                                    @click="goToUpdate"
                                >
                                    {{ t('common.edit') }}
                                </v-btn>

                                <v-spacer></v-spacer>

                                <v-btn
                                    color="error"
                                    size="large"
                                    :prepend-icon="ICONS.action.delete"
                                    @click="goToDelete"
                                    :disabled="isLastAdmin"
                                >
                                    {{ t('common.delete') }}
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
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { useNotificationStore } from '@/stores/notification';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const notification = useNotificationStore();

const loading = ref(true);
const user = ref({});
const allUsers = ref([]);

const userId = computed(() => route.params.id);

const breadcrumbs = computed(() => [
    { title: t('nav.home'), to: routes.HOME, disabled: false },
    { title: t('pages.admin.title'), to: routes.ADMIN, disabled: false },
    { title: t('pages.users.title'), to: routes.USERS, disabled: false },
    { title: t('pages.users.detailTitle2'), disabled: true },
]);

// 最後の管理者かチェック
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
        console.error('ユーザー情報取得エラー:', error);
        notification.error(t('pages.users.fetchError'));
        router.push(routes.USERS);
    } finally {
        loading.value = false;
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
}

function goToUpdate() {
    router.push(routes.USER_UPDATE.replace(':id', userId.value));
}

function goToDelete() {
    router.push(routes.USER_DELETE.replace(':id', userId.value));
}

function goBack() {
    router.push(routes.USERS);
}

onMounted(() => {
    fetchUser();
});
</script>
