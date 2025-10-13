<script setup>
const props = defineProps({
    // ⭐ Material Symbols アイコン名（admin_panel_settings など）
    icon: {
        type: String,
        required: true,
    },
    // カードのタイトル（2〜4文字）
    title: {
        type: String,
        required: true,
    },
    // ルーティング用（vue-router）
    to: {
        type: [String, Object],
        default: null,
    },
    // 外部リンク用
    href: {
        type: String,
        default: null,
    },
    // アイコンの色
    color: {
        type: String,
        default: 'primary',
    },
    // アイコンサイズ
    iconSize: {
        type: [String, Number],
        default: 64,
    },
});

const emit = defineEmits(['click']);

const handleClick = (event) => {
    // toやhrefが設定されていない場合のみemit
    if (!props.to && !props.href) {
        emit('click', event);
    }
};
</script>

<template>
    <v-card
        :to="to"
        :href="href"
        class="menu-card"
        elevation="2"
        hover
        @click="handleClick"
    >
        <v-card-text
            class="d-flex flex-column align-center justify-center pa-6"
        >
            <v-icon
                :icon="icon"
                :color="color"
                :size="iconSize"
                class="mb-3"
            ></v-icon>
            <div class="text-subtitle-1 font-weight-medium text-center">
                {{ title }}
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.menu-card {
    min-width: 160px;
    max-width: 200px;
    aspect-ratio: 4/3;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.menu-card:hover {
    transform: translateY(-4px);
}
</style>
