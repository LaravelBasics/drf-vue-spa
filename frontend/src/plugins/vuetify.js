// src/plugins/vuetify.js - Material Symbols (Google公式) 対応版
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
// import { aliases, md } from 'vuetify/iconsets/md'; // ⭐ Google公式アイコン
import { h } from 'vue';
import { ja } from 'vuetify/locale';
import { THEME_CONFIG } from '@/constants/theme';

import 'vuetify/styles';

// ⭐ 変更点 2: Material Symbols (MS) のカスタムアイコンセットを定義します
const materialSymbols = {
    // ページネーションなどが内部的に使用するアイコンを Material Symbols にマッピング
    aliases: {
        // ページネーション
        prev: 'navigate_before',
        next: 'navigate_next',
        first: 'first_page',
        last: 'last_page',

        // データテーブル
        sortAsc: 'arrow_upward',
        sortDesc: 'arrow_downward',
        expand: 'expand_more',
        unfold: 'arrow_drop_down',

        // チェックボックス・ラジオボタン
        checkboxOn: 'check_box',
        checkboxOff: 'check_box_outline_blank',
        checkboxIndeterminate: 'indeterminate_check_box',
        radioOn: 'radio_button_checked',
        radioOff: 'radio_button_unchecked',

        // その他
        collapse: 'unfold_less',
        complete: 'check_circle',
        cancel: 'cancel',
        close: 'close',
        delete: 'delete',
        clear: 'close',
        info: 'info',
        warning: 'warning',
        error: 'error',
        success: 'check_circle',
        menu: 'menu',
        subgroup: 'arrow_right',
        delimiter: 'more_horiz',
        // ... (他のデフォルトアイコンも必要に応じて追加)
    },
    // 重要な変更: アイコンをレンダリングするためのコンポーネント関数
    component: (props) => {
        // props.icon の値（例: 'home' や 'md:home'）からアイコン名のみを抽出
        let iconName = props.icon.startsWith('md:')
            ? props.icon.substring(3)
            : props.icon;

        // <span>タグと Material Symbols のクラスでレンダリング
        return h('span', {
            // main.js でインポートしたCSSに依存するクラス
            class: 'material-symbols-outlined',
            // アイコン名がテキストコンテンツとして挿入される
            innerHTML: iconName,
        });
    },
};

export default createVuetify({
    components,
    directives,
    icons: {
        // ⭐ 変更点 3: デフォルトセットをカスタムセット 'ms' に変更
        defaultSet: 'ms',
        aliases: materialSymbols.aliases, // ⭐ これが重要
        sets: {
            // ⭐ 変更点 4: 'ms' という名前で Material Symbols のカスタム定義を登録
            ms: materialSymbols,
            // md, // ⬅️ 元の md セットは不要
        },
    },
    theme: {
        defaultTheme: 'light',
        themes: {
            light: {
                colors: THEME_CONFIG.colors.light,
            },
            dark: {
                colors: THEME_CONFIG.colors.dark,
            },
        },
    },
    defaults: THEME_CONFIG.defaults,
    locale: {
        locale: 'ja',
        fallback: 'ja',
        messages: { ja },
    },
});
