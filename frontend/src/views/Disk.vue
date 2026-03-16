<template>
  <v-layout class="fill-height" @drop.prevent="handleDrop" @dragover.prevent="dragover = true" @dragleave.prevent="dragover = false">
    <v-app-bar color="transparent" flat class="glass-effect" height="70">
      <v-toolbar-title class="font-weight-bold text-white d-flex align-center">
        <v-icon icon="mdi-cloud-outline" size="large" class="mr-2"></v-icon>
        ABox
      </v-toolbar-title>
      
      <v-spacer></v-spacer>

      <v-btn icon @click="loadData">
        <v-icon>mdi-refresh</v-icon>
      </v-btn>

      <v-btn icon color="white" @click="toggleTheme">
        <v-icon>{{ isDark ? 'mdi-weather-sunny' : 'mdi-weather-night' }}</v-icon>
      </v-btn>

      <v-menu v-if="authStore.user">
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-avatar color="primary" size="36">
              <span class="text-white text-h6">{{ authStore.user.email.charAt(0).toUpperCase() }}</span>
            </v-avatar>
          </v-btn>
        </template>
        <v-list>
          <v-list-item>
            <v-list-item-title class="font-weight-medium">{{ authStore.user.email }}</v-list-item-title>
            <v-list-item-subtitle>{{ formatBytes(authStore.user.used_storage) }} out of {{ formatBytes(authStore.user.storage_quota) }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item @click="authStore.logout" color="error">
            <template v-slot:prepend>
              <v-icon icon="mdi-logout"></v-icon>
            </template>
            <v-list-item-title>Выйти</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer permanent elevation="0" width="280" color="transparent" class="glass-effect border-0">
      <div class="pa-4 pt-6">
        <v-btn block color="primary" size="large" rounded="pill" prepend-icon="mdi-plus" @click="createBucketDialog = true">
          Создать бакет
        </v-btn>
      </div>

      <v-list nav class="px-2">
        <v-list-subheader class="text-white opacity-70">МОИ БАКЕТЫ</v-list-subheader>
        
        <v-list-item 
          v-for="bucket in filesStore.buckets" 
          :key="bucket.name"
          :value="bucket.name"
          :active="filesStore.currentBucket === bucket.name"
          @click="filesStore.currentBucket = bucket.name"
          rounded="xl"
          color="white"
          class="mb-1 text-white bucket-item"
        >
          <template v-slot:prepend>
            <v-icon :icon="filesStore.currentBucket === bucket.name ? 'mdi-folder-open' : 'mdi-folder'"></v-icon>
          </template>
          <v-list-item-title class="font-weight-medium">{{ bucket.name }}</v-list-item-title>
          <template v-slot:append>
            <div class="d-flex align-center">
              <v-chip size="x-small" variant="flat" class="mr-1">{{ getBucketFileCount(bucket.name) }}</v-chip>
              <v-btn
                icon="mdi-delete-outline"
                size="x-small"
                variant="text"
                color="white"
                class="bucket-delete-btn"
                @click.stop="confirmDeleteBucket(bucket)"
              ></v-btn>
            </div>
          </template>
        </v-list-item>

        <v-list-item v-if="filesStore.buckets.length === 0" disabled>
          <v-list-item-title class="text-caption text-center">Нет бакетов</v-list-item-title>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-4 text-white" v-if="authStore.user">
          <div class="d-flex justify-space-between text-caption mb-1">
            <span>Использовано</span>
            <strong>{{ usagePercent }}%</strong>
          </div>
          <v-progress-linear
            :model-value="usagePercent"
            color="white"
            height="6"
            rounded
          ></v-progress-linear>
          <div class="text-caption mt-1 opacity-70">
            {{ formatBytes(authStore.user.used_storage) }} из {{ formatBytes(authStore.user.storage_quota) }}
          </div>
        </div>
      </template>
    </v-navigation-drawer>

    <v-main class="h-100">
      <v-overlay v-model="dragover" class="align-center justify-center border-dashed" :opacity="0.9" z-index="1000">
        <div class="text-center">
          <v-icon size="100" color="primary">mdi-cloud-upload</v-icon>
          <h2 class="text-h4 text-white mt-4 font-weight-bold">Отпустите файлы для загрузки</h2>
        </div>
      </v-overlay>

      <v-container fluid class="pa-6" style="max-width: 1400px;">
        <div class="d-flex align-center justify-space-between mb-6">
          <v-breadcrumbs :items="breadcrumbItems" class="px-0 py-2 pb-0 text-h6 font-weight-medium">
            <template v-slot:divider>
              <v-icon icon="mdi-chevron-right"></v-icon>
            </template>
          </v-breadcrumbs>

          <v-slide-y-transition>
            <div v-if="selectedRows.length > 0" class="d-flex align-center bg-primary-lighten-1 rounded-pill px-4 py-2" style="position: absolute; left: 50%; transform: translateX(-50%); z-index: 10;">
              <span class="text-body-2 font-weight-bold mr-4 text-white">{{ selectedRows.length }} выбрано</span>
              
              <v-btn size="small" variant="text" color="white" prepend-icon="mdi-zip-box" @click="downloadArchive" class="mr-2">
                Создать архив
              </v-btn>
              <v-btn size="small" variant="text" color="white" prepend-icon="mdi-delete" @click="confirmDeleteMultiple">
                Удалить
              </v-btn>
              <v-divider vertical class="mx-3 border-opacity-50" color="white"></v-divider>
              <v-btn icon="mdi-close" size="small" variant="text" color="white" @click="selectedRows = []"></v-btn>
            </div>
          </v-slide-y-transition>

          <div class="d-flex">
            <input type="file" ref="fileInput" @change="handleFileUpload" multiple class="d-none" />
            <v-btn color="primary" prepend-icon="mdi-upload" rounded="pill" @click="$refs.fileInput.click()">
              Загрузить файлы
            </v-btn>
          </div>
        </div>

        <v-card class="glass-card">
          <v-data-table
            v-model="selectedRows"
            :headers="tableHeaders"
            :items="currentBucketFiles"
            :loading="filesStore.loading"
            item-value="id"
            show-select
            hover
            class="bg-transparent text-white"
            @click:row="handleRowClick"
          >
            <template v-slot:item.name="{ item }">
              <div class="d-flex align-center py-2">
                <v-icon :icon="getFileIcon(item.mime_type)" :color="getFileColor(item.mime_type)" size="large" class="mr-4"></v-icon>
                <span class="font-weight-medium text-body-1">{{ item.name }}</span>
              </div>
            </template>
            <template v-slot:item.size="{ item }">
              <span class="text-medium-emphasis">{{ formatBytes(item.size) }}</span>
            </template>
            <template v-slot:item.uploaded_at="{ item }">
              <span class="text-medium-emphasis">{{ formatDate(item.uploaded_at) }}</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <div class="d-flex justify-end">
                <v-btn icon="mdi-download" density="comfortable" variant="text" color="primary" @click.stop="downloadFile(item)"></v-btn>
                <v-menu location="start">
                  <template v-slot:activator="{ props }">
                    <v-btn icon="mdi-dots-vertical" density="comfortable" variant="text" v-bind="props"></v-btn>
                  </template>
                  <v-list density="compact" class="rounded-lg">
                    <v-list-item v-if="isMedia(item.mime_type)" @click="openViewer(item)" prepend-icon="mdi-eye">
                      <v-list-item-title>Предпросмотр</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="openRenameDialog(item)" prepend-icon="mdi-pencil">
                      <v-list-item-title>Переименовать</v-list-item-title>
                    </v-list-item>
                    <v-list-item @click="copyShareLink(item)" prepend-icon="mdi-link-variant">
                      <v-list-item-title>Копировать ссылку</v-list-item-title>
                    </v-list-item>
                    <v-divider></v-divider>
                    <v-list-item @click="confirmDeleteSingle(item)" prepend-icon="mdi-delete" class="text-error">
                      <v-list-item-title>Удалить</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
              </div>
            </template>
            
            <template v-slot:no-data>
              <div class="pa-10 text-center text-medium-emphasis">
                <v-icon icon="mdi-folder-open-outline" size="64" class="mb-4 text-disabled"></v-icon>
                <div class="text-h6 font-weight-regular">Папка пуста</div>
                <div class="text-body-2 mt-2">Перетащите файлы сюда или нажмите кнопку ЗАГРУЗИТЬ ФАЙЛЫ</div>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-container>
    </v-main>

    <v-snackbar v-model="showUploadProgress" :timeout="-1" color="surface" variant="elevated" location="bottom right">
      <div class="d-flex align-center pb-2">
        <span class="font-weight-medium text-body-1">Загрузка файла...</span>
        <v-spacer></v-spacer>
        <span>{{ filesStore.uploadProgress }}%</span>
      </div>
      <v-progress-linear :model-value="filesStore.uploadProgress" color="primary"></v-progress-linear>
    </v-snackbar>

    <v-dialog v-model="createBucketDialog" max-width="400">
      <v-card class="rounded-xl">
        <v-card-title class="pt-6 px-6 font-weight-bold">Создать бакет</v-card-title>
        <v-card-text class="px-6 pt-2">
          <v-text-field
            v-model="newBucketName"
            label="Имя бакета"
            variant="outlined"
            placeholder="my-cool-bucket"
            :rules="[v => !!v || 'Имя обязательно', v => /^[a-z0-9-]+$/.test(v) || 'Только малые англ. буквы, цифры и дефис']"
            autofocus
            @keyup.enter="handleCreateBucket"
          ></v-text-field>
        </v-card-text>
        <v-card-actions class="px-6 pb-6 pt-0">
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="createBucketDialog = false">Отмена</v-btn>
          <v-btn color="primary" variant="flat" :disabled="!newBucketName" @click="handleCreateBucket" :loading="bucketCreating">Создать</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="viewerDialog" fullscreen transition="dialog-bottom-transition">
      <v-card class="bg-black">
        <v-toolbar color="rgba(0,0,0,0.8)" theme="dark">
          <v-btn icon="mdi-close" @click="closeViewer"></v-btn>
          <v-toolbar-title>{{ viewerFile?.name }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-download" @click="downloadFile(viewerFile)"></v-btn>
        </v-toolbar>
        
        <v-card-text class="pa-0 d-flex align-center justify-center fill-height position-relative">
          <v-progress-circular v-if="viewerLoading" indeterminate color="primary" class="position-absolute"></v-progress-circular>
          
          <template v-if="viewerFile">
            <img 
               v-if="viewerFile.mime_type?.startsWith('image/')" 
               :src="filesStore.getPreviewUrl(viewerFile, authStore)" 
               @load="viewerLoading = false"
               @error="viewerLoading = false"
               style="max-width: 100%; max-height: calc(100vh - 64px); object-fit: contain;" 
            />
            <video 
               v-else-if="viewerFile.mime_type?.startsWith('video/')" 
               controls 
               autoplay
               :src="filesStore.getPreviewUrl(viewerFile, authStore)"
               @loadeddata="viewerLoading = false"
               @error="viewerLoading = false"
               style="max-width: 100%; max-height: calc(100vh - 64px);"
            ></video>
            <audio 
               v-else-if="viewerFile.mime_type?.startsWith('audio/')" 
               controls 
               autoplay
               :src="filesStore.getPreviewUrl(viewerFile, authStore)"
               @loadeddata="viewerLoading = false"
               @error="viewerLoading = false"
               class="w-50"
            ></audio>
            <div v-else class="text-center text-white">
               <v-icon size="64" class="mb-4">mdi-file-hidden</v-icon>
               <div class="text-h6">Предпросмотр недоступен.</div>
               <v-btn class="mt-4" color="primary" @click="downloadFile(viewerFile)">Скачать</v-btn>
            </div>
          </template>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-dialog v-model="confirmDialog.show" max-width="500">
      <v-card class="glass-card pa-6 text-center">
        <v-icon icon="mdi-alert-circle-outline" size="80" color="white" class="mb-4 opacity-80"></v-icon>
        <v-card-title class="text-h4 font-weight-bold text-white mb-2 pb-0">
          {{ confirmDialog.title }}
        </v-card-title>
        <v-card-text class="text-h6 text-white opacity-80 leading-relaxed pt-2">
          {{ confirmDialog.message }}
        </v-card-text>
        <v-card-actions class="justify-center pt-6 ga-4">
          <v-btn
            variant="text"
            color="white"
            class="px-8 rounded-xl font-weight-bold"
            @click="confirmDialog.show = false"
          >
            Отмена
          </v-btn>
          <v-btn
            color="white"
            class="glass-btn px-8 rounded-xl font-weight-bold"
            @click="handleCustomConfirm"
          >
            Да, уверен
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-layout>
</template>

<script setup>
import { ref, reactive, computed, onMounted, inject } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useFilesStore } from '../stores/files'
import { useTheme } from 'vuetify'

const authStore = useAuthStore()
const filesStore = useFilesStore()
const theme = useTheme()
const notify = inject('notify')

const confirmDialog = reactive({
  show: false,
  title: '',
  message: '',
  onConfirm: null
})

const openConfirm = (title, message, callback) => {
  confirmDialog.title = title
  confirmDialog.message = message
  confirmDialog.onConfirm = callback
  confirmDialog.show = true
}

const handleCustomConfirm = async () => {
  if (confirmDialog.onConfirm) {
    await confirmDialog.onConfirm()
  }
  confirmDialog.show = false
}

const dragover = ref(false)
const selectedRows = ref([])
const createBucketDialog = ref(false)
const newBucketName = ref('')
const bucketCreating = ref(false)
const showUploadProgress = computed(() => filesStore.uploadProgress > 0)

const viewerDialog = ref(false)
const viewerFile = ref(null)
const viewerLoading = ref(false)

const isDark = computed(() => theme.global.name.value === 'dark')

const toggleTheme = () => {
  theme.global.name.value = isDark.value ? 'light' : 'dark'
}

const loadData = async () => {
  await authStore.fetchUser()
  await filesStore.loadBuckets(authStore)
  await filesStore.loadFiles()
}

onMounted(() => {
  loadData()
})

const usagePercent = computed(() => {
  if (!authStore.user || authStore.user.storage_quota === 0) return 0
  return Math.min(100, Math.round((authStore.user.used_storage / authStore.user.storage_quota) * 100))
})

const tableHeaders = [
  { title: 'Имя', key: 'name', sortable: true },
  { title: 'Размер', key: 'size', sortable: true },
  { title: 'Дата загрузки', key: 'uploaded_at', sortable: true },
  { title: '', key: 'actions', sortable: false, align: 'end' }
]

const currentBucketFiles = computed(() => {
  return filesStore.files.filter(f => f.bucket_name === filesStore.currentBucket)
})

const breadcrumbItems = computed(() => {
  return [
    { title: 'ABox', disabled: false },
    { title: filesStore.currentBucket || 'Диск', disabled: true }
  ]
})

const getBucketFileCount = (name) => {
  return filesStore.files.filter(f => f.bucket_name === name).length
}

const formatBytes = (bytes, decimals = 1) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

const formatDate = (dateString) => {
  const d = new Date(dateString)
  return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getFileIcon = (mimeType) => {
  if (!mimeType) return 'mdi-file-outline'
  if (mimeType.includes('image')) return 'mdi-image'
  if (mimeType.includes('pdf')) return 'mdi-file-pdf-box'
  if (mimeType.includes('zip') || mimeType.includes('compressed')) return 'mdi-folder-zip-outline'
  if (mimeType.includes('text')) return 'mdi-file-document-outline'
  if (mimeType.includes('video')) return 'mdi-play-box-outline'
  return 'mdi-file-outline'
}

const getFileColor = (mimeType) => {
  if (!mimeType) return 'grey-lighten-1'
  if (mimeType.includes('image')) return 'info'
  if (mimeType.includes('pdf')) return 'error'
  if (mimeType.includes('zip')) return 'warning'
  if (mimeType.includes('text')) return 'primary'
  if (mimeType.includes('video')) return 'purple'
  return 'grey'
}

const handleCreateBucket = async () => {
  if (!newBucketName.value) return
  bucketCreating.value = true
  try {
    await filesStore.createBucket(newBucketName.value, authStore)
    notify('Бакет создан!', 'success')
    createBucketDialog.value = false
    newBucketName.value = ''
  } catch (err) {
    notify(filesStore.error || 'Ошибка', 'error')
  } finally {
    bucketCreating.value = false
  }
}

const confirmDeleteBucket = (bucket) => {
  openConfirm(
    'Удалить бакет?',
    `Вы уверены, что хотите удалить бакет "${bucket.name}" со всеми файлами? Это действие необратимо!`,
    async () => {
      try {
        await filesStore.deleteBucket(bucket.name, authStore)
        notify(`Бакет ${bucket.name} удален`, 'success')
      } catch (err) {
        notify(filesStore.error || 'Ошибка при удалении бакета', 'error')
      }
    }
  )
}

const handleDrop = async (e) => {
  dragover.value = false
  if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
    for (let f of e.dataTransfer.files) {
      await uploadSingle(f)
    }
  }
}

const handleFileUpload = async (event) => {
  const files = event.target.files
  for (let f of files) {
    await uploadSingle(f)
  }
  event.target.value = ''
}

const uploadSingle = async (file) => {
  if (!filesStore.currentBucket) {
     notify('Сначала выберите или создайте бакет', 'warning')
     return
  }
  try {
    await filesStore.uploadFile(file, filesStore.currentBucket)
    notify(`${file.name} загружен`, 'success')
  } catch (err) {
    notify(`Ошибка загрузки ${file.name}: ${filesStore.error}`, 'error')
  }
  await authStore.fetchUser()
}

const downloadFile = (file) => {
  const url = filesStore.getDownloadUrl(file, authStore)
  window.open(url, '_blank')
}

const confirmDeleteSingle = (file) => {
  openConfirm(
    'Удалить файл?',
    `Точно удалить файл ${file.name}?`,
    async () => {
      try {
        await filesStore.deleteFile(file, authStore)
        notify('Удалено', 'success')
        await authStore.fetchUser()
      } catch (err) {
        notify('Ошибка удаления', 'error')
      }
    }
  )
}

const confirmDeleteMultiple = () => {
  openConfirm(
    'Удалить файлы?',
    `Удалить выбранные файлы (${selectedRows.value.length})? Это действие нельзя отменить.`,
    async () => {
      try {
        for (const id of selectedRows.value) {
          const file = currentBucketFiles.value.find(f => f.id === id)
          if (file) {
              await filesStore.deleteFile(file, authStore)
          }
        }
        notify('Файлы удалены', 'success')
        selectedRows.value = []
        await authStore.fetchUser()
      } catch (e) {
        notify('Произошла ошибка при множественном удалении', 'error')
      }
    }
  )
}

const downloadArchive = async () => {
  try {
    const res = await filesStore.createArchive(selectedRows.value)
    notify(`Архив ${res.filename} создан!`, 'success')
    selectedRows.value = []
    await filesStore.loadFiles()
    await authStore.fetchUser()
  } catch (e) {
    notify('Ошибка создания архива', 'error')
  }
}

const openRenameDialog = (item) => {
    notify('Функция переименования в разработке (для S3 это CopyObject + DeleteObject)', 'warning')
}

const copyShareLink = async (item) => {
  const url = `${window.location.origin}/shared/${item.id}`
  try {
    await navigator.clipboard.writeText(url)
    notify('Ссылка для скачивания скопирована!', 'success')
  } catch (err) {
    notify('Не удалось скопировать ссылку', 'error')
  }
}

const isMedia = (mimeType) => {
  if (!mimeType) return false
  return mimeType.startsWith('image/') || mimeType.startsWith('video/') || mimeType.startsWith('audio/')
}

const handleRowClick = (event, { item }) => {
  if (isMedia(item.mime_type)) {
    openViewer(item)
  }
}

const openViewer = (file) => {
  viewerFile.value = file
  viewerLoading.value = true
  viewerDialog.value = true
}

const closeViewer = () => {
  viewerDialog.value = false
  setTimeout(() => {
    viewerFile.value = null
  }, 300)
}
</script>

<style scoped>
.border-dashed {
  border: 4px dashed rgba(255, 255, 255, 0.5) !important;
  pointer-events: none;
}

.bucket-item :deep(.v-list-item__overlay) {
  opacity: 0.1 !important;
}

:deep(.v-data-table) {
  background: transparent !important;
}

:deep(.v-data-table-header__content) {
  color: white !important;
  font-weight: 700 !important;
}

:deep(.v-data-table__td) {
  color: white !important;
}

:deep(.v-checkbox-btn .v-selection-control__input) {
  color: white !important;
}

:deep(.v-breadcrumbs-item) {
  color: white !important;
}

.bucket-delete-btn {
  opacity: 0;
  transition: opacity 0.2s;
}

.bucket-item:hover .bucket-delete-btn {
  opacity: 0.7;
}

.bucket-delete-btn:hover {
  opacity: 1 !important;
  color: #ff5252 !important;
}
</style>
