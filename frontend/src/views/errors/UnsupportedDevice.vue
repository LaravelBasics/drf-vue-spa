<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useI18n } from 'vue-i18n';
import { BREAKPOINTS } from '@/constants/breakpoints';

const { t } = useI18n();

const windowWidth = ref(window.innerWidth);
const windowHeight = ref(window.innerHeight);

// ⭐ 表示更新のみ（遷移は App.vue に任せる）
const handleResize = () => {
    windowWidth.value = window.innerWidth;
    windowHeight.value = window.innerHeight;
};

onMounted(() => {
    window.addEventListener('resize', handleResize);
});

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize);
});
</script>

<template>
    <v-container
        class="d-flex align-center justify-center"
        style="min-height: 100vh"
    >
        <v-card class="mx-auto" max-width="600" elevation="2">
            <v-card-title class="text-center pb-2">
                <div class="text-h4 mb-2">📱</div>
                <div>{{ t('errors.unsupportedDevice.title') }}</div>
            </v-card-title>

            <v-card-text class="text-center">
                <p class="text-body-1 mb-4">
                    {{ t('errors.unsupportedDevice.message') }}
                </p>

                <v-divider class="my-4" />

                <div class="text-caption text-grey">
                    <p>{{ t('errors.unsupportedDevice.currentSize') }}:</p>
                    <p class="font-weight-bold">
                        {{ windowWidth }} × {{ windowHeight }} px
                    </p>
                </div>

                <p class="text-caption text-grey mt-4">
                    {{ t('errors.unsupportedDevice.requiresSize') }}:
                    {{ BREAKPOINTS.LARGE_SCREEN }}px 以上
                </p>
            </v-card-text>

            <!-- ⭐ オプション: 手動で遷移するボタン -->
            <!-- <v-card-actions class="justify-center pb-4">
                <v-btn
                    color="primary"
                    variant="elevated"
                    size="large"
                    @click="handleGoToApp"
                    :disabled="windowWidth < BREAKPOINTS.LARGE_SCREEN"
                >
                    {{ auth.isAuthenticated ? t('errors.unsupportedDevice.home') : t('auth.login') }}
                </v-btn>
            </v-card-actions> -->
        </v-card>
    </v-container>
</template>
