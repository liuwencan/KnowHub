<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
const props = defineProps<{ sending: boolean }>(); const emit = defineEmits<{ send: [value: string]; stop: [] }>(); const value = ref(''); const input = ref<HTMLTextAreaElement>()
function resize() { if (!input.value) return; input.value.style.height = 'auto'; input.value.style.height = `${Math.min(188, Math.max(52, input.value.scrollHeight))}px` }
watch(value, resize, { flush: 'post' }); onMounted(resize)
function submit() { if (props.sending || !value.value.trim()) return; emit('send', value.value.trim()); value.value = '' }
function keydown(event: KeyboardEvent) { if (event.isComposing || event.keyCode === 229) return; if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit() } }
async function setDraft(text: string) { value.value = text; await nextTick(); input.value?.focus() }
defineExpose({ setDraft })
</script>
<template><div class="composer" :class="{ 'is-sending': sending }"><textarea ref="input" v-model="value" rows="2" maxlength="20000" aria-label="知识问题" placeholder="告诉我你想了解的企业知识…" @keydown="keydown" /><div class="composer-actions"><span class="composer-context"><span class="context-dot" />KnowHub 知识咨询</span><span class="composer-keyboard">Enter 发送，Shift + Enter 换行</span><button v-if="sending" class="stop-button" aria-label="暂停生成" @click="emit('stop')">暂停生成</button><button v-else class="send-button" :disabled="!value.trim()" aria-label="发送消息" @click="submit">↑</button></div></div></template>
