<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import { ROUTE_NAMES } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import api from '@/plugins/axios';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { showInfo, handleApiError } = useApiError();

const groupId = ref('');
const userId = ref('');
const password = ref('');
const loading = ref(false);
const loadingGroups = ref(false);
const isVisible = ref(false);
const form = ref(null);
const groups = ref([]);

const groupIdRules = [(v) => !!v || t('form.validation.required')];
const userIdRules = createRules.loginEmployeeId(); // 既存のルールを流用可能
const passwordRules = createRules.loginPassword();

onMounted(async () => {
    await nextTick();
    isVisible.value = true;

    // グループ一覧を取得
    await fetchGroups();

    if (route.query.logout === 'success') {
        showInfo('auth.logoutSuccess', {}, 3000);
        router.replace({ name: ROUTE_NAMES.LOGIN, query: {} });
    }
});

async function fetchGroups() {
    loadingGroups.value = true;
    try {
        const response = await api.get('auth/groups/');
        groups.value = response.data;
    } catch (error) {
        handleApiError(error);
        groups.value = [];
    } finally {
        loadingGroups.value = false;
    }
}

async function onSubmit() {
    if (loading.value) return;

    const { valid } = await form.value.validate();

    if (!valid) return;

    loading.value = true;

    try {
        await auth.loginSession(groupId.value, userId.value, password.value);
        showInfo('auth.loginSuccess', {}, 3000);
        isVisible.value = false;

        setTimeout(async () => {
            const redirect = route.query.next || ROUTE_NAMES.HOME;
            await router.push(redirect);
        }, 150);
    } catch (error) {
        handleApiError(error);
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <v-container fluid class="fill-height login-page">
        <v-row align="center" justify="center">
            <v-col cols="12" sm="10" md="6" lg="5" xl="4">
                <transition name="login-fade" appear>
                    <v-card
                        v-show="isVisible"
                        rounded="lg"
                        :elevation="12"
                        class="login-card"
                        max-width="480"
                    >
                        <v-toolbar color="primary" flat>
                            <div
                                class="d-flex w-100 justify-center align-center"
                            >
                                <span class="text-h5 font-weight-bold">
                                    {{ t('auth.loginTitle') }}
                                </span>
                            </div>
                        </v-toolbar>

                        <v-card-text class="pa-6">
                            <v-form
                                @submit.prevent="onSubmit"
                                ref="form"
                                class="d-flex flex-column ga-4"
                            >
                                <!-- ✅ グループ選択プルダウン（新規追加） -->
                                <v-select
                                    v-model="groupId"
                                    :items="groups"
                                    item-title="group_name"
                                    item-value="group_id"
                                    :label="t('form.fields.group')"
                                    :prepend-inner-icon="ICONS.form.group"
                                    variant="outlined"
                                    :rules="groupIdRules"
                                    :loading="loadingGroups"
                                    :disabled="loading || loadingGroups"
                                    :hint="
                                        t('form.hint.selectGroup', {
                                            default: '所属するグループを選択',
                                        })
                                    "
                                    persistent-hint
                                />

                                <v-text-field
                                    v-model="userId"
                                    :label="
                                        t('form.placeholders.userId', {
                                            field: t('form.fields.userId'),
                                            default: 'ユーザーIDを入力',
                                        })
                                    "
                                    :prepend-inner-icon="ICONS.form.user"
                                    variant="outlined"
                                    inputmode="text"
                                    :rules="userIdRules"
                                    :hint="
                                        t('form.hint.testUserId', {
                                            default: 'テストID: user001',
                                        })
                                    "
                                    persistent-hint
                                    :disabled="loading"
                                />

                                <v-text-field
                                    v-model="password"
                                    :label="
                                        t('form.placeholders.enterPassword', {
                                            field: t('form.fields.password'),
                                        })
                                    "
                                    type="password"
                                    :prepend-inner-icon="ICONS.form.password"
                                    variant="outlined"
                                    :rules="passwordRules"
                                    :hint="t('form.hint.testPassword')"
                                    persistent-hint
                                    :disabled="loading"
                                />

                                <v-btn
                                    type="submit"
                                    :loading="loading"
                                    color="primary"
                                    block
                                    size="large"
                                    rounded
                                    class="text-none"
                                >
                                    {{ t('auth.login') }}
                                </v-btn>
                            </v-form>
                        </v-card-text>
                    </v-card>
                </transition>
            </v-col>
        </v-row>
    </v-container>
</template>

<style scoped>
.login-page {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
}

.login-card {
    background-color: rgba(255, 255, 255, 0.95);
    margin: 0 auto;
}

.login-fade-enter-active,
.login-fade-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.login-fade-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
}

.login-fade-leave-to {
    opacity: 0;
    transform: translateY(-20px) scale(1.1);
}
</style>
