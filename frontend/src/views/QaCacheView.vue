<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const entries = ref<Array<Record<string, unknown>>>([]); const error = ref('')
async function load() { try { entries.value = await api.qaCache() } catch (e) { error.value = e instanceof Error ? e.message : '加载失败' } }
async function act(entry: Record<string, unknown>, action: 'approve' | 'reject' | 'disable' | 'publish') { try { await api.review(String(entry.id), action); await load() } catch (e) { error.value = e instanceof Error ? e.message : '操作失败' } }
onMounted(load)
</script>
<template><section class="page-section"><div class="page-title"><div><h1>QA 缓存审核</h1><p>审核并沉淀高质量知识问答。</p></div><button class="secondary-button" @click="load">刷新</button></div><p v-if="error" class="form-error">{{ error }}</p><div class="data-panel"><div v-for="entry in entries" :key="String(entry.id)" class="qa-row"><div><strong>{{ entry.question }}</strong><p>{{ entry.answer }}</p><small>{{ entry.status }}</small></div><div class="row-actions"><button v-if="entry.status === 'PENDING'" class="primary-button small" @click="act(entry, 'approve')">批准</button><button v-if="entry.status === 'PENDING'" class="secondary-button small" @click="act(entry, 'reject')">拒绝</button><button v-if="entry.status === 'ACTIVE'" class="secondary-button small" @click="act(entry, 'disable')">下线</button><button v-if="entry.status === 'APPROVED'" class="primary-button small" @click="act(entry, 'publish')">发布</button></div></div><div v-if="!entries.length" class="empty-state">暂无待审核条目</div></div></section></template>
