<script setup>
import { ref, onMounted, computed } from 'vue';
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

// ⭐ フィールド参照（フォーカス用）
const employeeIdField = ref(null);
const passwordField = ref(null);

const employeeIdRules = createRules.loginEmployeeId();
const passwordRules = createRules.loginPassword();

// テーマカラー
const primaryColor = computed(
    () =>
        theme.global.current.value?.colors?.primary ||
        THEME_CONFIG.colors.light.primary,
);

onMounted(() => {
    setTimeout(() => {
        isVisible.value = true;
        // ⭐ マウント後に最初のフィールドにフォーカス
        employeeIdField.value?.focus();
    }, 100);

    // ⭐ ログアウト後のクエリパラメータチェック
    if (route.query.logout === 'success') {
        // 「ログアウトしました」のメッセージ表示時間3秒
        showInfo('auth.logoutSuccess', {}, 3000);
        // URLをクリーンにする
        router.replace({ path: routes.LOGIN, query: {} });
    }
});

async function onSubmit() {
    const { valid, errors } = await form.value.validate();

    if (!valid) {
        // ⭐ バリデーションエラー時にフォーカス
        if (errors && errors.length > 0) {
            const firstErrorField = errors[0]?.id;
            if (firstErrorField?.includes('employee')) {
                employeeIdField.value?.focus();
            } else if (firstErrorField?.includes('password')) {
                passwordField.value?.focus();
            }
        }
        return;
    }

    // ⭐ 追加: 重複送信防止
    if (loading.value) return;

    loading.value = true;

    try {
        await auth.loginSession(employeeId.value, password.value);

        // ✅ ログイン成功
        showInfo('auth.loginSuccess', {}, 3000);

        // ⭐ フェードアウトしてから遷移
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
    <div class="login-page">
        <transition name="login-fade" appear>
            <div v-show="isVisible" class="login-center">
                <v-card rounded="lg" :elevation="12" class="login-card">
                    <v-toolbar :color="primaryColor" dark flat>
                        <div class="d-flex w-100 justify-center align-center">
                            <span class="text-h5 font-weight-bold text-white">
                                {{ t('auth.loginTitle') }}
                            </span>
                        </div>
                    </v-toolbar>

                    <v-card-text class="py-6 px-6">
                        <v-form @submit.prevent="onSubmit" ref="form">
                            <v-text-field
                                ref="employeeIdField"
                                v-model="employeeId"
                                :label="
                                    t('form.placeholders.employeeId', {
                                        field: t('form.fields.employeeId'),
                                    })
                                "
                                :prepend-inner-icon="ICONS.form.user"
                                variant="outlined"
                                class="mt-1 mb-2"
                                type="text"
                                inputmode="numeric"
                                :rules="employeeIdRules"
                                :hint="t('form.hint.testEmployeeId')"
                                persistent-hint
                            />
                            <v-text-field
                                ref="passwordField"
                                v-model="password"
                                :label="
                                    t('form.placeholders.enterPassword', {
                                        field: t('form.fields.password'),
                                    })
                                "
                                type="password"
                                :prepend-inner-icon="ICONS.form.password"
                                variant="outlined"
                                class="mb-3"
                                :rules="passwordRules"
                                :hint="t('form.hint.testPassword')"
                                persistent-hint
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
            </div>
        </transition>
    </div>
</template>

<style scoped>
.login-page {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 1000;
}

.login-center {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    max-width: 425px;
}

.login-card {
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.login-fade-enter-active,
.login-fade-leave-active {
    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.login-fade-enter-from {
    opacity: 0;
    transform: translate(-50%, -50%) translateY(20px) scale(0.9);
}

.login-fade-leave-to {
    opacity: 0;
    transform: translate(-50%, -50%) translateY(-20px) scale(1.1);
}
</style>
