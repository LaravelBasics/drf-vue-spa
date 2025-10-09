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
        // v-paginationの矢印アイコンをMaterial Symbolsで定義
        prev: 'navigate_before', // ⬅️ 前へボタン
        next: 'navigate_next', // ⬅️ 次へボタン
        // v-selectなどが使うアイコンもついでに追加しておくと安全です
        expand: 'expand_more',
        collapse: 'unfold_less',
        // ⭐ 新しく追加するデータテーブル関連アイコン ⭐
        sortAsc: 'arrow_upward', // ソート: 昇順
        sortDesc: 'arrow_downward', // ソート: 降順
        unfold: 'arrow_drop_down', // テーブル行の展開/折りたたみ

        // v-pagination 関連 (前回追加済み)
        prev: 'navigate_before',
        next: 'navigate_next',

        // 一般的なUI要素 (前回追加/確認済み)
        collapse: 'unfold_less',
        complete: 'check_circle',
        cancel: 'cancel',
        close: 'close',
        delete: 'delete',
        expand: 'expand_more', // v-select や v-menu など
        // その他: エラー、警告、情報などのステータスアイコンも追加しておくと安全
        info: 'info',
        warning: 'warning',
        error: 'error',
        success: 'check_circle',

        // ⭐ v-data-table が使用するその他の重要アイコン
        first: 'first_page',
        last: 'last_page',
        delimiter: 'more_horiz',
        menu: 'menu',
        subgroup: 'arrow_right',
        checkbox: 'check_box_outline_blank', //チェックボックス（使われていたら追加）
        // MDIにはあるが Material Symbols にはないアイコンの代替（v-data-tableが内部で使う可能性あり）
        // ⭐ v-checkbox/v-radio など フォームコンポーネント用
        checkboxOn: 'check_box', // チェック済み (✅)
        checkboxOff: 'check_box_outline_blank', // 未チェック (☐)
        checkboxIndeterminate: 'indeterminate_check_box', // 不定状態 (➖)

        // v-radio 用のエイリアス (ついでに追加しておくと便利です)
        radioOn: 'radio_button_checked', // 選択済み (🔘)
        radioOff: 'radio_button_unchecked', // 未選択 (⚪)

        // ... (v-data-table 関連もここにすべて含まれていることを確認)
        sortAsc: 'arrow_upward',
        sortDesc: 'arrow_downward',
        expand: 'expand_more',
        prev: 'navigate_before',
        next: 'navigate_next',
        info: 'info', // type="info"
        warning: 'warning', // type="warning"
        error: 'error', // type="error"
        success: 'check_circle', // type="success"
        clear: 'close', // または 'cancel'。ここでは'close'が一般的
        cancel: 'cancel',
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
