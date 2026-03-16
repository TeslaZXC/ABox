import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
    {
        path: '/',
        name: 'Landing',
        component: () => import('../views/Landing.vue')
    },
    {
        path: '/login',
        name: 'Login',
        component: () => import('../views/Login.vue')
    },
    {
        path: '/register',
        name: 'Register',
        component: () => import('../views/Register.vue')
    },
    {
        path: '/verify',
        name: 'Verify',
        component: () => import('../views/Verify.vue')
    },
    {
        path: '/shared/:id',
        name: 'SharedFile',
        component: () => import('../views/SharedFile.vue')
    },
    {
        path: '/disk',
        name: 'Disk',
        component: () => import('../views/Disk.vue'),
        meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.token) {
        return '/login'
    }

    if ((to.path === '/login' || to.path === '/register') && authStore.token) {
        return '/disk'
    }

    return true
})

export default router
