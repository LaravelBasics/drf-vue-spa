// src/plugins/vuetify.js - 日本語ロケール対応版
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { aliases, mdi } from 'vuetify/iconsets/mdi';
import { ja } from 'vuetify/locale';
import { THEME_CONFIG } from '@/constants/theme';

import 'vuetify/styles';

export default createVuetify({
    components,
    directives,
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: { mdi },
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
