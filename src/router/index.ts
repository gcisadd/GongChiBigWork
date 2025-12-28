import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      // 登录页面路由
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      // 登录页面路由（别名）
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/table',
      name: 'table',
      // 表格页面路由
      // route level code-splitting
      // this generates a separate chunk (Table.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/TableView.vue'),
    },
  ],
})

export default router
