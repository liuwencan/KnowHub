import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/chat' },
    { path: '/chat', name: 'chat', component: () => import('./App.vue') },
    { path: '/documents', name: 'documents', component: () => import('./App.vue') },
    { path: '/qa-cache', name: 'qa-cache', component: () => import('./App.vue'), meta: { staffOnly: true } },
  ],
})
