<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { usePermissions } from '@/composables/usePermissions';

const { t } = useI18n();
const { isAdmin } = usePermissions();

const copyrightText = computed(() => {
    const year = new Date().getFullYear();
    const company = t('footer.company');
    return t('footer.copyright', { year, company });
});

const versionText = computed(() => {
    const version = import.meta.env.VITE_APP_VERSION || '1.0.0';
    return t('footer.version', { version });
});
</script>

<template>
    <v-footer app class="bg-grey-lighten-4 py-1 px-4">
        <v-container fluid class="pa-0">
            <!-- Vuetifyユーティリティクラスでレスポンシブ対応 -->
            <div
                class="d-flex flex-column flex-sm-row justify-space-between align-center ga-0"
            >
                <div class="text-caption text-grey-darken-1">
                    {{ copyrightText }}
                </div>

                <div v-if="isAdmin" class="text-caption text-grey">
                    {{ versionText }}
                </div>
            </div>
        </v-container>
    </v-footer>
</template>
