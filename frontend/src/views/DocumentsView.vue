<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'
const documents = ref<Array<{ doc_id: number; doc_title: string; status: string }>>([]); const error = ref(''); const busy = ref(false); const file = ref<File | null>(null)
async function load() { try { documents.value = await api.documents() } catch (e) { error.value = e instanceof Error ? e.message : '文档加载失败' } }
async function upload() { if (!file.value) return; busy.value = true; try { await api.upload(file.value); file.value = null; await load() } catch (e) { error.value = e instanceof Error ? e.message : '上传失败' } finally { busy.value = false } }
onMounted(load)
</script>
<template><section class="page-section"><div class="page-title"><div><h1>知识文档</h1><p>管理企业知识来源，为对话提供可靠依据。</p></div><button class="secondary-button" @click="load">刷新</button></div><form class="upload-strip" @submit.prevent="upload"><input type="file" accept=".pdf,.docx,.xlsx,.xlsm,.csv,.md,.txt" @change="file = ($event.target as HTMLInputElement).files?.[0] ?? null" /><button class="primary-button" :disabled="busy">{{ busy ? '上传中…' : '上传文档' }}</button></form><p v-if="error" class="form-error">{{ error }}</p><div class="data-panel"><div class="data-heading"><strong>全部文档</strong><span>{{ documents.length }} 个条目</span></div><div v-for="document in documents" :key="document.doc_id" class="data-row"><div><strong>{{ document.doc_title }}</strong><small>ID {{ document.doc_id }}</small></div><span class="status-chip">{{ document.status }}</span></div><div v-if="!documents.length" class="empty-state">暂无文档</div></div></section></template>
