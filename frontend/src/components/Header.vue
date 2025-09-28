<template>
    <v-app-bar color="grey-lighten-5" elevation="4" :height="headerHeight" app>
        <v-app-bar-title class="d-flex align-center">
            <span class="text-h6 font-weight-bold">{{ appTitle }}</span>
        </v-app-bar-title>

        <v-btn
            v-for="(button, index) in props.pageButtons"
            :key="index"
            variant="outlined"
            color="grey-darken-3"
            class="mx-3 px-2 text-subtitle-2"
            @click="button.action"
        >
            <v-icon :icon="button.icon"></v-icon>
            {{ button.name }}
        </v-btn>
    </v-app-bar>
</template>

<script setup>
const props = defineProps({
    appTitle: {
        type: String,
        default: 'デフォルトのタイトル名',
    },
    headerHeight: {
        type: [String, Number],
        default: 56,
    },
    pageButtons: {
        type: Array,
        default: () => [],
    },
});
</script>
