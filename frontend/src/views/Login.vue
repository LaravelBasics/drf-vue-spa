<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useTheme } from 'vuetify';
import { useAuthStore } from '@/stores/auth';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { THEME_CONFIG } from '@/constants/theme';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const theme = useTheme();
const { createRules } = useValidation();
const { showInfo, handleApiError } = useApiError();

const employeeId = ref('');
const password = ref('');
const loading = ref(false);
const isVisible = ref(false);
const form = ref(null);

const employeeIdRules = createRules.loginEmployeeId();
const passwordRules = createRules.loginPassword();

const primaryColor = computed(
    () =>
        theme.global.current.value?.colors?.primary ||
        THEME_CONFIG.colors.light.primary,
);

onMounted(async () => {
    await nextTick();
    isVisible.value = true;

    if (route.query.logout === 'success') {
        showInfo('auth.logoutSuccess', {}, 3000);
        router.replace({ path: routes.LOGIN, query: {} });
    }
});

async function onSubmit() {
    if (loading.value) return;

    const { valid } = await form.value.validate();

    if (!valid) return;

    loading.value = true;

    try {
        await auth.loginSession(employeeId.value, password.value);
        showInfo('auth.loginSuccess', {}, 3000);
        isVisible.value = false;

        setTimeout(async () => {
            const redirect = route.query.next || routes.HOME;
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
                        <v-toolbar :color="primaryColor" flat>
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
                                <v-text-field
                                    v-model="employeeId"
                                    :label="
                                        t('form.placeholders.employeeId', {
                                            field: t('form.fields.employeeId'),
                                        })
                                    "
                                    :prepend-inner-icon="ICONS.form.user"
                                    variant="outlined"
                                    inputmode="numeric"
                                    :rules="employeeIdRules"
                                    :hint="t('form.hint.testEmployeeId')"
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
                                    :color="primaryColor"
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
/* ==================== ログインページ全体のレイアウト ==================== */
.login-page {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
}

/* ==================== ログインカードのスタイル ==================== */
.login-card {
    /* 半透明の白背景（背景が透ける演出） */
    background-color: rgba(255, 255, 255, 0.95);
    /* 中央配置（v-colと組み合わせて使用） */
    margin: 0 auto;
}

/* ==================== フェードインアニメーション ==================== */
/* Material Design Easing を使用 */
.login-fade-enter-active,
.login-fade-leave-active {
    /* 0.4秒のスムーズなトランジション（Material Design推奨） */
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

/* 登場時: 下から上にフェードイン + 縮小から通常サイズ */
.login-fade-enter-from {
    opacity: 0;
    transform: translateY(20px) scale(0.9);
}

/* 退場時: 上に移動しながらフェードアウト + 拡大 */
.login-fade-leave-to {
    opacity: 0;
    transform: translateY(-20px) scale(1.1);
}
</style>
