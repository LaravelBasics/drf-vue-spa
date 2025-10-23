// src/plugins/vuetify.js - Vuetify設定（Material Symbols使用）

import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { h } from 'vue';
import { ja, en } from 'vuetify/locale';
import { THEME_CONFIG } from '@/constants/theme';

import 'vuetify/styles';

// Material Symbolsのカスタムアイコンセット
const materialSymbols = {
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
    },
    // Material Symbolsアイコンをレンダリングするコンポーネント
    component: (props) => {
        let iconName = props.icon.startsWith('md:')
            ? props.icon.substring(3)
            : props.icon;

        return h('span', {
            class: 'material-symbols-outlined',
            innerHTML: iconName,
        });
    },
};

const vuetify = createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'ms',
        aliases: materialSymbols.aliases,
        sets: {
            ms: materialSymbols,
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
        messages: { ja, en },
    },
});

export default vuetify;
