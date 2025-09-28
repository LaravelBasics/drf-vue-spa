<template>
    <v-app-bar app>
        <v-app-bar-nav-icon @click="ui.drawer = !ui.drawer">
            <v-icon>{{ getIcon('nav', 'menu') }}</v-icon>
        </v-app-bar-nav-icon>

        <v-toolbar-title>
            <v-icon :size="getSize('lg')">mdi-github</v-icon>
            <span>{{ t('app.title') }}</span>
        </v-toolbar-title>

        <v-chip :color="colors.current.primary" class="me-3">
            <v-icon :size="getSize('sm')" class="me-2">
                {{ getIcon('form', 'user') }}
            </v-icon>
            <span>{{ auth.user.username }}</span>
        </v-chip>

        <v-chip
            @click="handleLogout"
            :color="colors.current.secondary"
            class="mr-2"
        >
            <v-icon :size="getSize('sm')" class="me-2">
                {{ getIcon('nav', 'logout') }}
            </v-icon>
            <span>{{ t('auth.logout') }}</span>
        </v-chip>
    </v-app-bar>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useUiStore } from '@/stores/ui';
import { useAuthStore } from '@/stores/auth';
import { useDesignSystem } from '@/composables/useDesignSystem';

const { t } = useI18n();
const ui = useUiStore();
const auth = useAuthStore();
const router = useRouter();
const { colors, getIcon, getSize } = useDesignSystem();

async function handleLogout() {
    await auth.logout();
}
</script>
