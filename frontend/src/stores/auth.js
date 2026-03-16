import { defineStore } from 'pinia'
import axios from 'axios'
import router from '../router'

const API_URL = 'http://localhost:8000/api'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        token: localStorage.getItem('token') || null,
        user: null,
        loading: false,
        error: null
    }),

    actions: {
        async login(email, password) {
            this.loading = true
            this.error = null
            try {
                const response = await axios.post(`${API_URL}/auth/login`, { email, password })
                this.token = response.data.access_token
                localStorage.setItem('token', this.token)
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
                await this.fetchUser()
                router.push('/disk')
            } catch (err) {
                this.error = err.response?.data?.detail || 'Ошибка входа'
                throw err
            } finally {
                this.loading = false
            }
        },

        async register(email, password) {
            this.loading = true
            this.error = null
            try {
                await axios.post(`${API_URL}/auth/register`, { email, password })
                router.push({ path: '/verify', query: { email } })
            } catch (err) {
                this.error = err.response?.data?.detail || 'Ошибка регистрации'
                throw err
            } finally {
                this.loading = false
            }
        },

        async verifyEmail(email, code) {
            this.loading = true
            this.error = null
            try {
                await axios.post(`${API_URL}/auth/verify-email`, { email, code })
                router.push('/login')
            } catch (err) {
                this.error = err.response?.data?.detail || 'Неверный код'
                throw err
            } finally {
                this.loading = false
            }
        },

        async resendCode(email) {
            try {
                await axios.post(`${API_URL}/auth/resend-code`, { email })
            } catch (err) {
                this.error = err.response?.data?.detail || 'Ошибка повторной отправки кода'
                throw err
            }
        },

        async fetchUser() {
            if (!this.token) return

            try {
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
                const response = await axios.get(`${API_URL}/auth/me`)
                this.user = response.data
            } catch (err) {
                this.logout()
            }
        },

        logout() {
            this.token = null
            this.user = null
            localStorage.removeItem('token')
            delete axios.defaults.headers.common['Authorization']
            router.push('/login')
        }
    }
})
