<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { handleApiError } = useApiError();

const loading = ref(true);
const user = ref({});
const allUsers = ref([]);

const userId = computed(() => route.params.id);

const breadcrumbs = computed(() => [
    { title: t('breadcrumbs.home'), to: routes.HOME, disabled: false },
    { title: t('breadcrumbs.admin'), to: routes.ADMIN, disabled: false },
    { title: t('breadcrumbs.users.list'), to: routes.USERS, disabled: false },
    { title: t('breadcrumbs.users.detail'), disabled: true },
]);

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

<template>
    <div>
        <Header
            :app-title="t('pages.users.detail.title')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container class="pa-4">
            <v-row justify="center">
                <v-col cols="12" sm="10" md="6">
                    <v-card elevation="2" v-if="!loading">
                        <v-card-text class="pa-6">
                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold"
                                    >ID</v-col
                                >
                                <v-col cols="8">{{ user.id }}</v-col>
                            </v-row>

                            <v-divider class="my-3" />

                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold">
                                    {{ t('form.fields.username') }}
                                </v-col>
                                <v-col cols="8">{{ user.username }}</v-col>
                            </v-row>

                            <v-divider class="my-3" />

                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold">
                                    {{ t('form.fields.employeeId') }}
                                </v-col>
                                <v-col cols="8">{{ user.employee_id }}</v-col>
                            </v-row>

                            <v-divider class="my-3" />

                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold">
                                    {{ t('form.fields.isAdmin') }}
                                </v-col>
                                <v-col cols="8">
                                    <v-icon
                                        :color="
                                            user.is_admin ? 'success' : 'grey'
                                        "
                                        :size="
                                            user.is_admin ? 'default' : 'small'
                                        "
                                    >
                                        {{
                                            user.is_admin
                                                ? ICONS.status.check
                                                : ICONS.status.minus
                                        }}
                                    </v-icon>
                                </v-col>
                            </v-row>

                            <v-divider class="my-3" />

                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold">
                                    {{ t('form.fields.isActive') }}
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

                            <v-divider class="my-3" />

                            <v-row class="mb-3">
                                <v-col cols="4" class="font-weight-bold">
                                    {{ t('form.fields.createdAt') }}
                                </v-col>
                                <v-col cols="8">{{
                                    formatDate(user.created_at)
                                }}</v-col>
                            </v-row>

                            <v-divider class="my-4" />

                            <div class="d-flex gap-2">
                                <v-btn
                                    color="primary"
                                    size="large"
                                    variant="outlined"
                                    :prepend-icon="ICONS.buttons.arrowForward"
                                    @click="goToUpdate"
                                >
                                    {{ t('buttons.users.detail.update') }}
                                </v-btn>

                                <v-spacer />

                                <v-btn
                                    color="error"
                                    size="large"
                                    variant="outlined"
                                    :prepend-icon="ICONS.buttons.arrowForward"
                                    @click="goToDelete"
                                    :disabled="isLastAdmin"
                                >
                                    {{ t('buttons.users.detail.delete') }}
                                </v-btn>

                                <v-spacer />

                                <v-btn
                                    variant="outlined"
                                    size="large"
                                    :prepend-icon="ICONS.buttons.arrowBack"
                                    @click="goBack"
                                >
                                    {{ t('buttons.back') }}
                                </v-btn>
                            </div>
                        </v-card-text>
                    </v-card>

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
