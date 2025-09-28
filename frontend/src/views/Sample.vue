<template>
    <!-- ヘッダーコンポーネント -->
    <Header app-title="Template App"></Header>

    <!-- メインコンテンツ -->
    <v-container fluid>
        <!-- ページタイトル -->
        <v-row class="mb-4">
            <v-col>
                <h1
                    class="text-h4 font-weight-bold text-center text-blue-darken-3"
                >
                    <v-icon size="40" class="mr-2">mdi-card-multiple</v-icon>
                    サンプルカード一覧
                </h1>
                <p class="text-center text-body-1 mt-2 text-grey-darken-1">
                    各カテゴリのサンプル機能をご確認いただけます
                </p>
            </v-col>
        </v-row>

        <!-- カードグリッド -->
        <v-row>
            <v-col
                v-for="(item, index) in sampleItems"
                :key="item.id"
                cols="12"
                sm="6"
                md="4"
                lg="3"
            >
                <v-card
                    :color="item.color"
                    dark
                    elevation="8"
                    class="sample-card"
                    height="280"
                    @click="handleCardClick(item)"
                >
                    <!-- カードヘッダー -->
                    <v-card-title
                        class="d-flex justify-center align-center pa-4"
                    >
                        <v-icon
                            :icon="item.icon"
                            size="48"
                            class="mb-2"
                        ></v-icon>
                    </v-card-title>

                    <!-- カードコンテンツ -->
                    <v-card-text class="text-center">
                        <h3 class="text-h6 font-weight-bold mb-2">
                            {{ item.title }}
                        </h3>
                        <p class="text-body-2 mb-3">
                            {{ item.description }}
                        </p>

                        <!-- 機能リスト -->
                        <v-chip-group class="mb-3">
                            <v-chip
                                v-for="feature in item.features"
                                :key="feature"
                                size="small"
                                variant="outlined"
                                color="white"
                            >
                                {{ feature }}
                            </v-chip>
                        </v-chip-group>
                    </v-card-text>

                    <!-- カードアクション -->
                    <v-card-actions class="justify-center pb-4">
                        <v-btn
                            :color="item.btnColor"
                            variant="elevated"
                            :prepend-icon="item.btnIcon"
                            @click.stop="handleButtonClick(item)"
                        >
                            {{ item.btnText }}
                        </v-btn>
                    </v-card-actions>

                    <!-- ホバーエフェクト用オーバーレイ -->
                    <v-overlay
                        :model-value="false"
                        contained
                        class="d-flex align-center justify-center"
                    >
                        <v-icon size="64" color="white">mdi-eye</v-icon>
                    </v-overlay>
                </v-card>
            </v-col>
        </v-row>

        <!-- フッター情報 -->
        <v-row class="mt-8">
            <v-col>
                <v-card color="blue-grey-lighten-5" flat class="pa-4">
                    <v-card-text class="text-center">
                        <v-icon icon="mdi-information" class="mr-2"></v-icon>
                        <span class="text-body-2 text-grey-darken-2">
                            各カードをクリックして詳細を確認、またはボタンで直接アクションを実行できます
                        </span>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>

    <!-- アクション結果表示用スナックバー -->
    <v-snackbar
        v-model="showSnackbar"
        :color="snackbarColor"
        :timeout="3000"
        location="top"
    >
        {{ snackbarMessage }}
        <template #actions>
            <v-btn color="white" variant="text" @click="showSnackbar = false">
                閉じる
            </v-btn>
        </template>
    </v-snackbar>
</template>

<script setup>
import { ref } from 'vue';
import Header from '@/components/Header.vue';

// State
const showSnackbar = ref(false);
const snackbarMessage = ref('');
const snackbarColor = ref('success');

