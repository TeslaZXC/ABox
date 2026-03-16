<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="glass-card pa-4" :loading="loading">
          <v-card-title class="text-h4 font-weight-bold text-center pt-8 pb-4 text-white">
            ABox
          </v-card-title>
          
          <v-card-text>
            <v-form @submit.prevent="handleLogin" ref="form">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-account"
                variant="solo"
                bg-color="rgba(255, 255, 255, 0.1)"
                flat
                density="comfortable"
                :rules="[v => !!v || 'Email обязателен', v => /.+@.+\..+/.test(v) || 'Введите корректный email']"
                required
                class="mb-4 glass-input"
              ></v-text-field>

              <v-text-field
                v-model="password"
                label="Пароль"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                variant="solo"
                bg-color="rgba(255, 255, 255, 0.1)"
                flat
                density="comfortable"
                :rules="[v => !!v || 'Пароль обязателен']"
                required
                class="mb-4 glass-input"
              ></v-text-field>

              <div class="d-flex justify-center mb-6">
                <v-btn variant="plain" color="white" class="px-0 text-body-2" to="/register">
                  Нет аккаунта? Зарегистрироваться
                </v-btn>
              </div>

              <v-btn
                type="submit"
                color="white"
                size="large"
                block
                class="glass-btn rounded-xl font-weight-bold mb-4"
                :disabled="loading"
              >
                Войти
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.glass-input :deep(.v-field) {
  border-radius: 12px !important;
  color: white !important;
}
.glass-input :deep(.v-label) {
  color: rgba(255, 255, 255, 0.7) !important;
}
.glass-input :deep(.v-field__input) {
  color: white !important;
}
</style>


<script setup>
import { ref, inject } from 'vue'
import { useAuthStore } from '../stores/auth'

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const form = ref(null)

const authStore = useAuthStore()
const notify = inject('notify')

const handleLogin = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return
  
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    notify('Успешный вход!', 'success')
  } catch (error) {
    notify(authStore.error || 'Ошибка при входе', 'error')
  } finally {
    loading.value = false
  }
}
</script>
