<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useTheme } from 'vuetify';
import { useUiStore } from '@/stores/ui';
import { useAuthStore } from '@/stores/auth';
import { useApiError } from '@/composables/useApiError';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES, THEME_CONFIG } from '@/constants/theme';

const router = useRouter();
const { t } = useI18n();
const ui = useUiStore();
const auth = useAuthStore();
const theme = useTheme();
const { showInfo, handleApiError } = useApiError();

// ⭐ ログアウト中の状態管理
const loggingOut = ref(false);

const displayName = computed(() => {
    return auth.user?.username || auth.user?.employee_id || 'ゲスト';
});

const primaryColor = computed(
    () =>
        theme.global.current.value?.colors?.primary ||
        THEME_CONFIG.colors.light.primary,
);

// ⭐ ログアウト関数（クエリパラメータで通知を伝える）
async function handleLogout() {
    // 重複実行防止
    if (loggingOut.value) return;

    loggingOut.value = true;

    try {
        // ログアウトAPI呼び出し（redirect=falseで自動リダイレクトを無効化）
        await auth.logout(false);

        // ✅ クエリパラメータ付きでログイン画面へ遷移
        router.push({
            path: routes.LOGIN,
            query: { logout: 'success' },
        });
    } catch (error) {
        handleApiError(error);
    } finally {
        loggingOut.value = false;
    }
}

function goToSettings() {
    router.push(routes.SETTINGS);
}

function goToHome() {
    router.push(routes.HOME);
}
</script>

<template>
    <v-app-bar app>
        <v-app-bar-nav-icon @click="ui.toggleRail">
            <v-icon>{{ ICONS.nav.menu }}</v-icon>
        </v-app-bar-nav-icon>

        <v-toolbar-title>
            <div class="d-flex align-center" style="height: 100%">
                <span
                    class="d-flex align-center cursor-pointer"
                    @click="goToHome"
                >
                    <v-icon :size="ICON_SIZES.lg">
                        {{ ICONS.app.title }}
                    </v-icon>
                    <span>{{ t('app.tabTitle') }}</span>
                </span>
            </div>
        </v-toolbar-title>

        <v-spacer />

        <v-menu offset-y location="bottom end">
            <template v-slot:activator="{ props }">
                <v-chip v-bind="props" :color="primaryColor" class="me-2">
                    <v-icon :size="ICON_SIZES.sm" class="me-2">
                        {{ ICONS.nav.profile }}
                    </v-icon>
                    <span>{{ displayName }}</span>
                </v-chip>
            </template>

            <v-list density="compact" min-width="200">
                <v-list-item>
                    <v-list-item-title class="text-caption">
                        {{ t('form.fields.employeeId') }}:
                        {{ auth.user?.employee_id }}
                    </v-list-item-title>
                </v-list-item>

                <v-divider />

                <v-list-item
                    :prepend-icon="ICONS.nav.settings"
                    :title="t('pages.settings.title')"
                    @click="goToSettings"
                />

                <v-divider />

                <v-list-item
                    :prepend-icon="ICONS.nav.logout"
                    :title="t('auth.logout')"
                    :disabled="loggingOut"
                    @click="handleLogout"
                >
                    <!-- ⭐ ログアウト中はローディング表示 -->
                    <template v-slot:append v-if="loggingOut">
                        <v-progress-circular
                            indeterminate
                            size="20"
                            width="2"
                        />
                    </template>
                </v-list-item>
            </v-list>
        </v-menu>
    </v-app-bar>
</template>
