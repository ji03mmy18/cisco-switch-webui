import { createRouter, createWebHistory } from 'vue-router'
import { useSessionStore } from '@/stores/session'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    // 未知路由導向登入頁
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

// 路由守衛：未登入時導向登入頁，已登入時不允許再訪問登入頁
router.beforeEach(async (to) => {
  const sessionStore = useSessionStore()

  // 首次導航時，向後端確認連線狀態
  if (!sessionStore.initialized) {
    await sessionStore.checkStatus()
  }

  if (to.meta.requiresAuth && !sessionStore.isConnected) {
    return { name: 'login' }
  }

  if (to.name === 'login' && sessionStore.isConnected) {
    return { name: 'dashboard' }
  }
})

export default router
