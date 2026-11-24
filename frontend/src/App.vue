<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { api, type Identity, type SseEvent } from './api'
import { useRoute, useRouter } from 'vue-router'

const identity = ref<Identity | null>(null)
const phone = ref(''); const password = ref(''); const message = ref(''); const answer = ref(''); const conversationId = ref<string>()
const documents = ref<Array<{ doc_id: number; doc_title: string; status: string }>>([]); const cacheEntries = ref<Array<Record<string, unknown>>>([])
const conversations = ref<Array<{ conversation_id: string; message_count: string }>>([]); const citations = ref<Array<Record<string, unknown>>>([]); const cards = ref<Array<Record<string, unknown>>>([])
const error = ref(''); const busy = ref(false); const view = ref<'chat' | 'documents' | 'cache'>('chat')
const loginAsStaff = ref(false); const uploadFile = ref<File | null>(null); const splitText = ref(''); const splitType = ref('smart'); const maxLength = ref(1200)
const isStaff = computed(() => identity.value?.role === 'staff')
const router = useRouter(); const route = useRoute()
watch(() => route.name, (name) => { view.value = name === 'documents' ? 'documents' : name === 'qa-cache' ? 'cache' : 'chat' }, { immediate: true })

async function login() { error.value = ''; try { const result = await api.login(phone.value, password.value); identity.value = result.identity; await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '登录失败' } }
async function staffLogin() { error.value = ''; try { const result = await api.staffLogin(phone.value, password.value); identity.value = result.identity; await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '登录失败' } }
async function refresh() { documents.value = await api.documents(); conversations.value = await api.conversations(); if (isStaff.value) cacheEntries.value = await api.qaCache() }
async function send() { if (!message.value.trim()) return; busy.value = true; answer.value = ''; citations.value = []; cards.value = []; error.value = ''; try { await api.streamChat(message.value, conversationId.value, (event: SseEvent) => { if (event.type === 'token') answer.value += String(event.content ?? ''); if (event.type === 'reference' && Array.isArray(event.data)) citations.value = event.data as Array<Record<string, unknown>>; if (event.type === 'card' && typeof event.data === 'object') cards.value.push(event.data as Record<string, unknown>); if (event.type === 'done') { conversationId.value = String(event.conversation_id ?? ''); refresh() } }) } catch (e) { error.value = e instanceof Error ? e.message : '流式请求失败' } finally { busy.value = false } }
async function openConversation(id: string) { const items = await api.messages(id); conversationId.value = id; answer.value = String(items.filter(item => item.role === 'assistant').map(item => item.content ?? '').join('\n')); view.value = 'chat' }
async function removeConversation(id: string) { await api.deleteConversation(id); if (conversationId.value === id) { conversationId.value = undefined; answer.value = '' } await refresh() }
async function rateAnswer(helpful: boolean) { const items = conversationId.value ? await api.messages(conversationId.value) : []; const assistant = [...items].reverse().find(item => item.role === 'assistant'); if (assistant?.message_id) await api.feedback(String(assistant.message_id), helpful) }
async function logout() { await api.logout(); identity.value = null; conversationId.value = undefined }
async function upload() { if (!uploadFile.value) return; busy.value = true; try { await api.upload(uploadFile.value); uploadFile.value = null; await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '上传失败' } finally { busy.value = false } }
async function approve(entry: Record<string, unknown>) { try { await api.review(String(entry.id), 'approve'); await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '审核失败' } }
async function reject(entry: Record<string, unknown>) { try { await api.review(String(entry.id), 'reject'); await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '审核失败' } }
async function disable(entry: Record<string, unknown>) { try { await api.review(String(entry.id), 'disable', { comment: 'MANUAL' }); await refresh() } catch (e) { error.value = e instanceof Error ? e.message : '下线失败' } }
onMounted(() => { /* session is established by the API cookie after login */ })
</script>

