<template>
    <v-app-bar app>
        <v-app-bar-nav-icon @click="ui.drawer = !ui.drawer">
        </v-app-bar-nav-icon>
        <span class="pl-5">テスト環境</span>
        <v-toolbar-title class="ml-1">
            <!-- <v-icon>mdi-github</v-icon> -->
        </v-toolbar-title>

        <v-chip color="primary" class="me-3">
            <v-icon size="20" class="me-2">mdi-account</v-icon>
            <span>{{ auth.user.username }}</span>
        </v-chip>

        <v-chip @click="handleLogout" class="mr-2">
            <v-icon size="20" class="me-2">mdi-power</v-icon>
            <span>ログアウト</span>
        </v-chip>
    </v-app-bar>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useUiStore } from '@/stores/ui';
import { useAuthStore } from '@/stores/auth';

const ui = useUiStore();
const auth = useAuthStore();
const router = useRouter();

async function handleLogout() {
    await auth.logout();
}
</script>
