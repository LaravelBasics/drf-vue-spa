<template>
    <div>
        <!-- ⭐ ヘッダーに専用ボタンを追加 -->
        <Header app-title="商品管理システム">
            <!-- 中央のボタン群 -->
            <template #page-actions>
                <v-btn
                    variant="outlined"
                    color="white"
                    class="mx-1"
                    @click="openSearchDialog"
                >
                    <v-icon class="mr-1">mdi-magnify</v-icon>
                    商品検索
                </v-btn>
                <v-btn
                    variant="outlined"
                    color="white"
                    class="mx-1"
                    @click="exportToPDF"
                >
                    <v-icon class="mr-1">mdi-file-pdf-box</v-icon>
                    PDF出力
                </v-btn>
            </template>

            <!-- 右側のボタン -->
            <template #page-actions-right>
                <v-btn
                    icon="mdi-cog"
                    @click="openProductSettings"
                    class="mr-2"
                ></v-btn>
            </template>

            <!-- モバイル用 -->
            <template #mobile-actions>
                <v-list-item @click="openSearchDialog">
                    <template #prepend>
                        <v-icon>mdi-magnify</v-icon>
                    </template>
                    <v-list-item-title>商品検索</v-list-item-title>
                </v-list-item>
                <v-list-item @click="exportToPDF">
                    <template #prepend>
                        <v-icon>mdi-file-pdf-box</v-icon>
                    </template>
                    <v-list-item-title>PDF出力</v-list-item-title>
                </v-list-item>
            </template>
        </Header>

        <!-- ページコンテンツ -->
        <v-container>
            <h1>商品一覧</h1>
            <!-- 商品リストなど -->
        </v-container>

        <!-- 検索ダイアログ -->
        <v-dialog v-model="searchDialog" max-width="500px">
            <v-card>
                <v-card-title>商品検索</v-card-title>
                <v-card-text>
                    <v-text-field
                        v-model="searchQuery"
                        label="商品名で検索"
                        prepend-icon="mdi-magnify"
                    ></v-text-field>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="searchDialog = false">キャンセル</v-btn>
                    <v-btn color="primary" @click="performSearch">検索</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import Header from '@/components/Header.vue';

// State
const searchDialog = ref(false);
const searchQuery = ref('');

// Methods
const openSearchDialog = () => {
    searchDialog.value = true;
};

const exportToPDF = () => {
    console.log('PDF出力処理');
    // PDF出力ロジック
};

const openProductSettings = () => {
    console.log('商品設定画面を開く');
    // 設定画面への遷移など
};

const performSearch = () => {
    console.log('検索実行:', searchQuery.value);
    // 検索処理
    searchDialog.value = false;
};
</script>
