<template>
    <v-container>
        <Header app-title="カスタムアプリ名"></Header>
        <v-row>
            <v-col>
                <v-card class="pa-6" color="blue-grey-lighten-5">
                    <v-row justify="center">
                        <v-col
                            cols="auto"
                            class="d-flex flex-column align-center"
                        >
                            <v-icon size="64" color="indigo-darken-2">
                                mdi-atom
                            </v-icon>
                            <v-card-title class="text-h5 font-weight-bold mt-2">
                                ログイン成功！
                            </v-card-title>
                        </v-col>
                    </v-row>
                    <v-card-text class="text-center text-body-1">
                        このページから、各種サービスをご利用いただけます。
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script setup>
import Header from '@/components/Header.vue';
</script>
