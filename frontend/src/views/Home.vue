<!-- src/views/Home.vue -->
<!-- <script setup>
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ROUTE_NAMES } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const { showWarning } = useApiError();
const { isAdmin } = usePermissions();

// マウント時に権限エラーチェック
onMounted(() => {
    if (route.query.unauthorized === 'admin') {
        showWarning('notifications.unauthorized.admin');
        router.replace({ name: ROUTE_NAMES.HOME, query: {} });
    }
});

const menuItems = computed(() => [
    {
        id: 'admin',
        icon: ICONS.nav.management,
        title: t('pages.admin.title'),
        to: { name: ROUTE_NAMES.ADMIN.MENU },
        color: 'secondary',
        requiresAdmin: true,
    },
    {
        id: 'settings',
        icon: ICONS.nav.settings,
        title: t('pages.settings.title'),
        to: { name: ROUTE_NAMES.SETTINGS },
        color: COLORS.neutral.medium,
    },
]);

// 管理者権限が必要なメニューをフィルタリング
const filteredMenuItems = computed(() => {
    return menuItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});
</script> -->

<!-- <template>
    <Header :app-title="t('pages.home.title')" />

    <MenuCardGrid :items="filteredMenuItems" />
</template> -->

<!-- src/views/Home.vue -->
<script setup>
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter, useRoute } from 'vue-router';
import { usePermissions } from '@/composables/usePermissions';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import MenuCardGrid from '@/components/MenuCardGrid.vue';
import { ROUTE_NAMES } from '@/constants/routes';
import { ICONS } from '@/constants/icons';
import { COLORS } from '@/constants/theme';

const { t } = useI18n();
const router = useRouter();
const route = useRoute();
const { showWarning } = useApiError();
const { isAdmin } = usePermissions();

// ===== グループ化セレクト用のデータと状態 =====
const selectedUserId = ref(null);
const userSelectItems = ref([]);

// バックエンドから来ると想定したデータ（実際は API から取得）
const mockUserSelectData = [
    // 先頭に「全て」
    {
        type: 'all',
        value: null,
        label: '全て',
        disabled: false,
        groupCode: null,
        userId: null,
    },

    // 管理者グループ
    {
        type: 'group',
        value: null,
        label: '管理者グループ',
        disabled: true,
        groupCode: 'admin',
        userId: null,
    },
    {
        type: 'user',
        value: 'admin:user_a',
        label: 'ユーザーA',
        disabled: false,
        groupCode: 'admin',
        userId: 'user_a',
    },
    {
        type: 'user',
        value: 'admin:user_b',
        label: 'ユーザーB',
        disabled: false,
        groupCode: 'admin',
        userId: 'user_b',
    },
    {
        type: 'user',
        value: 'admin:user_c',
        label: 'ユーザーC',
        disabled: false,
        groupCode: 'admin',
        userId: 'user_c',
    },

    // 一般グループ
    {
        type: 'group',
        value: null,
        label: '一般グループ',
        disabled: true,
        groupCode: 'general',
        userId: null,
    },
    {
        type: 'user',
        value: 'general:user_a',
        label: 'ユーザーA',
        disabled: false,
        groupCode: 'general',
        userId: 'user_a',
    },
    {
        type: 'user',
        value: 'general:user_b',
        label: 'ユーザーB',
        disabled: false,
        groupCode: 'general',
        userId: 'user_b',
    },

    // 店長グループ
    {
        type: 'group',
        value: null,
        label: '店長グループ',
        disabled: true,
        groupCode: 'manager',
        userId: null,
    },
    {
        type: 'user',
        value: 'manager:user_a',
        label: 'ユーザーA',
        disabled: false,
        groupCode: 'manager',
        userId: 'user_a',
    },
    {
        type: 'user',
        value: 'manager:user_c',
        label: 'ユーザーC',
        disabled: false,
        groupCode: 'manager',
        userId: 'user_c',
    },
    {
        type: 'user',
        value: 'manager:user_d',
        label: 'ユーザーD',
        disabled: false,
        groupCode: 'manager',
        userId: 'user_d',
    },
];

