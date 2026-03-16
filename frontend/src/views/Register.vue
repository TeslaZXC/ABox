<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="glass-card pa-4" :loading="loading">
          <v-card-title class="text-h4 font-weight-bold text-center pt-8 pb-4 text-white">
            ABox
          </v-card-title>
          
          <v-card-text>
            <v-form @submit.prevent="handleRegister" ref="form">
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
                prepend-inner-icon="mdi-email"
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
                :rules="[v => !!v || 'Пароль обязателен', v => v.length >= 8 || 'Минимум 8 символов']"
                required
                class="mb-4 glass-input"
              ></v-text-field>

              <v-text-field
                v-model="passwordConfirm"
                label="Подтверждение пароля"
                :type="showPassword ? 'text' : 'password'"
                prepend-inner-icon="mdi-lock-check"
                variant="solo"
                bg-color="rgba(255, 255, 255, 0.1)"
                flat
                density="comfortable"
                :rules="[
                  v => !!v || 'Подтвердите пароль',
                  v => v === password || 'Пароли не совпадают'
                ]"
                required
                class="mb-6 glass-input"
              ></v-text-field>

              <v-btn
                type="submit"
                color="white"
                size="large"
                block
                class="glass-btn rounded-xl font-weight-bold mb-4"
                :disabled="loading"
              >
                Зарегистрироваться
              </v-btn>

              <div class="text-center">
                <v-btn variant="plain" color="white" class="text-body-2" to="/login">
                  Уже есть аккаунт? Войти
                </v-btn>
              </div>
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
const passwordConfirm = ref('')
const showPassword = ref(false)
const loading = ref(false)
const form = ref(null)

const authStore = useAuthStore()
const notify = inject('notify')

const handleRegister = async () => {
  const { valid } = await form.value.validate()
  if (!valid) return
  
  loading.value = true
  try {
    await authStore.register(email.value, password.value)
    notify('Регистрация успешна! Проверьте email.', 'success')
  } catch (error) {
    notify(authStore.error || 'Ошибка при регистрации', 'error')
  } finally {
    loading.value = false
  }
}
</script>
