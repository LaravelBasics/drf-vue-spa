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
        default: 64, // ✅ デフォルト値を明確に
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
        @click="handleClick"
        @keydown.enter.prevent="handleClick"
        @keydown.space.prevent.stop="handleClick"
    >
        <v-card-text
            class="py-6 d-flex flex-column align-center justify-center ga-3"
        >
            <v-icon :icon="icon" :color="color" :size="iconSize" />
            <div class="text-h6 font-weight-medium text-center">
                {{ title }}
            </div>
        </v-card-text>
    </v-card>
</template>

<style scoped>
.menu-card {
    min-height: 160px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-card:hover {
    transform: translateY(-4px);
}

.menu-card:focus-visible {
    outline: 2px solid rgb(var(--v-theme-primary));
    outline-offset: 2px;
}
</style>
