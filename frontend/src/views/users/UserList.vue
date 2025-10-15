<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';
import { ICONS } from '@/constants/icons.js';
import { useDisplay } from 'vuetify';

const { mdAndUp } = useDisplay();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const users = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const currentPage = ref(1);
const itemsPerPage = ref(10);
const totalItems = ref(0);
const sortBy = ref([]);

// ⭐ デバウンス用タイマー
let searchTimer = null;

const headerButtons = computed(() => [
    {
        name: t('buttons.csv'),
        action: exportCSV,
        icon: ICONS.buttons.csv,
        type: 'success',
    },
]);

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('breadcrumbs.home'),
        to: routes.HOME,
        disabled: false,
    },
    {
        title: t('breadcrumbs.admin'),
        to: routes.ADMIN,
        disabled: false,
    },
    {
        title: t('breadcrumbs.users.list'),
        disabled: true,
    },
]);

// テーブルヘッダー（ソート可能）
const headers = computed(() => {
    const baseHeaders = [
        { title: t('form.fields.id'), key: 'id', sortable: true },
        { title: t('form.fields.username'), key: 'username', sortable: false },
        {
            title: t('form.fields.employeeId'),
            key: 'employee_id',
            sortable: true,
        },
        { title: t('form.fields.isAdmin'), key: 'is_admin', sortable: true },
    ];

    // ⭐ タブレット以上の場合のみ追加
    if (mdAndUp.value) {
        baseHeaders.push({
            title: t('form.fields.createdAt'),
            key: 'created_at',
            sortable: true,
        });
    }

    return baseHeaders;
});

// ⭐ 修正後：t()に置き換え
const noDataText = computed(() => t('dataTable.noData'));
const loadingText = computed(() => t('dataTable.loading'));

const itemCountText = computed(() => {
    return t('dataTable.itemCount', {
        start: startItem.value,
        end: endItem.value,
        total: totalItems.value,
    });
});

// ⭐ ホバー時のツールチップテキスト（言語対応）
const hoverTooltipText = computed(() => {
    const text = t('tooltips.viewDetails');
    return `"${text}"`;
});

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

// ⭐ watch: 検索クエリの変更を監視してデバウンス処理
watch(searchQuery, () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        currentPage.value = 1;
        fetchUsers();
        updateURLParams();
    }, 1000);
});

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

function exportCSV() {
    console.log('Export CSV');
}

onMounted(() => {
    initFromURLParams();
    fetchUsers();
});
</script>

<template>
    <div>
        <Header
            :app-title="t('pages.users.list.title')"
            :page-buttons="headerButtons"
            :breadcrumbs="breadcrumbs"
        />

        <v-container fluid class="pa-4">
            <v-row class="mb-1 align-center">
                <v-col cols="12" sm="5" md="3">
                    <v-text-field
                        v-model="searchQuery"
                        :label="t('pages.users.list.searchPlaceholder')"
                        :prepend-inner-icon="ICONS.buttons.search"
                        variant="outlined"
                        density="compact"
                        hide-details
                    >
                        <template v-slot:append-inner>
                            <v-progress-circular
                                v-if="loading"
                                indeterminate
                                size="20"
                                width="2"
                                color="primary"
                            />
                            <v-icon
                                v-else-if="searchQuery"
                                icon="close"
                                size="small"
                                class="cursor-pointer"
                                @click="searchQuery = ''"
                            />
                        </template>
                    </v-text-field>
                </v-col>

                <v-col cols="12" sm="4" md="3">
                    <div class="text-body-2 text-grey-darken-1">
                        {{ itemCountText }}
                    </div>
                </v-col>

                <v-spacer />

                <v-col cols="12" sm="3" md="3" class="d-flex justify-end">
                    <v-btn
                        variant="outlined"
                        color="primary"
                        size="default"
                        :prepend-icon="ICONS.buttons.arrowForward"
                        @click="goToCreate"
                    >
                        {{ t('pages.users.list.createButton') }}
                    </v-btn>
                </v-col>
            </v-row>

            <!-- ⭐ no-data-text と loading-text を追加 -->
            <v-data-table-server
                :headers="headers"
                :items="users"
                :items-length="totalItems"
                :loading="loading"
                :no-data-text="noDataText"
                :loading-text="loadingText"
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
                <template v-slot:item.id="{ item }">
                    <RouterLink
                        :to="routes.USER_DETAIL.replace(':id', item.id)"
                        class="font-weight-medium text-decoration-none text-primary"
                        @click.stop
                    >
                        {{ item.id }}
                    </RouterLink>
                </template>

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

                <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                </template>
            </v-data-table-server>

            <div class="d-flex justify-center mt-4">
                <v-pagination
                    v-model="currentPage"
                    :length="totalPages"
                    :total-visible="5"
                    density="compact"
                    @update:model-value="handlePageChange"
                />
            </div>
        </v-container>
    </div>
</template>

<style scoped>
:deep(.clickable-table tbody tr) {
    cursor: pointer;
    position: relative;
}

/* ⭐ CSSカスタムプロパティでツールチップテキストを動的に変更 */
:deep(.clickable-table tbody tr:hover::after) {
    content: v-bind(hoverTooltipText);
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background-color: rgb(var(--v-theme-primary));
    color: white;
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
