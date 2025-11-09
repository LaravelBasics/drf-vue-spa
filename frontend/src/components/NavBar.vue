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
const { handleApiError } = useApiError();

const loggingOut = ref(false);

const primaryColor = computed(
    () =>
        theme.global.current.value?.colors?.primary ||
        THEME_CONFIG.colors.light.primary,
);

async function handleLogout() {
    if (loggingOut.value) return;

    loggingOut.value = true;

    try {
        await auth.logout(false);
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
    <v-app-bar>
        <v-app-bar-nav-icon @click="ui.toggleRail" :icon="ICONS.nav.menu" />
        <v-toolbar-title>
            <div class="d-flex align-center h-100">
                <span
                    class="d-flex align-center"
                    role="button"
                    tabindex="0"
                    @click="goToHome"
                    @keydown.enter="goToHome"
                    @keydown.space.prevent="goToHome"
                >
                    <v-icon :size="ICON_SIZES.lg">
                        {{ ICONS.app.title }}
                    </v-icon>
                    <span>{{ t('app.tabTitle') }}</span>
                </span>
            </div>
        </v-toolbar-title>

        <v-spacer />

        <!-- ユーザーメニュー -->
        <v-menu location="bottom end">
            <template #activator="{ props }">
                <v-chip v-bind="props" :color="primaryColor" class="me-2">
                    <v-icon :size="ICON_SIZES.sm" class="me-2">
                        {{ ICONS.nav.profile }}
                    </v-icon>
                    <span>{{ auth.user?.display_name }}</span>
                </v-chip>
            </template>

            <!-- Vuetify 3.xのバグ対応：tabindex本来は不要、バグ対応で明示的指定が必要 -->
            <v-list density="compact" min-width="200">
                <v-list-item tabindex="-1">
                    <v-list-item-title class="text-caption">
                        {{ t('form.fields.employeeId') }}:
                        {{ auth.user?.employee_id }}
                    </v-list-item-title>
                </v-list-item>

                <v-divider />

                <v-list-item
                    tabindex="0"
                    :prepend-icon="ICONS.nav.settings"
                    :title="t('pages.settings.title')"
                    @click="goToSettings"
                    @keydown.enter="goToSettings"
                    @keydown.space.prevent="goToSettings"
                />

                <v-divider />

                <!-- ログアウト中はクリック無効化（disabled属性で自動制御） -->
                <v-list-item
                    :tabindex="loggingOut ? -1 : 0"
                    :prepend-icon="ICONS.nav.logout"
                    :title="t('auth.logout')"
                    :disabled="loggingOut"
                    @click="handleLogout"
                    @keydown.enter="handleLogout"
                    @keydown.space.prevent="handleLogout"
                >
                    <template #append>
                        <v-progress-circular
                            v-if="loggingOut"
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

<style scoped>
:deep(.v-list-item[disabled]) {
    cursor: not-allowed;
}
</style>
