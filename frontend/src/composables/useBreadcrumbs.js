// src/composables/useBreadcrumbs.js - パンくずリスト自動生成
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

export function useBreadcrumbs() {
    const route = useRoute();
    const { t } = useI18n();

    /**
     * 現在のルートからパンくずリストを自動生成
     * ルートのmetaに定義された breadcrumb 情報を使用
     */
    const breadcrumbs = computed(() => {
        const crumbs = [];
        const matched = route.matched;

        matched.forEach((record) => {
            const meta = record.meta;

            // breadcrumb が false の場合はスキップ
            if (meta.breadcrumb === false) {
                return;
            }

            // breadcrumb が定義されている場合
            if (meta.breadcrumb) {
                const crumb = {
                    title:
                        typeof meta.breadcrumb === 'string'
                            ? t(meta.breadcrumb)
                            : t(meta.breadcrumb.i18nKey),
                    to: record.path,
                    disabled: false,
                };

                // 動的パラメータを含むパスを置換
                if (route.params && Object.keys(route.params).length > 0) {
                    Object.keys(route.params).forEach((key) => {
                        crumb.to = crumb.to.replace(
                            `:${key}`,
                            route.params[key],
                        );
                    });
                }

                // カスタム無効化条件
                if (meta.breadcrumb.disabled) {
                    crumb.disabled =
                        typeof meta.breadcrumb.disabled === 'function'
                            ? meta.breadcrumb.disabled(route)
                            : meta.breadcrumb.disabled;
                }

                crumbs.push(crumb);
            }
        });

        // 最後のパンくずは常に無効化
        if (crumbs.length > 0) {
            crumbs[crumbs.length - 1].disabled = true;
        }

        return crumbs;
    });

    return {
        breadcrumbs,
    };
}
