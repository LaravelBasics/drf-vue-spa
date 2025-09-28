<template>
    <Header app-title="テスト"></Header>
    <v-container>
        <v-row justify="center">
            <v-col cols="12" md="8">
                <v-card class="pa-6" color="blue-grey-lighten-5">
                    <v-card-title class="text-center">
                        <v-icon size="64" color="blue-darken-2"
                            >mdi-account</v-icon
                        >
                        <div class="text-h4 font-weight-bold mt-2">
                            プロフィール
                        </div>
                    </v-card-title>
                    <v-card-text class="text-center">
                        <p class="text-body-1">
                            ユーザープロフィール管理ページです
                        </p>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import Header from '@/components/Header.vue';
</script>
