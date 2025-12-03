// src/plugins/vuetify.js

import { createVuetify } from 'vuetify';
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n';
import { useI18n } from 'vue-i18n';
import i18n from './i18n';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { h } from 'vue';
import { THEME_CONFIG } from '@/constants/theme';

import 'vuetify/styles';

const materialSymbols = {
    aliases: {
        prev: 'navigate_before',
        next: 'navigate_next',
        first: 'first_page',
        last: 'last_page',
        sortAsc: 'arrow_upward',
        sortDesc: 'arrow_downward',
        expand: 'expand_more',
        dropdown: 'arrow_drop_down',
        unfold: 'arrow_drop_down',
        checkboxOn: 'check_box',
        checkboxOff: 'check_box_outline_blank',
        checkboxIndeterminate: 'indeterminate_check_box',
        radioOn: 'radio_button_checked',
        radioOff: 'radio_button_unchecked',
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
    locale: {
        // 🌟 Vue I18nと自動連携
        adapter: createVueI18nAdapter({ i18n, useI18n }),
    },
});

export default vuetify;