// ⭐ サンプルデータ（オブジェクト配列）
const sampleItems = ref([
    {
        id: 1,
        title: 'ユーザー管理',
        description: 'ユーザーの登録、編集、削除などの基本的な管理機能',
        icon: 'mdi-account-group',
        color: 'blue-darken-2',
        btnText: '管理画面へ',
        btnIcon: 'mdi-cog',
        btnColor: 'white',
        features: ['CRUD操作', 'フィルタ', '検索'],
        action: 'user-management',
    },
    {
        id: 2,
        title: 'データ分析',
        description: 'グラフやチャートを使用したデータの可視化機能',
        icon: 'mdi-chart-line',
        color: 'green-darken-2',
        btnText: 'グラフ表示',
        btnIcon: 'mdi-chart-bar',
        btnColor: 'white',
        features: ['棒グラフ', '円グラフ', 'トレンド'],
        action: 'analytics',
    },
    {
        id: 3,
        title: 'ファイル管理',
        description: 'ファイルのアップロード、ダウンロード、プレビュー機能',
        icon: 'mdi-folder-multiple',
        color: 'orange-darken-2',
        btnText: 'ファイル一覧',
        btnIcon: 'mdi-file-document',
        btnColor: 'white',
        features: ['アップロード', 'プレビュー', '共有'],
        action: 'file-management',
    },
    {
        id: 4,
        title: 'カレンダー',
        description: 'イベントやスケジュールの管理機能',
        icon: 'mdi-calendar',
        color: 'purple-darken-2',
        btnText: 'カレンダー表示',
        btnIcon: 'mdi-calendar-month',
        btnColor: 'white',
        features: ['月表示', 'イベント', '通知'],
        action: 'calendar',
    },
    {
        id: 5,
        title: 'チャット',
        description: 'リアルタイムメッセージング機能',
        icon: 'mdi-chat',
        color: 'teal-darken-2',
        btnText: 'チャット開始',
        btnIcon: 'mdi-send',
        btnColor: 'white',
        features: ['リアルタイム', '絵文字', 'ファイル'],
        action: 'chat',
    },
    {
        id: 6,
        title: '通知管理',
        description: 'システム通知やお知らせの管理機能',
        icon: 'mdi-bell',
        color: 'red-darken-2',
        btnText: '通知設定',
        btnIcon: 'mdi-bell-cog',
        btnColor: 'white',
        features: ['プッシュ通知', 'メール', 'SMS'],
        action: 'notifications',
    },
    {
        id: 7,
        title: 'レポート',
        description: '各種レポートの生成とエクスポート機能',
        icon: 'mdi-file-chart',
        color: 'indigo-darken-2',
        btnText: 'レポート生成',
        btnIcon: 'mdi-download',
        btnColor: 'white',
        features: ['PDF', 'Excel', '自動生成'],
        action: 'reports',
    },
    {
        id: 8,
        title: '設定',
        description: 'アプリケーション設定とカスタマイズ',
        icon: 'mdi-cog',
        color: 'brown-darken-2',
        btnText: '設定変更',
        btnIcon: 'mdi-wrench',
        btnColor: 'white',
        features: ['テーマ', '言語', 'セキュリティ'],
        action: 'settings',
    },
]);

// Methods
const handleCardClick = (item) => {
    showSnackbar.value = true;
    snackbarMessage.value = `「${item.title}」カードがクリックされました`;
    snackbarColor.value = 'info';

    console.log('Card clicked:', item);
};

const handleButtonClick = (item) => {
    showSnackbar.value = true;
    snackbarMessage.value = `「${item.btnText}」がクリックされました - Action: ${item.action}`;
    snackbarColor.value = 'success';

    // 実際のアクションロジックをここに追加
    console.log('Button clicked:', item.action, item);

    // 例：ルーティング
    // router.push(`/${item.action}`);
};
</script>

<style scoped>
.sample-card {
    transition: all 0.3s ease;
    cursor: pointer;
}

.sample-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.v-chip-group {
    justify-content: center;
}

.v-card-title {
    min-height: 100px;
}

.v-card-text {
    flex-grow: 1;
}
</style>
