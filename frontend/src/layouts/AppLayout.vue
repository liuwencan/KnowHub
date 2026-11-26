<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { authState, clearAuth, restoreAuth } from '../authState'
import { chatState, loadConversations, newConversation, resetChat, selectConversation } from '../chat'

const route = useRoute(); const router = useRouter(); const collapsed = ref(false); const mobileOpen = ref(false); const search = ref('')
const isStaff = computed(() => authState.identity?.role === 'staff')
const displayName = computed(() => authState.identity?.user_id || '企业员工')
const groups = computed(() => {
  const term = search.value.trim().toLowerCase()
  const rows = chatState.conversations.filter((item) => !term || item.title.toLowerCase().includes(term))
  return [{ label: '历史对话', items: rows }].filter((group) => group.items.length)
})
const pageTitle = computed(() => route.name === 'documents' ? '知识文档' : route.name === 'qa-cache' ? 'QA 缓存审核' : '新的知识对话')

onMounted(async () => {
  const identity = await restoreAuth()
  if (!identity) { router.replace({ name: 'login', query: { redirect: route.fullPath } }); return }
  await loadConversations().catch(() => undefined)
})
async function openConversation(id: string) { await selectConversation(id); mobileOpen.value = false; router.push('/chat') }
async function signOut() { await clearAuth(); resetChat(); router.replace('/login') }
function startNew() { newConversation(); mobileOpen.value = false; router.push('/chat') }
</script>

<template>
  <div v-if="authState.ready && authState.identity" class="app-shell" :class="{ 'sidebar-collapsed': collapsed, 'mobile-sidebar-open': mobileOpen }">
    <button v-if="mobileOpen" class="sidebar-backdrop" aria-label="关闭会话侧栏" @click="mobileOpen = false" />
    <aside class="app-sidebar" aria-label="会话与账号">
      <div class="sidebar-brand-row"><RouterLink to="/chat" class="brand-link"><span class="brand-mark">K</span><span v-if="!collapsed" class="brand-copy"><strong>KnowHub</strong><small>企业知识助手</small></span></RouterLink><button class="icon-button" :title="collapsed ? '展开侧栏' : '收起侧栏'" @click="collapsed = !collapsed">{{ collapsed ? '›' : '‹' }}</button></div>
      <div class="sidebar-actions"><button class="new-chat-button" @click="startNew"><span class="plus">+</span><span v-if="!collapsed">新建对话</span></button><button v-if="!collapsed" class="icon-button" title="搜索会话">⌕</button></div>
      <input v-if="!collapsed" v-model="search" class="sidebar-search" placeholder="搜索历史会话" aria-label="搜索历史会话" />
      <div class="sidebar-history" :class="{ 'history-hidden': collapsed }">
        <p v-if="chatState.loading" class="sidebar-empty">正在加载会话…</p>
        <template v-else><section v-for="group in groups" :key="group.label" class="history-group"><h2>{{ group.label }}</h2><button v-for="item in group.items" :key="item.id" class="conversation-item" :class="{ active: item.id === chatState.activeId && route.name === 'chat' }" :title="item.title" @click="openConversation(item.id)"><span class="conversation-icon">◌</span><span v-if="!collapsed">{{ item.title }}</span></button></section><p v-if="!groups.length" class="sidebar-empty">还没有历史对话<small>从一段新的知识咨询开始</small></p></template>
      </div>
      <div class="sidebar-bottom"><RouterLink to="/documents" class="side-link" :class="{ active: route.name === 'documents' }">▧ <span v-if="!collapsed">知识文档</span></RouterLink><RouterLink v-if="isStaff" to="/qa-cache" class="side-link" :class="{ active: route.name === 'qa-cache' }">◇ <span v-if="!collapsed">QA 缓存</span></RouterLink><div class="account-row"><span class="avatar">{{ displayName.slice(0, 1).toUpperCase() }}</span><span v-if="!collapsed" class="account-details"><strong>{{ displayName }}</strong><small>{{ isStaff ? '管理员 / 员工' : '企业员工' }}</small></span><button v-if="!collapsed" class="logout" title="退出登录" @click="signOut">↗</button></div></div>
    </aside>
    <div class="app-body"><header class="app-header"><button class="icon-button mobile-toggle" aria-label="打开会话侧栏" @click="mobileOpen = !mobileOpen">☰</button><div class="header-context"><span v-if="route.name !== 'chat'">知识工作台 / </span>{{ pageTitle }}</div></header><main class="app-main"><RouterView /></main></div>
  </div>
  <div v-else aria-hidden="true" />
</template>
