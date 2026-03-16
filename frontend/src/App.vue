<template>
  <v-app>
    <router-view></router-view>

    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          color="white"
          variant="text"
          @click="snackbar.show = false"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { reactive, provide } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

if (authStore.token && !authStore.user) {
    authStore.fetchUser()
}

const snackbar = reactive({
  show: false,
  text: '',
  color: 'info'
})

const showNotification = (text, color = 'info') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

provide('notify', showNotification)
</script>

<style>
html, body {
  font-family: 'Roboto', 'Inter', sans-serif;
}
.v-application {
  background-color: var(--v-theme-surface);
}
</style>