<template>
  <main class="shell">
    <section v-if="!identity" class="login-panel">
      <p class="eyebrow">KONWHUB</p><h1>企业知识问答</h1><p class="muted">登录后访问对话、文档和审核工作流。</p>
      <form @submit.prevent="loginAsStaff ? staffLogin() : login()"><label>账号<input v-model="phone" autocomplete="username" required /></label><label>密码<input v-model="password" type="password" autocomplete="current-password" required /></label><label class="check"><input v-model="loginAsStaff" type="checkbox" />员工登录</label><button type="submit">登录</button></form>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
    <section v-else class="app-panel">
      <header><div><p class="eyebrow">KONWHUB</p><h1>知识工作台</h1></div><div class="identity">{{ identity.user_id }} · {{ identity.role }} <button class="ghost" @click="logout">退出</button></div></header>
      <nav><button :class="{active: route.name === 'chat'}" @click="router.push('/chat')">对话</button><button :class="{active: route.name === 'documents'}" @click="router.push('/documents'); refresh()">文档</button><button v-if="isStaff" :class="{active: route.name === 'qa-cache'}" @click="router.push('/qa-cache'); refresh()">QA 缓存</button></nav>
      <section v-if="view === 'chat'" class="workspace chat-layout"><aside class="history"><div class="section-title"><h2>历史</h2><button class="ghost" @click="conversationId = undefined; answer = ''">新建</button></div><ul><li v-for="item in conversations" :key="item.conversation_id"><button class="history-item" @click="openConversation(item.conversation_id)">{{ item.conversation_id.slice(0, 10) }}</button><button class="ghost" title="删除会话" @click="removeConversation(item.conversation_id)">×</button></li></ul></aside><div class="chat-main"><div class="answer">{{ answer || '输入问题开始对话。' }}<div v-if="citations.length" class="citations"><h3>引用</h3><div v-for="citation in citations" :key="String(citation.chunk_id)">文档 {{ citation.document_id }} · {{ citation.source }} · {{ citation.score }}</div></div><div v-for="(card, index) in cards" :key="index" class="business-card">{{ card }}</div></div><form class="composer" @submit.prevent="send"><textarea v-model="message" placeholder="请输入问题" :disabled="busy" /><button type="submit" :disabled="busy">{{ busy ? '处理中…' : '发送' }}</button></form><div class="feedback"><button class="secondary" @click="rateAnswer(true)">有帮助</button><button class="secondary" @click="rateAnswer(false)">没帮助</button></div></div></section>
      <section v-else-if="view === 'documents'" class="workspace"><div class="section-title"><h2>文档</h2><button @click="refresh">刷新</button></div><form v-if="isStaff" class="upload-form" @submit.prevent="upload"><input type="file" accept=".pdf,.docx,.xlsx,.xlsm,.csv,.md,.txt" @change="uploadFile = ($event.target as HTMLInputElement).files?.[0] ?? null" /><button :disabled="busy">上传文档</button></form><ul><li v-for="document in documents" :key="document.doc_id"><strong>{{ document.doc_title }}</strong><span>{{ document.status }}</span></li><li v-if="!documents.length" class="muted">暂无文档</li></ul><div v-if="isStaff" class="split-tools"><h3>切分预览</h3><textarea v-model="splitText" placeholder="粘贴文档文本" /><select v-model="splitType"><option value="smart">智能切分</option><option value="markdown_parent_child">Markdown 父子</option><option value="markdown_sibling">Markdown 兄弟</option><option value="length">按长度</option><option value="regex">正则/分隔符</option></select><input v-model.number="maxLength" type="number" min="100" max="10000" /><p class="muted">上传后可选择文档查看版本、片段和表格预览。</p></div></section>
      <section v-else class="workspace"><div class="section-title"><h2>QA 缓存审核</h2><button @click="refresh">刷新</button></div><ul><li v-for="entry in cacheEntries" :key="String(entry.id)"><div><strong>{{ entry.question }}</strong><p class="muted">{{ entry.status }} · {{ entry.answer }}</p></div><div class="actions"><button v-if="entry.status === 'PENDING'" @click="approve(entry)">批准</button><button v-if="entry.status === 'PENDING'" class="secondary" @click="reject(entry)">拒绝</button><button v-if="entry.status === 'ACTIVE'" class="secondary" @click="disable(entry)">下线</button><button v-if="entry.status === 'APPROVED'" @click="api.review(String(entry.id), 'publish').then(refresh)">发布</button></div></li><li v-if="!cacheEntries.length" class="muted">暂无待审核条目</li></ul></section>
      <p v-if="error" class="error">{{ error }}</p>
    </section>
  </main>
</template>
