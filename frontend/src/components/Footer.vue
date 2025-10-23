<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';

const { t } = useI18n();
const { isAdmin } = usePermissions();

// コピーライト表記（年と会社名を動的に取得）
const copyrightText = computed(() => {
    const year = new Date().getFullYear();
    const company = t('footer.company');
    return t('footer.copyright', { year, company });
});

// バージョン情報（管理者のみ表示）
const versionText = computed(() => {
    const version = import.meta.env.VITE_APP_VERSION || '1.0.0';
    return t('footer.version', { version });
});
</script>

<template>
    <v-footer app class="bg-grey-lighten-4 py-0 px-2">
        <v-container fluid class="pa-0">
            <!-- PC: 横並び（左右配置）、スマホ: 縦並び（中央配置） -->
            <div class="footer-content">
                <div class="text-caption text-grey-darken-1">
                    {{ copyrightText }}
                </div>

                <!-- バージョン情報は管理者のみ表示 -->
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

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;
}

/* スマホ: 縦並び・中央寄せ */
@media (max-width: 599px) {
    .footer-content {
        flex-direction: column;
        justify-content: center;
        text-align: center;
        gap: 8px;
    }
}
</style>
