<template>
    <div>
        <Header
            :app-title="t('pages.users.title')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container fluid class="pa-4">
            <!-- 検索・操作エリア -->

            <v-row class="mb-1 align-center">
                <v-col cols="12" sm="5" md="3">
                    <v-text-field
                        v-model="searchQuery"
                        :label="t('pages.users.searchPlaceholder')"
                        :prepend-inner-icon="ICONS.action.search"
                        variant="outlined"
                        density="compact"
                        clearable
                        hide-details
                        @update:model-value="handleSearchInput"
                    >
                        <template v-slot:append-inner v-if="searching">
                            <v-progress-circular
                                indeterminate
                                size="20"
                                width="2"
                                color="primary"
                            />
                        </template>
                    </v-text-field>
                </v-col>

                <v-col cols="12" sm="4" md="3">
                    <div class="text-body-2 text-grey-darken-1">
                        {{ startItem }}-{{ endItem }} / {{ totalItems }}件
                    </div>
                </v-col>

                <v-spacer />

                <v-col cols="12" sm="3" md="3" class="d-flex justify-end">
                    <v-btn
                        variant="outlined"
                        color="primary"
                        size="default"
                        :prepend-icon="ICONS.action.add"
                        @click="goToCreate"
                    >
                        {{ t('pages.users.createButton') }}
                    </v-btn>
                </v-col>
            </v-row>

            <!-- データテーブル -->
            <v-data-table-server
                :headers="headers"
                :items="users"
                :items-length="totalItems"
                :loading="loading"
                v-model:items-per-page="itemsPerPage"
                v-model:page="currentPage"
                v-model:sort-by="sortBy"
                class="elevation-2 clickable-table"
                density="compact"
                hover
                hide-default-footer
                @update:options="handleOptionsUpdate"
                @click:row="handleRowClick"
            >
                <!-- ID列 -->
                <template v-slot:item.id="{ item }">
                    <RouterLink
                        :to="routes.USER_DETAIL.replace(':id', item.id)"
                        class="font-weight-medium text-decoration-none text-primary"
                        aria-label="ユーザー詳細へ移動"
                        @click.stop
                    >
                        {{ item.id }}
                    </RouterLink>
                </template>

                <!-- 管理者フラグ -->
                <template v-slot:item.is_admin="{ item }">
                    <v-icon
                        :color="item.is_admin ? 'success' : 'grey'"
                        :size="item.is_admin ? 'default' : 'small'"
                    >
                        {{
                            item.is_admin
                                ? ICONS.status.check
                                : ICONS.status.minus
                        }}
                    </v-icon>
                </template>

                <!-- 登録日 -->
                <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                </template>
            </v-data-table-server>

            <!-- ページネーション -->
            <div class="d-flex justify-center mt-4">
                <v-pagination
                    v-model="currentPage"
                    :length="totalPages"
                    :total-visible="7"
                    @update:model-value="handlePageChange"
                />
            </div>
        </v-container>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons.js';

const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const users = ref([]);
const loading = ref(false);
const searching = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalItems = ref(0);
const sortBy = ref([]);

// デバウンス用タイマー
let searchTimer = null;

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('nav.home'),
        to: routes.HOME,
        disabled: false,
    },
    {
        title: t('pages.admin.title'),
        to: routes.ADMIN,
        disabled: false,
    },
    {
        title: t('pages.users.title'),
        disabled: true,
    },
]);

// テーブルヘッダー（ソート可能）
const headers = computed(() => [
    {
        title: 'ID',
        key: 'id',
        sortable: true,
        width: 80,
    },
    {
        title: t('form.fields.username'),
        key: 'username',
        sortable: true,
    },
    {
        title: t('form.fields.employeeId'),
        key: 'employee_id',
        sortable: true,
    },
    {
        title: t('form.fields.isAdmin'),
        key: 'is_admin',
        sortable: true,
        align: 'center',
    },
    {
        title: t('form.fields.createdAt'),
        key: 'created_at',
        sortable: true,
    },
]);

// ページ数計算
const totalPages = computed(() =>
    Math.ceil(totalItems.value / itemsPerPage.value),
);

