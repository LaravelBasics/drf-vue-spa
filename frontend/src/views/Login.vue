<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '@/stores/auth';
import { useValidation } from '@/composables/useValidation';
import { useDesignSystem } from '@/composables/useDesignSystem';
import { messages } from '@/constants/messages';

const auth = useAuthStore();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { createRules } = useValidation();
const { colors, getIcon, getSize } = useDesignSystem();

const username = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);
const isVisible = ref(false); // ⭐ フェードイン制御
const form = ref(null); // ⭐ これを追加！フォームを参照するための ref を定義します ⭐

// ⭐ バリデーションルールを分離
const nameRules = createRules.loginUsername();
const passwordRules = createRules.loginPassword();

// ⭐ マウント時にスムーズフェードイン
onMounted(() => {
    // 少し遅延してからフェードイン
    setTimeout(() => {
        isVisible.value = true;
    }, 100);
});

async function onSubmit() {
    // onSubmit 関数でこれだけ書けばOK！
    const { valid } = await form.value.validate();
    if (!valid) return; // 有効でなければ即座に終了
    error.value = '';
    loading.value = true;

    const result = await auth.loginSession(username.value, password.value);
    loading.value = false;

    if (result.success) {
        // ⭐ ログイン成功時はフェードアウトしてから遷移
        isVisible.value = false;

        setTimeout(async () => {
            const redirect = route.query.next || '/';
            await router.push(redirect);
        }, 300); // フェードアウト時間と合わせる
    } else {
        // ⭐ エラーメッセージも統一管理
        error.value = messages.auth.invalidCredentials;
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
                                v-model="username"
                                :label="
                                    t('form.placeholders.enterUsername', {
                                        field: t('form.fields.username'),
                                    })
                                "
                                :prepend-inner-icon="getIcon('form', 'user')"
                                variant="outlined"
                                class="mt-1 mb-2"
                                :rules="nameRules"
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

                    <!-- ⭐ エラーメッセージもスムーズに -->
                    <transition name="error-slide">
                        <v-card-actions v-if="error" class="pt-0 px-6 pb-6">
                            <v-alert
                                :icon="getIcon('status', 'error')"
                                type="error"
                                variant="tonal"
                                class="w-100 text-center"
                                density="compact"
                            >
                                {{ error }}
                            </v-alert>
                        </v-card-actions>
                    </transition>
                </v-card>
            </div>
        </transition>
    </div>
</template>

<style scoped>
/* ⭐ フルスクリーン背景 */
.login-page {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 1000;
}

/* ⭐ 完全中央配置 */
.login-center {
    position: absolute;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 100%;
    max-width: 425px;
}

/* ⭐ カードスタイル */
.login-card {
    /* backdrop-filter: blur(10px); */
    background-color: rgba(255, 255, 255, 0.95);
    border: 1px solid rgba(255, 255, 255, 0.2);
}

/* ⭐ ログイン画面のフェード遷移 */
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

/* ⭐ エラーメッセージのスライド遷移 */
.error-slide-enter-active,
.error-slide-leave-active {
    transition: all 0.3s ease-out;
}

.error-slide-enter-from {
    opacity: 0;
    transform: translateY(-10px);
    max-height: 0;
}

.error-slide-leave-to {
    opacity: 0;
    transform: translateY(-10px);
    max-height: 0;
}
</style>
