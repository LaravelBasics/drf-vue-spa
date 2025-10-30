<script setup>
const props = defineProps({
    icon: {
        type: String,
        required: true,
    },
    title: {
        type: String,
        required: true,
    },
    to: {
        type: [String, Object],
        default: null,
    },
    href: {
        type: String,
        default: null,
    },
    color: {
        type: String,
        default: 'primary',
    },
    iconSize: {
        type: [String, Number],
        default: 64,
    },
});

const emit = defineEmits(['click']);

// toやhrefが設定されていない場合のみカスタムイベントを発火
const handleClick = (event) => {
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
        tabindex="0"
        @click="handleClick"
        @keydown.enter.prevent="handleClick"
        @keydown.space.prevent.stop="handleClick"
    >
        <v-card-text
            class="d-flex flex-column align-center justify-center pa-6"
        >
            <v-icon
                :icon="icon"
                :color="color"
                :size="iconSize"
                class="mt-1 mb-3"
            ></v-icon>
            <div class="text-subtitle-1 font-weight-medium text-center">
                {{ title }}
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.menu-card {
    /* min-width: 200px; */
    max-width: 200px;
    aspect-ratio: 4/3;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.menu-card:hover {
    transform: translateY(-4px);
}

/* キーボードフォーカス時のアウトライン表示 */
.menu-card:focus {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 2px;
}
</style>