// 実際の API 呼び出し用関数（コメントアウト例）
// const fetchUserSelectData = async () => {
//     try {
//         const response = await axios.get('/api/users/select-list/');
//         userSelectItems.value = response.data;
//     } catch (error) {
//         console.error('Failed to fetch user list:', error);
//     }
// };

// 検索実行関数（例）
const handleSearch = () => {
    // API送信時は userId だけを抽出
    const selectedItem = userSelectItems.value.find(
        (item) => item.value === selectedUserId.value,
    );

    const searchParams = {
        create_by: selectedItem?.userId || null, // user_id のみを送信
    };

    console.log('検索パラメータ:', searchParams);
    // 実際の検索処理を実行
    // await searchAPI(searchParams);
};

// マウント時に権限エラーチェック
onMounted(() => {
    if (route.query.unauthorized === 'admin') {
        showWarning('notifications.unauthorized.admin');
        router.replace({ name: ROUTE_NAMES.HOME, query: {} });
    }

    // データ読み込み
    userSelectItems.value = mockUserSelectData;
    // 実際の実装では API 呼び出し
    // fetchUserSelectData();
});

const menuItems = computed(() => [
    {
        id: 'admin',
        icon: ICONS.nav.management,
        title: t('pages.admin.title'),
        to: { name: ROUTE_NAMES.ADMIN.MENU },
        color: 'secondary',
        requiresAdmin: true,
    },
    {
        id: 'settings',
        icon: ICONS.nav.settings,
        title: t('pages.settings.title'),
        to: { name: ROUTE_NAMES.SETTINGS },
        color: COLORS.neutral.medium,
    },
]);

// 管理者権限が必要なメニューをフィルタリング
const filteredMenuItems = computed(() => {
    return menuItems.value.filter((item) => {
        if (item.requiresAdmin) {
            return isAdmin.value;
        }
        return true;
    });
});
</script>

<template>
    <Header :app-title="t('pages.home.title')" />

    <!-- グループ化セレクトボックス -->
    <v-container>
        <v-row>
            <v-col cols="12" md="6">
                <v-card>
                    <v-card-title>グループ化セレクト サンプル</v-card-title>
                    <v-card-text>
                        <!-- v-select 本体 -->
                        <v-select
                            v-model="selectedUserId"
                            :items="userSelectItems"
                            item-value="value"
                            item-title="label"
                            label="登録者"
                            clearable
                            density="comfortable"
                            variant="outlined"
                        >
                            <!-- ドロップダウンリストの表示制御 -->
                            <template #item="{ props, item }">
                                <!-- グループヘッダー -->
                                <v-list-subheader
                                    v-if="item.raw.type === 'group'"
                                    class="font-weight-bold text-grey-darken-2"
                                >
                                    {{ item.raw.label }}
                                </v-list-subheader>

                                <!-- ユーザー項目（インデント） -->
                                <v-list-item
                                    v-else-if="item.raw.type === 'user'"
                                    v-bind="props"
                                    class="pl-8"
                                />

                                <!-- 全ての場合（インデントなし） -->
                                <v-list-item v-else v-bind="props" />
                            </template>

                            <!-- 選択後の表示制御（これがないとグループヘッダーも表示される） -->
                            <template #selection="{ item }">
                                <!-- グループヘッダーは表示しない -->
                                <span v-if="item.raw.type !== 'group'">
                                    {{ item.raw.label }}
                                </span>
                            </template>
                        </v-select>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>

    <MenuCardGrid :items="filteredMenuItems" />
</template>

<style scoped>
/* グループヘッダー用のスタイル */
.group-header {
    background-color: rgb(245, 245, 245);
    pointer-events: none;
}

/* Vuetify3 の pl-8 が効かない場合の補助 */
.pl-8 {
    padding-left: 32px !important;
}
</style>
