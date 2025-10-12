<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { handleApiError, showDeleteSuccess } = useApiError();

const loading = ref(true);
const deleting = ref(false);
const user = ref({});
const allUsers = ref([]);
const showConfirmDialog = ref(false);

const breadcrumbs = computed(() => [
    { title: t('breadcrumbs.home'), to: routes.HOME, disabled: false },
    { title: t('breadcrumbs.admin'), to: routes.ADMIN, disabled: false },
    { title: t('breadcrumbs.users.list'), to: routes.USERS, disabled: false },
    { title: t('breadcrumbs.users.detail'), disabled: true },
    { title: t('breadcrumbs.users.delete'), disabled: true },
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
        handleApiError(error, 'pages.users.detail.error');
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
        showDeleteSuccess('pages.users.delete.success', {
            username: user.value.username,
        });
        showConfirmDialog.value = false;
        router.replace(routes.USERS);
    } catch (error) {
        handleApiError(error, 'pages.users.delete.error');
    } finally {
        deleting.value = false;
    }
}

onMounted(() => {
    fetchUser();
});
</script>

<template>
    <div>
        <Header
            :app-title="t('pages.users.delete.title')"
            :breadcrumbs="breadcrumbs"
        ></Header>

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="11" md="7">
                    <v-card class="elevation-2">
                        <v-card-text class="pa-6" v-if="!loading">
                            <v-alert
                                type="warning"
                                variant="tonal"
                                class="mb-6"
                            >
                                {{ t('pages.users.delete.warning') }}
                            </v-alert>

                            <v-card variant="outlined" class="mb-4">
                                <v-card-text>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            {{ t('form.fields.id') }}
                                        </v-col>
                                        <v-col cols="8">{{ user.id }}</v-col>
                                    </v-row>
                                    <v-divider class="my-2"></v-divider>
                                    <v-row>
                                        <v-col
                                            cols="4"
                                            class="font-weight-bold"
                                        >
                                            {{ t('form.fields.username') }}
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
                                            {{ t('form.fields.employeeId') }}
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
                                            {{ t('form.fields.isAdmin') }}
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

                            <v-alert
                                v-if="isLastAdmin"
                                type="error"
                                variant="tonal"
                                class="mb-4"
                            >
                                {{ t('pages.users.delete.lastAdminError') }}
                            </v-alert>

                            <v-divider class="my-4" />

                            <div class="d-flex gap-2">
                                <v-btn
                                    color="error"
                                    size="large"
                                    variant="outlined"
                                    :disabled="isLastAdmin"
                                    @click="showConfirmDialog = true"
                                    :prepend-icon="ICONS.status.info"
                                >
                                    {{ t('buttons.confirmDelete') }}
                                </v-btn>

                                <v-spacer></v-spacer>

                                <v-btn
                                    variant="outlined"
                                    size="large"
                                    :prepend-icon="ICONS.buttons.arrowBack"
                                    @click="router.back()"
                                >
                                    {{ t('buttons.back') }}
                                </v-btn>
                            </div>
                        </v-card-text>

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

        <ConfirmDialog
            v-model="showConfirmDialog"
            :title="t('modal.deleteConfirm.warning')"
            :message="
                t('modal.deleteConfirm.message', { username: user.username })
            "
            :confirm-text="t('buttons.delete')"
            :cancel-text="t('buttons.cancel')"
            confirm-color="error"
            :icon="ICONS.status.info"
            :confirm-icon="ICONS.buttons.delete"
            :loading="deleting"
            @confirm="deleteUser"
        >
            <!-- 追加情報（オプション） -->
            <!-- <template #content>
                <v-alert type="error" variant="tonal" class="mt-4">
                    この操作は取り消せません
                </v-alert>
            </template> -->
        </ConfirmDialog>
    </div>
</template>
