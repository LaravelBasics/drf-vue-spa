<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { ROUTE_NAMES } from '@/constants/routes';
import { useI18n } from 'vue-i18n';
import { useValidation } from '@/composables/useValidation';
import { useApiError } from '@/composables/useApiError';
import Header from '@/components/Header.vue';
import { usersAPI } from '@/api/users';
import { ICONS } from '@/constants/icons';

const router = useRouter();
const { t } = useI18n();
const { createRules } = useValidation();
const { showSuccess, handleApiError } = useApiError();

const submitting = ref(false);
const form = ref(null);
const usernameField = ref(null);

const formData = ref({
    username: '',
    employee_id: '',
    password: '',
    is_admin: false,
});

const usernameRules = createRules.username();
const employeeIdRules = createRules.employeeId();
const passwordRules = createRules.newPassword();

onMounted(async () => {
    await nextTick();
    usernameField.value?.focus();
});

async function submitForm() {
    if (submitting.value) return;

    const { valid } = await form.value.validate();

    if (!valid) return;

    submitting.value = true;
    try {
        await usersAPI.create(formData.value);
        showSuccess('pages.users.create.success', {
            username: formData.value.username,
        });
        router.replace({ name: ROUTE_NAMES.ADMIN.USERS.LIST });
    } catch (error) {
        handleApiError(error);
    } finally {
        submitting.value = false;
    }
}

function goBack() {
    router.replace({ name: ROUTE_NAMES.ADMIN.USERS.LIST });
}
</script>

<template>
    <Header :app-title="t('pages.users.create.title')" />

    <!-- ✅ Grid Systemで構造 -->
    <v-container class="pa-4">
        <v-row justify="center">
            <v-col cols="12" sm="10" md="6" lg="5" xl="4">
                <v-card elevation="2">
                    <!-- ✅ pa-6で統一的な内部余白 -->
                    <v-card-text class="pa-6">
                        <!-- ✅ d-flex + flex-column + ga-4で要素間余白 (Flexboxなので安全) -->
                        <v-form
                            ref="form"
                            class="d-flex flex-column ga-4"
                            @submit.prevent="submitForm"
                        >
                            <v-text-field
                                ref="usernameField"
                                v-model="formData.username"
                                :label="$t('form.fields.username') + ' *'"
                                :rules="usernameRules"
                                variant="outlined"
                                :hint="t('form.hint.min', { min: 3 })"
                                persistent-hint
                            />

                            <v-text-field
                                v-model="formData.employee_id"
                                :label="$t('form.fields.employeeId') + ' *'"
                                :rules="employeeIdRules"
                                variant="outlined"
                                inputmode="numeric"
                                :hint="t('form.hint.employeeIdFormat')"
                                persistent-hint
                            />

                            <v-text-field
                                v-model="formData.password"
                                :label="$t('form.fields.password') + ' *'"
                                :rules="passwordRules"
                                variant="outlined"
                                type="password"
                                :hint="t('form.hint.passwordStrength')"
                                persistent-hint
                            />

                            <v-checkbox
                                v-model="formData.is_admin"
                                :label="t('form.fields.isAdmin')"
                                hide-details
                            />

                            <!-- ✅ <v-divider>で明確な区切り -->
                            <v-divider />

                            <!-- ✅ d-flex + <v-spacer />で両端配置 -->
                            <div class="d-flex ga-3">
                                <v-btn
                                    type="submit"
                                    color="primary"
                                    size="large"
                                    variant="outlined"
                                    :loading="submitting"
                                    :prepend-icon="ICONS.buttons.add"
                                >
                                    {{ t('buttons.create') }}
                                </v-btn>

                                <v-spacer />

                                <v-btn
                                    variant="outlined"
                                    size="large"
                                    :prepend-icon="ICONS.buttons.arrowBack"
                                    @click="goBack"
                                >
                                    {{ t('buttons.back') }}
                                </v-btn>
                            </div>
                        </v-form>
                    </v-card-text>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>
