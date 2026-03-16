<template>
  <v-container fluid class="fill-height bg-surface-variant">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="5">
        <v-card class="elevation-12 rounded-xl text-center pb-6" :loading="loading">
          <v-card-title class="text-h4 font-weight-bold pt-8 pb-4">
            Подтверждение Email
          </v-card-title>
          
          <v-card-text>
            <p class="text-body-1 mb-6 text-medium-emphasis">
              Мы отправили код на <strong>{{ email }}</strong>
            </p>

            <v-form @submit.prevent="handleVerify" class="px-4">
              <v-otp-input
                v-model="code"
                length="6"
                type="number"
                class="mb-8"
                auto-focus
                variant="outlined"
              ></v-otp-input>

              <v-btn
                type="submit"
                color="primary"
                size="large"
                block
                class="rounded-lg text-button font-weight-bold mb-6"
                :disabled="loading || code.length < 6"
              >
                Подтвердить
              </v-btn>

              <div class="d-flex justify-center align-center flex-column mt-4">
                <p v-if="timer > 0" class="text-caption text-medium-emphasis">
                  Повторная отправка через {{ timer }} сек.
                </p>
                <v-btn 
                  v-else 
                  variant="plain" 
                  color="primary" 
                  class="text-caption px-0 mt-n2"
                  @click="handleResend"
                >
                  Отправить код повторно
                </v-btn>
              </div>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const email = ref(route.query.email || '')
const code = ref('')
const loading = ref(false)
const timer = ref(60)

const authStore = useAuthStore()
const notify = inject('notify')

let interval = null

const startTimer = () => {
  timer.value = 60
  interval = setInterval(() => {
    if (timer.value > 0) {
      timer.value--
    } else {
      clearInterval(interval)
    }
  }, 1000)
}

onMounted(() => {
  startTimer()
})

onUnmounted(() => {
  if (interval) clearInterval(interval)
})

const handleVerify = async () => {
  if (code.value.length < 6) return
  
  loading.value = true
  try {
    await authStore.verifyEmail(email.value, code.value)
    notify('Email успешно подтвержден! Теперь вы можете войти.', 'success')
  } catch (error) {
    notify(authStore.error || 'Ошибка подтверждения', 'error')
    code.value = ''
  } finally {
    loading.value = false
  }
}

const handleResend = async () => {
  try {
    await authStore.resendCode(email.value)
    notify('Код повторно отправлен!', 'info')
    startTimer()
  } catch (err) {
    notify(authStore.error || 'Ошибка отправки', 'error')
  }
}
</script>
