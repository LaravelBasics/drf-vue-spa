<template>
    <Header
        :app-title="t('pages.userManagement.title')"
        :page-buttons="headerButtons"
        :breadcrumbs="breadcrumbs"
    ></Header>

    <v-container fluid class="pa-6">
        <!-- 検索・操作エリア -->
        <v-row class="mb-4">
            <v-col cols="12" md="8">
                <v-text-field
                    v-model="searchQuery"
                    :label="t('pages.userManagement.searchPlaceholder')"
                    prepend-inner-icon="mdi-magnify"
                    variant="outlined"
                    clearable
                    @input="handleSearch"
                />
            </v-col>
            <v-col cols="12" md="4" class="d-flex align-end justify-end">
                <v-btn
                    color="primary"
                    size="large"
                    @click="navigateToCreate"
                    class="mb-1"
                >
                    <v-icon class="me-2">mdi-plus</v-icon>
                    {{ t('pages.userManagement.createUser') }}
                </v-btn>
            </v-col>
        </v-row>

        <!-- データテーブル -->
        <v-data-table
            :headers="headers"
            :items="filteredUsers"
            :loading="loading"
            :items-per-page="10"
            class="elevation-1"
        >
            <!-- 管理者フラグ表示 -->
            <template v-slot:item.is_admin="{ item }">
                <v-chip
                    :color="item.is_admin ? 'success' : 'default'"
                    size="small"
                    variant="flat"
                >
                    {{ item.is_admin ? t('common.yes') : t('common.no') }}
                </v-chip>
            </template>

            <!-- 登録日表示 -->
            <template v-slot:item.created_at="{ item }">
                {{ formatDate(item.created_at) }}
            </template>

            <!-- アクション -->
            <template v-slot:item.actions="{ item }">
                <v-btn
                    icon="mdi-pencil"
                    size="small"
                    variant="text"
                    color="primary"
                    @click="navigateToEdit(item.id)"
                    class="me-2"
                />
                <v-btn
                    icon="mdi-delete"
                    size="small"
                    variant="text"
                    color="error"
                    @click="navigateToDelete(item.id)"
                />
            </template>
        </v-data-table>
    </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import Header from '@/components/Header.vue';
import { userAPI } from '@/api/user';

const router = useRouter();
const { t } = useI18n();

// リアクティブデータ
const users = ref([]);
const loading = ref(false);
const searchQuery = ref('');

// パンくずリスト
const breadcrumbs = computed(() => [
    {
        title: t('nav.home'),
        to: '/',
        disabled: false,
    },
    {
        title: t('nav.management'),
        to: '/management',
        disabled: false,
    },
    {
        title: t('pages.userManagement.title'),
        disabled: true,
    },
]);

// ヘッダーボタン
const headerButtons = [
    {
        name: t('common.refresh'),
        action: fetchUsers,
        icon: 'mdi-refresh',
        type: 'primary',
    },
];

// テーブルヘッダー
const headers = computed(() => [
    { title: 'ID', key: 'id', sortable: true, width: 80 },
    { title: t('form.fields.username'), key: 'username', sortable: true },
    { title: t('form.fields.employeeId'), key: 'employee_id', sortable: true },
    {
        title: t('form.fields.isAdmin'),
        key: 'is_admin',
        sortable: true,
        width: 120,
    },
    {
        title: t('form.fields.createdAt'),
        key: 'created_at',
        sortable: true,
        width: 150,
    },
    { title: t('common.actions'), key: 'actions', sortable: false, width: 120 },
]);

// フィルタリングされたユーザー一覧
const filteredUsers = computed(() => {
    if (!searchQuery.value) return users.value;

    return users.value.filter((user) =>
        user.username.toLowerCase().includes(searchQuery.value.toLowerCase()),
    );
});

// メソッド
async function fetchUsers() {
    loading.value = true;
    try {
        const response = await userAPI.list();
        users.value = response.data;
    } catch (error) {
        console.error('ユーザー一覧取得エラー:', error);
    } finally {
        loading.value = false;
    }
}

function handleSearch() {
    // リアルタイム検索は computed で処理済み
}

function navigateToCreate() {
    router.push('/users/create');
}

function navigateToEdit(userId) {
    router.push(`/users/${userId}/edit`);
}

function navigateToDelete(userId) {
    router.push(`/users/${userId}/delete`);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ja-JP');
}

// マウント時にデータ取得
onMounted(() => {
    fetchUsers();
});
</script>
