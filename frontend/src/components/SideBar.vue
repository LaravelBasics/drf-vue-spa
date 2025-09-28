<template>
    <v-navigation-drawer app v-model="ui.drawer">
        <v-list>
            <v-list-item
                v-for="(item, i) in navItems"
                :key="i"
                :to="item.to"
                link
            >
                <template v-slot:prepend>
                    <v-icon>{{ item.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script setup>
import { useUiStore } from '@/stores/ui';
import { routes } from '@/constants/routes';
// import { useAuthStore } from '@/stores/auth'; // 👈 追加

const ui = useUiStore();
// const auth = useAuthStore(); // 👈 追加

const navItems = [
    { title: 'ホーム', icon: 'mdi-home', to: routes.HOME }, // ← HOME (大文字)
    {
        title: 'ダッシュボード',
        icon: 'mdi-view-dashboard',
        to: routes.DASHBOARD,
    },
    { title: 'プロフィール', icon: 'mdi-account', to: routes.PROFILE },
    { title: '設定', icon: 'mdi-cog', to: routes.SETTINGS },
];
</script>
