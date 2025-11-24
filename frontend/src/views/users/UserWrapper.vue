<template>
    <router-view />
</template>

<script setup>
/**
 * UserWrapper - ユーザーリソースのコンテキストラッパー
 *
 * 🎯 役割:
 * 1. パンくずリスト構造の親要素として機能
 * 2. 詳細・編集・削除画面の共通の親として機能
 * 3. ルートパラメータ (:id) を子コンポーネントに継承
 *
 * 📝 設計思想:
 * - データ取得は各子コンポーネント（UserDetail, UserUpdate, UserDelete）で直接実行
 * - 共通データが必要な場合は provide/inject または Pinia を検討
 * - 現在はシンプルに <router-view> のみでOK
 *
 * 🔗 子ルート:
 * - /admin/users/:id (UserDetail) - デフォルト
 * - /admin/users/:id/update (UserUpdate)
 * - /admin/users/:id/delete (UserDelete)
 */
</script>
