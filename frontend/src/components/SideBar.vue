<template>
    <v-navigation-drawer
        v-model="ui.drawer"
        :rail="ui.rail"
        permanent
        app
        @click="handleDrawerClick"
    >
        <!-- ナビゲーションアイテム -->
        <v-list nav>
            <v-list-item
                v-for="(item, i) in navItems"
                :key="i"
                :to="item.to"
                :value="item.title"
                link
            >
                <template v-slot:prepend>
                    <v-icon :size="getSize('md')">{{ item.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>

        <!-- 言語切り替えボタン（下部） -->
        <template v-slot:append>
            <div class="pa-2">
                <v-btn
                    @click.stop="toggleLanguage"
                    variant="outlined"
                    size="small"
                    block
                >
                    <v-icon class="me-2" v-if="!ui.rail">
                        {{ languageIcon }}
                    </v-icon>
                    <v-icon v-else>
                        {{ languageIcon }}
                    </v-icon>
                    <span v-if="!ui.rail">
                        {{ languageDisplayText }}
                    </span>
                </v-btn>
            </div>
        </template>
    </v-navigation-drawer>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUiStore } from '@/stores/ui';
import { useDesignSystem } from '@/composables/useDesignSystem';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const { t, locale } = useI18n();
const ui = useUiStore();
const { getIcon, getSize } = useDesignSystem();

const currentLocale = computed(() => locale.value);

const navItems = computed(() => [
    { title: t('nav.home'), icon: 'mdi-home', to: routes.HOME },
    {
        title: t('nav.dashboard'),
        icon: 'mdi-view-dashboard',
        to: routes.DASHBOARD,
    },
    { title: t('nav.profile'), icon: 'mdi-account', to: routes.PROFILE },
    { title: t('nav.settings'), icon: 'mdi-cog', to: routes.SETTINGS },
    {
        title: t('nav.management'),
        icon: ICONS.nav.management,
        to: routes.ADMIN,
    },
]);

const languageDisplayText = computed(() => {
    return locale.value === 'ja' ? '日本語' : 'English';
});

const languageIcon = computed(() => {
    return 'mdi-web';
});

// ⭐ レールモード時のクリックでフル表示に切り替え
const handleDrawerClick = () => {
    if (ui.rail) {
        ui.rail = false;
    }
};

function toggleLanguage() {
    locale.value = locale.value === 'ja' ? 'en' : 'ja';
}
</script>
