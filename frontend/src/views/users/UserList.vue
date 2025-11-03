<!-- src/views/users/UserList.vue - ユーザー一覧画面 -->
<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { userRoutes } from '@/constants/routes'; // ✅ userRoutesをインポート
import { ICONS } from '@/constants/icons.js';
import { useDisplay } from 'vuetify';
import { useApiError } from '@/composables/useApiError';

const { mdAndUp } = useDisplay();
const router = useRouter();
const route = useRoute();
const { t } = useI18n();
const { handleApiError, showSuccess } = useApiError();

const users = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const totalItems = ref(0);
const currentPage = ref(1);
const itemsPerPage = ref(10);
const sortBy = ref([]);
const csvExporting = ref(false);

let searchTimer = null;

const headerButtons = computed(() => [
    {
        name: t('buttons.csv'),
        action: exportCSV,
        icon: ICONS.buttons.csv,
        type: 'success',
        loading: csvExporting.value,
    },
]);

// レスポンシブ対応: PC画面では作成日時も表示
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

    if (mdAndUp.value) {
        baseHeaders.push({
            title: t('form.fields.createdAt'),
            key: 'created_at',
            sortable: true,
        });
    }

    return baseHeaders;
});

const noDataText = computed(() => t('dataTable.noData'));
const loadingText = computed(() => t('dataTable.loading'));

const itemCountText = computed(() => {
    if (totalItems.value === 0) {
        return t('dataTable.itemCount', {
            start: 0,
            end: 0,
            total: 0,
        });
    }

    const start = (currentPage.value - 1) * itemsPerPage.value + 1;
    const end = Math.min(
        currentPage.value * itemsPerPage.value,
        totalItems.value,
    );

    return t('dataTable.itemCount', {
        start,
        end,
        total: totalItems.value,
    });
});

const hoverTooltipText = computed(() => {
    const text = t('tooltips.viewDetails');
    return `"${text}"`;
});

// ページネーション用の総ページ数
const totalPages = computed(() => {
    return Math.ceil(totalItems.value / itemsPerPage.value);
});

// データ取得処理（ページネーション、ソート、検索対応）
async function loadItems({ page, itemsPerPage, sortBy }) {
    if (loading.value) {
        return;
    }

    loading.value = true;

    try {
        const params = {
            page,
            page_size: itemsPerPage,
        };

        if (searchQuery.value?.trim()) {
            params.search = searchQuery.value.trim();
        }

        if (sortBy && sortBy.length > 0) {
            const sort = sortBy[0];
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

        updateURLParams({ page, itemsPerPage, sortBy });
    } catch (error) {
        handleApiError(error);
    } finally {
        loading.value = false;
    }
}

// CSV出力処理
async function exportCSV() {
    if (csvExporting.value) {
        return;
    }

    csvExporting.value = true;

    try {
        // 現在の検索・ソート条件を取得
        const params = {};

        if (searchQuery.value?.trim()) {
            params.search = searchQuery.value.trim();
        }

        if (sortBy.value && sortBy.value.length > 0) {
            const sort = sortBy.value[0];
            const orderPrefix = sort.order === 'desc' ? '-' : '';
            params.ordering = `${orderPrefix}${sort.key}`;
        }

        const response = await usersAPI.exportCSV(params);

        // Blobを作成してダウンロード
        const blob = new Blob([response.data], {
            type: 'text/csv; charset=utf-8-sig',
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;

        // ファイル名に日時を含める
        const now = new Date();
        const dateStr = now
            .toLocaleDateString('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
            })
            .replace(/\//g, '');
        const timeStr = now
            .toLocaleTimeString('ja-JP', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: false,
            })
            .replace(/:/g, '');

        link.download = `users_${dateStr}_${timeStr}.csv`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        showSuccess('pages.users.list.csvExportSuccess');
    } catch (error) {
        // Blobエラーレスポンスの場合はJSONに変換
        if (error.response && error.response.data instanceof Blob) {
            try {
                const text = await error.response.data.text();
                const jsonError = JSON.parse(text);
                // エラーオブジェクトを更新
                error.response.data = jsonError;
            } catch (e) {
                console.error('Failed to parse error response:', e);
            }
        }

        handleApiError(error);
    } finally {
        csvExporting.value = false;
    }
}

// 検索クエリ変更時の処理（デバウンス: 300ms）
watch(searchQuery, () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
        currentPage.value = 1;
        loadItems({
            page: 1,
            itemsPerPage: itemsPerPage.value,
            sortBy: sortBy.value,
        });
    }, 300);
});

// URLパラメータにフィルタ条件を保存
function updateURLParams({ page, itemsPerPage, sortBy }) {
    const query = {};

    if (searchQuery.value?.trim()) {
        query.search = searchQuery.value.trim();
    }

    if (page > 1) {
        query.page = page;
    }

    if (itemsPerPage !== 10) {
        query.per_page = itemsPerPage;
    }

    if (sortBy && sortBy.length > 0) {
        const sort = sortBy[0];
        query.sort = sort.key;
        query.order = sort.order;
    }

    router.replace({ query });
}

// URLパラメータから初期状態を復元
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

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    });
}

function goToCreate() {
    router.push(userRoutes.create()); // ✅ ヘルパー関数を使用
}

function handleRowClick(event, { item }) {
    router.push(userRoutes.detail(item.id)); // ✅ ヘルパー関数を使用
}

onMounted(() => {
    initFromURLParams();

    loadItems({
        page: currentPage.value,
        itemsPerPage: itemsPerPage.value,
        sortBy: sortBy.value,
    });
});

// クリーンアップ（メモリリーク対策）
onBeforeUnmount(() => {
    if (searchTimer) {
        clearTimeout(searchTimer);
        searchTimer = null;
    }
});
</script>

<template>
    <div>
        <Header
            :app-title="t('pages.users.list.title')"
            :page-buttons="headerButtons"
        />

        <v-container fluid class="pa-4">
            <v-row class="mb-1 align-center">
                <v-col cols="12" sm="5" md="3">
                    <v-text-field
                        v-model="searchQuery"
                        :label="t('pages.users.list.searchPlaceholder')"
                        :prepend-inner-icon="ICONS.buttons.search"
                        variant="outlined"
                        density="default"
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
                        {{ t('buttons.users.list.create') }}
                    </v-btn>
                </v-col>
            </v-row>

            <v-data-table-server
                :headers="headers"
                :items="users"
                :items-length="totalItems"
                :loading="loading"
                :no-data-text="noDataText"
                :loading-text="loadingText"
                :items-per-page-options="[10, 25, 50, 100]"
                v-model:page="currentPage"
                v-model:items-per-page="itemsPerPage"
                v-model:sort-by="sortBy"
                class="elevation-2 clickable-table"
                density="default"
                hover
                hide-default-footer
                @update:options="loadItems"
                @click:row="handleRowClick"
            >
                <!-- ✅ IDカラムのリンクもヘルパー関数を使用 -->
                <template v-slot:item.id="{ item }">
                    <RouterLink
                        :to="userRoutes.detail(item.id)"
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
        </v-container>
        <!-- 外部ページネーション -->
        <div class="d-flex justify-center">
            <v-pagination
                v-model="currentPage"
                :length="totalPages"
                :total-visible="3"
                density="default"
            />
        </div>
    </div>
</template>

<style scoped>
:deep(.clickable-table tbody tr) {
    cursor: pointer;
    position: relative;
}

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
