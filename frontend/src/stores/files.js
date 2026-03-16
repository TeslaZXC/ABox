import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'
const S3_URL = 'http://localhost:8000/s3'

export const useFilesStore = defineStore('files', {
    state: () => ({
        buckets: [],
        currentBucket: null,
        files: [],
        selectedFiles: [],
        loading: false,
        error: null,
        uploadProgress: 0
    }),

    actions: {
        async loadBuckets(authStore) {
            if (!authStore.user) return

            this.loading = true
            try {
                const response = await axios.get(`${S3_URL}/?AWSAccessKeyId=${authStore.user.access_key}`)
                const parser = new DOMParser()
                const xmlDoc = parser.parseFromString(response.data, "text/xml")
                const bucketNodes = xmlDoc.getElementsByTagName('Bucket')

                this.buckets = Array.from(bucketNodes).map(node => ({
                    name: node.getElementsByTagName('Name')[0].textContent,
                    creationDate: node.getElementsByTagName('CreationDate')[0].textContent
                }))

                if (this.buckets.length > 0 && !this.currentBucket) {
                    this.currentBucket = this.buckets[0].name
                }
            } catch (err) {
                this.error = 'Failed to load buckets'
                console.error(err)
            } finally {
                this.loading = false
            }
        },

        async createBucket(name, authStore) {
            try {
                await axios.put(`${S3_URL}/${name}?AWSAccessKeyId=${authStore.user.access_key}`)
                await this.loadBuckets(authStore)
                this.currentBucket = name
            } catch (err) {
                this.error = err.response?.data || 'Failed to create bucket'
                throw err
            }
        },

        async deleteBucket(name, authStore) {
            try {
                await axios.delete(`${S3_URL}/${name}?AWSAccessKeyId=${authStore.user.access_key}`)
                await this.loadBuckets(authStore)
                if (this.currentBucket === name) {
                    this.currentBucket = this.buckets.length > 0 ? this.buckets[0].name : null
                }
                await this.loadFiles()
            } catch (err) {
                this.error = 'Failed to delete bucket'
                throw err
            }
        },

        async loadFiles() {
            this.loading = true
            try {
                const response = await axios.get(`${API_URL}/files`)
                this.files = response.data
            } catch (err) {
                this.error = 'Failed to load files'
                console.error(err)
            } finally {
                this.loading = false
            }
        },

        async uploadFile(file, bucketName = null) {
            if (!bucketName) {
                bucketName = this.currentBucket || 'default'
            }

            const formData = new FormData()
            formData.append('file', file)
            formData.append('bucket_name', bucketName)

            try {
                await axios.post(`${API_URL}/files/upload`, formData, {
                    headers: { 'Content-Type': 'multipart/form-data' },
                    onUploadProgress: (progressEvent) => {
                        if (progressEvent.total) {
                            this.uploadProgress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                        }
                    }
                })
                await this.loadFiles()
                this.uploadProgress = 0
            } catch (err) {
                this.error = err.response?.data?.detail || 'Failed to upload'
                this.uploadProgress = 0
                throw err
            }
        },

        async deleteFile(file, authStore) {
            try {
                await axios.delete(`${S3_URL}/${file.bucket_name}/${file.key}?AWSAccessKeyId=${authStore.user.access_key}`)
                await this.loadFiles()
            } catch (err) {
                this.error = 'Failed to delete file'
                throw err
            }
        },

        async createArchive(fileIds) {
            try {
                const res = await axios.post(`${API_URL}/files/create-archive`, { file_ids: fileIds })
                await this.loadFiles()
                return res.data
            } catch (err) {
                this.error = 'Failed to create archive'
                throw err
            }
        },

        getDownloadUrl(file, authStore) {
            return `${S3_URL}/${file.bucket_name}/${file.key}?AWSAccessKeyId=${authStore.user.access_key}`
        },

        getPreviewUrl(file, authStore) {
            return `${API_URL}/files/preview/${file.id}?token=${authStore.token}`
        }
    }
})