// 表示範囲計算
const startItem = computed(() => {
    if (totalItems.value === 0) return 0;
    return (currentPage.value - 1) * itemsPerPage.value + 1;
});

const endItem = computed(() => {
    return Math.min(currentPage.value * itemsPerPage.value, totalItems.value);
});

// データ取得
async function fetchUsers() {
    loading.value = true;
    try {
        const params = {
            page: currentPage.value,
            page_size: itemsPerPage.value,
        };

        // 検索クエリ
        if (searchQuery.value && searchQuery.value.trim()) {
            params.search = searchQuery.value.trim();
        }

        // ソート条件
        if (sortBy.value.length > 0) {
            const sort = sortBy.value[0];
            const orderPrefix = sort.order === 'desc' ? '-' : '';
            params.ordering = `${orderPrefix}${sort.key}`;
        }

        const response = await usersAPI.list(params);

        if (response.data.results) {
            users.value = response.data.results;
            totalItems.value = response.data.count;
        } else {
            users.value = response.data;
            totalItems.value = response.data.length;
        }
    } catch (error) {
        console.error('ユーザー一覧取得エラー:', error);
    } finally {
        loading.value = false;
        searching.value = false;
    }
}

// v-data-table-serverのoptionsハンドラー
function handleOptionsUpdate(options) {
    currentPage.value = options.page;
    itemsPerPage.value = options.itemsPerPage;
    sortBy.value = options.sortBy;

    fetchUsers();
    updateURLParams();
}

// 検索入力ハンドラー
function handleSearchInput(value) {
    searching.value = true;

    if (searchTimer) {
        clearTimeout(searchTimer);
    }

    searchTimer = setTimeout(() => {
        currentPage.value = 1;
        fetchUsers();
        updateURLParams();
    }, 500);
}

// ページ変更ハンドラー
function handlePageChange(page) {
    currentPage.value = page;
    fetchUsers();
    updateURLParams();
}

// URL パラメータ更新
function updateURLParams() {
    const query = {};

    if (searchQuery.value && searchQuery.value.trim()) {
        query.search = searchQuery.value.trim();
    }

    if (currentPage.value > 1) {
        query.page = currentPage.value;
    }

    if (itemsPerPage.value !== 10) {
        query.per_page = itemsPerPage.value;
    }

    // ソート条件
    if (sortBy.value.length > 0) {
        const sort = sortBy.value[0];
        query.sort = sort.key;
        query.order = sort.order;
    }

    router.replace({ query });
}

// URL パラメータから初期化
function initFromURLParams() {
    const query = route.query;

    if (query.search) {
        searchQuery.value = query.search;
    }

    if (query.page) {
        currentPage.value = parseInt(query.page);
    }

    if (query.per_page) {
        itemsPerPage.value = parseInt(query.per_page);
    }

    // ソート条件復元
    if (query.sort && query.order) {
        sortBy.value = [
            {
                key: query.sort,
                order: query.order,
            },
        ];
    }
}

// 日付フォーマット
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
}

// 新規作成画面へ遷移
function goToCreate() {
    router.push(routes.USER_CREATE);
}

// 行クリックで詳細画面へ遷移
function handleRowClick(event, { item }) {
    router.push(routes.USER_DETAIL.replace(':id', item.id));
}

onMounted(() => {
    initFromURLParams();
    fetchUsers();
});
</script>

<style scoped>
/* 行をクリック可能に */
:deep(.clickable-table tbody tr) {
    cursor: pointer;
    position: relative;
}

/* ホバー時のツールチップ（プライマリカラー） */
:deep(.clickable-table tbody tr:hover::after) {
    content: '詳細を表示';
    position: absolute;
    right: 12px; /* 右端からのパディング */
    top: 50%;
    transform: translateY(-50%); /* 垂直方向の中央寄せは維持 */
    background-color: rgb(var(--v-theme-primary));
    color: white;
    padding: 6px 12px;
    border-radius: 4px;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: 500;
    pointer-events: none;
    white-space: nowrap;
    z-index: 1;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }

    to {
        opacity: 1;
    }
}
</style>
