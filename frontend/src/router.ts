import { createRouter, createWebHistory } from 'vue-router'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('./views/LoginView.vue') },
    { path: '/', component: () => import('./layouts/AppLayout.vue'), children: [
      { path: '', redirect: '/chat' },
      { path: 'chat', name: 'chat', component: () => import('./views/WorkspaceView.vue') },
      { path: 'documents', name: 'documents', component: () => import('./views/DocumentsView.vue') },
      { path: 'qa-cache', name: 'qa-cache', component: () => import('./views/QaCacheView.vue'), meta: { staffOnly: true } },
    ] },
    { path: '/:pathMatch(.*)*', redirect: '/chat' },
  ],
})
