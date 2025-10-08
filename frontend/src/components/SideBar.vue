<template>
    <v-navigation-drawer
        v-model="ui.drawer"
        :rail="ui.isDesktop && ui.rail"
        :permanent="ui.isDesktop"
        :temporary="!ui.isDesktop"
        app
    >
        <!-- ナビゲーションアイテム -->
        <v-list nav>
            <v-list-item
                v-for="(item, i) in filteredNavItems"
                :key="i"
                :to="item.to"
                :value="item.title"
                link
                @click="handleNavItemClick"
                color="grey-darken-2"
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
                    <!-- ⭐ モバイル時はテキストも表示 -->
                    <template v-if="!ui.isDesktop">
                        <v-icon :size="getSize('sm')" class="me-2">
                            {{ languageIcon }}
                        </v-icon>
                        {{ languageDisplayText }}
                    </template>

                    <!-- ⭐ PC時: rail状態でアイコンのみ -->
                    <template v-else-if="ui.rail">
                        <v-icon :size="getSize('sm')">
                            {{ languageIcon }}
                        </v-icon>
                    </template>

                    <!-- ⭐ PC時: rail解除でアイコン+テキスト -->
                    <template v-else>
                        <v-icon :size="getSize('sm')" class="me-2">
                            {{ languageIcon }}
                        </v-icon>
                        {{ languageDisplayText }}
                    </template>
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
import { usePermissions } from '@/composables/usePermissions';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';

const { t, locale } = useI18n();
const ui = useUiStore();
const { getIcon, getSize } = useDesignSystem();
const { isAdmin } = usePermissions();

const currentLocale = computed(() => locale.value);

const navItems = computed(() => [
    { title: t('nav.home'), icon: ICONS.nav.home, to: routes.HOME },
    {
        title: t('nav.dashboard'),
        icon: ICONS.nav.dashboard,
        to: routes.DASHBOARD,
    },
    { title: t('nav.profile'), icon: ICONS.nav.profile, to: routes.PROFILE },
    { title: t('nav.settings'), icon: ICONS.nav.settings, to: routes.SETTINGS },
    {
        title: t('nav.management'),
        icon: ICONS.nav.management,
        to: routes.ADMIN,
        requiresAdmin: true,
    },
]);

// ⭐ 権限に応じてフィルタリング
const filteredNavItems = computed(() => {
    return navItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});

const languageDisplayText = computed(() => {
    return locale.value === 'ja' ? '日本語' : 'English';
});

const languageIcon = computed(() => {
    return 'language'; // ⭐ Material Symbols の地球儀アイコン
});

// ⭐ ナビゲーションアイテムクリック時の処理
const handleNavItemClick = () => {
    if (!ui.isDesktop) {
        ui.drawer = false;
    }
};

function toggleLanguage() {
    locale.value = locale.value === 'ja' ? 'en' : 'ja';
}
</script>

<style scoped>
.v-list-item--active {
    --v-activated-opacity: 0 !important;
}
</style>
