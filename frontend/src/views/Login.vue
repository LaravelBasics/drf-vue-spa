<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError'; // ⭐ 追加
import { useDesignSystem } from '@/composables/useDesignSystem';
import { routes } from '@/constants/routes';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { handleApiError, showInfo } = useApiError(); // ⭐ 通知統一
const { colors, getIcon, getSize } = useDesignSystem();

const employeeId = ref('');
const password = ref('');
const loading = ref(false);
const isVisible = ref(false);
const form = ref(null);

const employeeIdRules = createRules.loginEmployeeId();
const passwordRules = createRules.loginPassword();

onMounted(() => {
    setTimeout(() => {
        isVisible.value = true;
    }, 100);
});

async function onSubmit() {
    const { valid } = await form.value.validate();
    if (!valid) return;

    loading.value = true;

    try {
        // ⭐ auth.loginSession が成功/失敗を返すのか、
        //    例外を投げるのかで分岐する
        const result = await auth.loginSession(
            employeeId.value,
            password.value,
        );

        if (result.success) {
            // ⭐ 成功通知を表示
            showInfo('auth.loginSuccess', {}, 3000); // デフォルトの設定は5秒

            // ⭐ フェードアウトしてから遷移
            isVisible.value = false;
            setTimeout(async () => {
                const redirect = route.query.next || routes.HOME;
                await router.push(redirect);
            }, 300);
        } else {
            // ⭐ 失敗時はエラー通知
            handleApiError(
                new Error(result.message || 'ログインに失敗しました'),
                'auth.loginFailed',
            );
        }
    } catch (error) {
        // ⭐ 例外発生時もエラー通知
        handleApiError(error, 'auth.loginFailed');
    } finally {
        loading.value = false;
    }
}
</script>

<template>
    <!-- ⭐ フルスクリーン中央配置コンテナ -->
    <div class="login-page">
        <transition name="login-fade" appear>
            <div v-show="isVisible" class="login-center">
                <v-card rounded="lg" :elevation="12" class="login-card">
                    <v-toolbar
                        :color="colors.current.primary"
                        dark
                        flat
                        class="rounded-t-lg"
                    >
                        <div class="d-flex w-100 justify-center align-center">
                            <span class="text-h5 font-weight-bold text-white">
                                {{ t('auth.loginTitle') }}
                            </span>
                        </div>
                    </v-toolbar>

                    <v-card-text class="py-6 px-6">
                        <v-form @submit.prevent="onSubmit" ref="form">
                            <v-text-field
                                v-model="employeeId"
                                :label="
                                    t('form.placeholders.employeeId', {
                                        field: t('form.fields.employeeId'),
                                    })
                                "
                                :prepend-inner-icon="getIcon('form', 'user')"
                                variant="outlined"
                                class="mt-1 mb-2"
                                type="text"
                                inputmode="numeric"
                                :rules="employeeIdRules"
                            />
                            <v-text-field
                                v-model="password"
                                :label="
                                    t('form.placeholders.enterPassword', {
                                        field: t('form.fields.password'),
                                    })
                                "
                                type="password"
                                :prepend-inner-icon="
                                    getIcon('form', 'password')
                                "
                                variant="outlined"
                                class="mb-3"
                                :rules="passwordRules"
                            />

                            <v-btn
                                type="submit"
                                :loading="loading"
                                :color="colors.current.primary"
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
