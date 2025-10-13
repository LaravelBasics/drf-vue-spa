// src/router/screen-size-guard.js
import { routes } from '@/constants/routes';
import { BREAKPOINTS } from '@/constants/breakpoints';

export const screenSizeGuard = (to, from) => {
    // 画面サイズチェックが不要なページはスキップ
    if (!to.meta.requiresLargeScreen) {
        return true;
    }

    const windowWidth = window.innerWidth;
    const isLargeEnough = windowWidth >= BREAKPOINTS.LARGE_SCREEN;

    console.log('📱 Screen Size Guard:', {
        path: to.path,
        windowWidth: windowWidth,
        isLargeEnough: isLargeEnough,
        requiresLargeScreen: to.meta.requiresLargeScreen,
    });

    // スマホ（768px未満）でLargeScreen必須なページへアクセス
    if (!isLargeEnough) {
        console.warn('📱 スマホサイズ - UnsupportedDeviceへリダイレクト');
        return {
            path: routes.UNSUPPORTED_DEVICE,
            replace: true,
        };
    }

    console.log('✅ Screen Size Guard 通過');
    return true;
};
