<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';

const { t } = useI18n();
const { isAdmin } = usePermissions();

// ⭐ フッターリンク
// const footerLinks = [
//     { key: 'terms', href: '/terms' },
//     { key: 'privacy', href: '/privacy' },
//     { key: 'contact', href: '/contact' },
// ];

// ⭐ コピーライトテキスト
const copyrightText = computed(() => {
    const year = new Date().getFullYear();
    const company = t('footer.company');
    return t('footer.copyright', { year, company });
});

// ⭐ バージョン情報
const versionText = computed(() => {
    const version = import.meta.env.VITE_APP_VERSION || '1.0.0';
    return t('footer.version', { version });
});
</script>

<template>
    <v-footer app class="bg-grey-lighten-4 py-0 px-2">
        <v-container fluid class="pa-0">
            <!-- ⭐ PC: 横並び、スマホ: 縦並び -->
            <div class="footer-content">
                <!-- コピーライト -->
                <div class="text-caption text-grey-darken-1">
                    {{ copyrightText }}
                </div>

                <!-- リンク -->
                <!-- <div class="mr-5 pr-5 footer-links">
                    <a
                        v-for="(link, index) in footerLinks"
                        :key="link.key"
                        :href="link.href"
                        target="_blank"
                        class="text-caption text-grey-darken-1 text-decoration-none mx-2"
                    >
                        {{ t(`footer.links.${link.key}`) }}
                        <span
                            v-if="index < footerLinks.length - 1"
                            class="text-grey-lighten-1"
                            >|</span
                        >
                    </a>
                </div> -->

                <!-- バージョン情報（管理者のみ） -->
                <div v-if="isAdmin" class="text-caption text-grey">
                    {{ versionText }}
                </div>
            </div>
        </v-container>
    </v-footer>
</template>

<style scoped>
.v-footer {
    margin-top: auto;
}

/* ⭐ PC: 横並び（space-between） */
.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}

/* .footer-links {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.footer-links a {
    transition: color 0.2s;
}

.footer-links a:hover {
    color: rgb(var(--v-theme-primary)) !important;
} */

/* ⭐ スマホ: 縦並び（中央寄せ） */
@media (max-width: 599px) {
    .footer-content {
        flex-direction: column;
        justify-content: center;
        text-align: center;
        gap: 8px;
    }

    /* .footer-links {
        justify-content: center;
    } */
}
</style>
