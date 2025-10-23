// src/router/screen-size-guard.js - 画面サイズチェック

import { routes } from '@/constants/routes';
import { BREAKPOINTS } from '@/constants/breakpoints';

export const screenSizeGuard = (to, from) => {
    // UNSUPPORTED_DEVICEページからの遷移は常に許可（無限ループ防止）
    if (from.path === routes.UNSUPPORTED_DEVICE) {
        return true;
    }

    // 画面サイズチェックが不要なページはスキップ
    if (!to.meta.requiresLargeScreen) {
        return true;
    }

    const windowWidth = window.innerWidth;
    const isLargeEnough = windowWidth >= BREAKPOINTS.LARGE_SCREEN;

    // スマホ（768px未満）で大画面必須ページへアクセスした場合
    if (!isLargeEnough) {
        return {
            path: routes.UNSUPPORTED_DEVICE,
            replace: true,
        };
    }

    return true;
};
