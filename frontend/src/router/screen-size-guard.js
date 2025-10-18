// src/router/screen-size-guard.js（修正版）
import { routes } from '@/constants/routes';
import { BREAKPOINTS } from '@/constants/breakpoints';

export const screenSizeGuard = (to, from) => {
    // ⭐ UNSUPPORTED_DEVICE から遷移する場合はチェックをスキップ
    if (from.path === routes.UNSUPPORTED_DEVICE) {
        console.log('📱 非対応画面からの遷移 - サイズチェックをスキップ');
        return true;
    }

    // 画面サイズチェックが不要なページはスキップ
    if (!to.meta.requiresLargeScreen) {
        return true;
    }

    const windowWidth = window.innerWidth;
    const isLargeEnough = windowWidth >= BREAKPOINTS.LARGE_SCREEN;

    console.log('📱 Screen Size Guard:', {
        path: to.path,
        from: from.path,
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

// ==================== 変更点のまとめ ====================
/*
✅ 追加された処理:

1. UNSUPPORTED_DEVICE からの遷移を許可
   if (from.path === routes.UNSUPPORTED_DEVICE) {
       return true;  // ← チェックをスキップ
   }

2. ログにfrom.pathを追加
   console.log('📱 Screen Size Guard:', {
       from: from.path,  // ← 追加
       ...
   });

これにより:
- UnsupportedDevice.vue で画面サイズが変わった時
- handleGoToApp() が router.push() を実行
- ルーターガードがチェックをスキップ
- 正しく遷移できる！
*/
