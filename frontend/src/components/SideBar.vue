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
    <v-navigation-drawer
        v-model="ui.drawer"
        :rail="ui.isDesktop && ui.rail"
        :temporary="!ui.isDesktop"
        :permanent="ui.isDesktop"
        mobile-breakpoint="md"
    >
        <!-- Vuetify 3.xのバグ対応：tabindex本来は不要、バグ対応で明示的指定が必要 -->
        <v-list nav>
            <v-list-item
                v-for="(item, i) in filteredNavItems"
                :key="i"
                :to="item.to"
                :value="item.title"
                tabindex="0"
                @click="handleNavItemClick"
                color="grey-darken-2"
            >
                <template #prepend>
                    <v-icon :size="ICON_SIZES.md">{{ item.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>

        <template #append>
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
:deep(.v-list-item--active) {
    /* アクティブ時の背景色を無効化（カスタムcolorプロパティを優先） */
    --v-activated-opacity: 0;
}
</style>
