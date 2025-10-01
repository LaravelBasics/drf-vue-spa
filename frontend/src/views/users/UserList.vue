<template>
    <div>
        <Header
            :app-title="t('pages.users.title')"
            :breadcrumbs="breadcrumbs"
        />

        <v-container fluid class="pa-6">
            <!-- 検索・操作エリア -->
            <v-row class="mb-4">
                <v-col>
                    <v-text-field
                        v-model="searchQuery"
                        :label="t('pages.users.searchPlaceholder')"
                        prepend-inner-icon="mdi-magnify"
                        variant="outlined"
                        density="comfortable"
                        clearable
                        hide-details
                        @update:model-value="handleSearchInput"
                    >
                        <!-- 検索中インジケーター -->
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
                <v-col class="d-flex align-end justify-end">
                    <v-btn
                        color="primary"
                        size="large"
                        prepend-icon="mdi-plus"
                        @click="goToCreate"
                    >
                        {{ t('pages.users.createButton') }}
                    </v-btn>
                </v-col>
            </v-row>

            <!-- データテーブル -->
            <v-data-table
                :headers="headers"
                :items="users"
                :loading="loading"
                :items-per-page="itemsPerPage"
                :items-length="totalItems"
                :page="currentPage"
                class="elevation-2 user-table"
                @update:page="handlePageChange"
                @update:items-per-page="handleItemsPerPageChange"
            >
                <!-- No列（index+1） -->
                <template v-slot:item.id="{ item, index }">
                    <span class="font-weight-medium">
                        {{ (currentPage - 1) * itemsPerPage + index + 1 }}
                    </span>
                </template>

                <!-- 管理者フラグ -->
                <template v-slot:item.is_admin="{ item }">
                    <v-chip
                        :color="item.is_admin ? 'success' : 'default'"
                        size="small"
                        variant="flat"
                    >
                        <v-icon
                            :icon="
                                item.is_admin
                                    ? 'mdi-shield-check'
                                    : 'mdi-account'
                            "
                            size="small"
                            class="mr-1"
                        />
                        {{
                            item.is_admin ? t('common.admin') : t('common.user')
                        }}
                    </v-chip>
                </template>

                <!-- 登録日 -->
                <template v-slot:item.created_at="{ item }">
                    {{ formatDate(item.created_at) }}
                </template>

                <!-- アクション列 -->
                <template v-slot:item.actions="{ item }">
                    <div class="d-flex gap-2">
                        <v-btn
                            icon="mdi-pencil"
                            size="small"
                            variant="text"
                            color="primary"
                            @click="goToEdit(item.id)"
                        >
                            <v-icon>mdi-pencil</v-icon>
                            <v-tooltip activator="parent" location="top">
                                {{ t('common.edit') }}
                            </v-tooltip>
                        </v-btn>

                        <v-btn
                            icon="mdi-delete"
                            size="small"
                            variant="text"
                            color="error"
                            @click="goToDelete(item.id)"
                            :disabled="!canDelete(item)"
                        >
                            <v-icon>mdi-delete</v-icon>
                            <v-tooltip activator="parent" location="top">
                                {{
                                    canDelete(item)
                                        ? t('common.delete')
                                        : t('pages.users.cannotDeleteLastAdmin')
                                }}
                            </v-tooltip>
                        </v-btn>
                    </div>
                </template>
            </v-data-table>
        </v-container>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { routes } from '@/constants/routes';

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
        title: t('pages.users.title'),
        disabled: true,
    },
]);

// テーブルヘッダー
const headers = computed(() => [
    {
        title: 'ID',
        key: 'id',
        sortable: false,
        width: 80,
    },
    {
        title: t('form.fields.username'),
        key: 'username',
        sortable: false,
    },
    {
        title: t('form.fields.employeeId'),
        key: 'employee_id',
        sortable: false,
    },
    {
        title: t('form.fields.isAdmin'),
        key: 'is_admin',
        sortable: false,
    },
    {
        title: t('form.fields.createdAt'),
        key: 'created_at',
        sortable: false,
    },
    {
        title: t('common.actions'),
        key: 'actions',
        sortable: false,
        width: 120,
    },
]);

// データ取得（サーバーサイド）
async function fetchUsers() {
    loading.value = true;
    try {
        const params = {
            page: currentPage.value,
            page_size: itemsPerPage.value,
        };

        // 検索クエリがある場合のみ追加
        if (searchQuery.value && searchQuery.value.trim()) {
            params.search = searchQuery.value.trim();
        }

        const response = await usersAPI.list(params);

        // DRF のページネーション形式に対応
        if (response.data.results) {
            users.value = response.data.results;
            totalItems.value = response.data.count;
        } else {
            // ページネーションなしの場合
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

// 検索入力ハンドラー（デバウンス）
function handleSearchInput(value) {
    searching.value = true;

    // 既存のタイマーをクリア
    if (searchTimer) {
        clearTimeout(searchTimer);
    }

    // 500ms 待機してから検索実行
    searchTimer = setTimeout(() => {
        currentPage.value = 1; // 検索時はページをリセット
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

// 表示件数変更ハンドラー
function handleItemsPerPageChange(perPage) {
    itemsPerPage.value = perPage;
    currentPage.value = 1;
    fetchUsers();
    updateURLParams();
}

// URL パラメータを更新（ブックマーク対応）
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
}

// 削除可能かチェック
function canDelete(user) {
    if (!user.is_admin) return true;

    const adminCount = users.value.filter(
        (u) => u.is_admin && u.is_active,
    ).length;
    return adminCount > 1;
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

// ナビゲーション
function goToCreate() {
    router.push(routes.USER_CREATE);
}

function goToEdit(id) {
    router.push(routes.USER_EDIT.replace(':id', id));
}

function goToDelete(id) {
    router.push(routes.USER_DELETE.replace(':id', id));
}

onMounted(() => {
    initFromURLParams();
    fetchUsers();
});
</script>

<style scoped>
.gap-2 {
    gap: 8px;
}

.user-table {
    /* データが少なくても、最低でも300pxの高さを確保する */
    min-height: 425px;
}
</style>
