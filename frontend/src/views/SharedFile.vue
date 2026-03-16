<template>
  <v-container class="fill-height bg-grey-lighten-4" fluid>
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-4 pb-4" rounded="lg">
          <v-progress-linear
            v-if="loading"
            indeterminate
            color="primary"
          ></v-progress-linear>

          <template v-if="!loading && file">
            <v-card-text class="text-center pt-8">
              <v-icon
                v-if="!isMedia(file.mime_type)"
                :icon="getFileIcon(file.mime_type)"
                :color="getFileColor(file.mime_type)"
                size="80"
                class="mb-4"
              ></v-icon>

              <div v-if="isMedia(file.mime_type)" class="mb-6 bg-grey-darken-4 rounded-lg overflow-hidden d-flex align-center justify-center" style="height: 250px; width: 100%;">
                 <img v-if="file.mime_type.startsWith('image/')" :src="getSharedPreviewUrl(file.id)" style="max-height: 100%; max-width: 100%; object-fit: contain;" />
                 <video v-else-if="file.mime_type.startsWith('video/')" controls :src="getSharedPreviewUrl(file.id)" style="max-height: 100%; max-width: 100%; object-fit: contain;"></video>
                 <audio v-else-if="file.mime_type.startsWith('audio/')" controls :src="getSharedPreviewUrl(file.id)" class="w-100 px-4"></audio>
              </div>
              
              <h2 class="text-h5 font-weight-bold mb-2">{{ file.name }}</h2>
              
              <div class="text-body-1 text-grey-darken-1 mb-6">
                Размер: {{ formatBytes(file.size) }}
              </div>
              
              <v-divider class="mb-6"></v-divider>
              
              <div class="d-flex align-center justify-center mb-6">
                <v-avatar color="primary" size="36" class="mr-3">
                  <span class="text-white">{{ file.owner_email.charAt(0).toUpperCase() }}</span>
                </v-avatar>
                <div class="text-left">
                  <div class="text-caption text-grey">Владелец</div>
                  <div class="text-body-2 font-weight-medium">{{ file.owner_email }}</div>
                </div>
              </div>

              <div class="text-caption text-grey mb-6">
                Загружено: {{ formatDate(file.uploaded_at) }}
              </div>

              <v-btn
                color="primary"
                size="large"
                prepend-icon="mdi-download"
                class="px-8"
                rounded="pill"
                @click="downloadFile"
              >
                Скачать файл
              </v-btn>
            </v-card-text>
          </template>

          <template v-else-if="!loading && error">
            <v-card-text class="text-center pt-8">
              <v-icon icon="mdi-file-hidden" color="error" size="64" class="mb-4"></v-icon>
              <h2 class="text-h5 font-weight-bold mb-2">Файл не найден</h2>
              <p class="text-body-1 text-grey-darken-1 mb-6">
                Возможно, ссылка устарела или файл был удален владельцем.
              </p>
              <v-btn
                color="primary"
                variant="outlined"
                to="/"
                prepend-icon="mdi-home"
              >
                Вернуться на главную
              </v-btn>
            </v-card-text>
          </template>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const fileId = route.params.id

const file = ref(null)
const loading = ref(true)
const error = ref(false)

const apiBaseUrl = 'http://localhost:8000'

onMounted(async () => {
  try {
    const response = await axios.get(`${apiBaseUrl}/api/files/shared/${fileId}`)
    file.value = response.data
  } catch (err) {
    console.error("Error loading shared file:", err)
    error.value = true
  } finally {
    loading.value = false
  }
})

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}

function getFileIcon(mimeType) {
  if (!mimeType) return 'mdi-file-outline'
  if (mimeType.startsWith('image/')) return 'mdi-image-outline'
  if (mimeType.startsWith('video/')) return 'mdi-video-outline'
  if (mimeType.includes('pdf')) return 'mdi-file-pdf-box'
  if (mimeType.includes('zip') || mimeType.includes('compressed')) return 'mdi-folder-zip-outline'
  return 'mdi-file-outline'
}

function getFileColor(mimeType) {
  if (!mimeType) return 'grey'
  if (mimeType.startsWith('image/')) return 'success'
  if (mimeType.startsWith('video/')) return 'deep-purple'
  if (mimeType.includes('pdf')) return 'error'
  if (mimeType.includes('zip')) return 'warning'
  return 'primary'
}

function isMedia(mimeType) {
  if (!mimeType) return false
  return mimeType.startsWith('image/') || mimeType.startsWith('video/') || mimeType.startsWith('audio/')
}

function getSharedPreviewUrl(id) {
  return `${apiBaseUrl}/api/files/shared/${id}/preview`
}

function downloadFile() {
  window.open(`${apiBaseUrl}/api/files/shared/${fileId}/download`, '_blank')
}
</script>
