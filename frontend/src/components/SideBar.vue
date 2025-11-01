<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useLocaleStore } from '@/stores/locale';
import { useUiStore } from '@/stores/ui';
import { usePermissions } from '@/composables/usePermissions';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { ICON_SIZES } from '@/constants/theme';

const { t } = useI18n();
const localeStore = useLocaleStore();
const ui = useUiStore();
const { isAdmin } = usePermissions();

// ナビゲーション項目の定義
const navItems = computed(() => [
    { title: t('pages.home.title'), icon: ICONS.nav.home, to: routes.HOME },
    {
        title: t('pages.admin.title'),
        icon: ICONS.nav.management,
        to: routes.ADMIN.ROOT,
        requiresAdmin: true,
    },
    {
        title: t('pages.settings.title'),
        icon: ICONS.nav.settings,
        to: routes.SETTINGS,
    },
]);

// 管理者権限が必要な項目をフィルタリング
const filteredNavItems = computed(() => {
    return navItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});

const languageDisplayText = computed(() => {
    return localeStore.locale === 'ja' ? '日本語' : 'English';
});

// モバイル時はナビゲーション後にドロワーを閉じる
const handleNavItemClick = () => {
    if (!ui.isDesktop) {
        ui.drawer = false;
    }
};

function toggleLanguage() {
    const newLocale = localeStore.locale === 'ja' ? 'en' : 'ja';
    localeStore.setLocale(newLocale);
}
</script>

<template>
    <!-- Vuetify 3.9+: appプロパティ不要（自動レイアウト管理） -->
    <v-navigation-drawer
        v-model="ui.drawer"
        :rail="ui.isDesktop && ui.rail"
        :temporary="!ui.isDesktop"
    >
        <v-list nav>
            <v-list-item
                v-for="(item, i) in filteredNavItems"
                :key="i"
                :to="item.to"
                :value="item.title"
                link
                tabindex="0"
                @click="handleNavItemClick"
                color="grey-darken-2"
            >
                <template v-slot:prepend>
                    <v-icon :size="ICON_SIZES.md">{{ item.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>

        <template v-slot:append>
            <div class="pa-2">
                <!-- 言語切り替えボタン（モバイル/デスクトップ/Railモードで表示切替） -->
                <v-btn
                    @click.stop="toggleLanguage"
                    variant="outlined"
                    size="small"
                    block
                >
                    <template v-if="!ui.isDesktop">
                        <v-icon :size="ICON_SIZES.sm" class="me-2">
                            {{ ICONS.brand.language }}
                        </v-icon>
                        {{ languageDisplayText }}
                    </template>

                    <template v-else-if="ui.rail">
                        <v-icon :size="ICON_SIZES.sm">
                            {{ ICONS.brand.language }}
                        </v-icon>
                    </template>

                    <template v-else>
                        <v-icon :size="ICON_SIZES.sm" class="me-2">
                            {{ ICONS.brand.language }}
                        </v-icon>
                        {{ languageDisplayText }}
                    </template>
                </v-btn>
            </div>
        </template>
    </v-navigation-drawer>
</template>

<style scoped>
/* アクティブ状態の透明度調整を無効化 */
.v-list-item--active {
    --v-activated-opacity: 0 !important;
}
</style>
