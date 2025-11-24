// src/composables/useBreadcrumbs.js - パンくずリスト自動生成（標準版）

import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';

export function useBreadcrumbs() {
    const route = useRoute();
    const { t } = useI18n();

    const breadcrumbs = computed(() => {
        // Vue Routerが親→子の順番で並べてくれる
        return route.matched
            .filter((record) => {
                // breadcrumb が false の場合はスキップ
                if (record.meta?.breadcrumb === false) {
                    return false;
                }
                // breadcrumb が定義されているものだけ
                return record.meta?.breadcrumb;
            })
            .map((record, index, array) => {
                const isLast = index === array.length - 1;

                // 多言語対応
                let titleText =
                    typeof record.meta.breadcrumb === 'string'
                        ? t(record.meta.breadcrumb)
                        : t(record.meta.breadcrumb.i18nKey);

                // 💡 パラメータの初期化: 現在のルートパラメータをコピー
                let destination;
                let destinationParams = { ...route.params }; // 現在のパラメーターをコピー

                // 💡 重要なロジック: パスに ':id' が含まれていない場合、id パラメータを削除
                if (!record.path.includes('/:id')) {
                    delete destinationParams.id;
                }

                // Wrapperパターン: 子に空パスのルートがある場合 (UserWrapperの処理)
                if (record.children?.some((child) => child.path === '')) {
                    const defaultChild = record.children.find(
                        (child) => child.path === '',
                    );
                    destination = defaultChild?.name
                        ? { name: defaultChild.name, params: destinationParams }
                        : record.path;
                } else if (record.name) {
                    destination = {
                        name: record.name,
                        params: destinationParams,
                    };
                } else {
                    destination = record.path;
                }

                return {
                    title: titleText,
                    to: destination,
                    disabled: isLast,
                };
            });
    });

    return { breadcrumbs };
}
