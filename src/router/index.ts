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
    {
      path: '/editor',
      name: 'editor',
      // 富文本编辑器页面路由
      component: () => import('../views/RichTextEditorView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      // 个人信息页面路由
      component: () => import('../views/ProfileView.vue'),
    },
  ],
})

export default router
