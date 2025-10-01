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
                    <v-icon :size="getSize('md')">{{ item.icon }}</v-icon>
                </template>
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
        </v-list>

        <!-- 言語切り替えボタン -->
        <template v-slot:append>
            <div class="pa-2">
                <v-btn
                    @click="toggleLanguage"
                    variant="outlined"
                    size="small"
                    block
                >
                    <v-icon :size="getSize('sm')" class="me-2">
                        {{ languageIcon }}
                    </v-icon>
                    {{ languageDisplayText }}
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
        icon: 'mdi-account-group',
        to: routes.USERS,
    },
]);

// 言語表示テキスト（日本語/English）
const languageDisplayText = computed(() => {
    return locale.value === 'ja' ? '日本語' : 'English';
});

// 言語切り替えアイコン（候補から選択）
const languageIcon = computed(() => {
    // アイコン候補:
    // mdi-web - 地球儀（一般的）
    // mdi-earth - 地球
    // mdi-flag - 旗
    // mdi-google-translate - Google翻訳アイコン
    // mdi-alphabetical-variant - A文字
    // mdi-format-letter-case - 大小文字
    return 'mdi-web'; // 最も分かりやすい地球儀アイコン
});

function toggleLanguage() {
    locale.value = locale.value === 'ja' ? 'en' : 'ja';
}
</script>
