<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from 'vue'
import { chatState, loadConversations, newConversation, sendMessage, stopMessage } from '../chat'
import MessageComposer from '../components/MessageComposer.vue'
import ConversationMessage from '../components/ConversationMessage.vue'

const scroller = ref<HTMLElement>(); const composer = ref<InstanceType<typeof MessageComposer>>(); const autoScroll = ref(true)
const starters = ['查询企业差旅标准', '帮我总结知识库内容', '如何上传和管理文档', '规划一个知识问答流程']
const hasMessages = () => chatState.messages.length > 0
function trackScroll() { if (scroller.value) autoScroll.value = scroller.value.scrollHeight - scroller.value.scrollTop - scroller.value.clientHeight < 100 }
watch(() => chatState.messages.map((message) => `${message.id}:${message.content}:${message.status}`), async () => { await nextTick(); if (scroller.value && autoScroll.value) scroller.value.scrollTop = scroller.value.scrollHeight }, { deep: true })
async function send(text: string) { autoScroll.value = true; await sendMessage(text) }
function starter(text: string) { composer.value?.setDraft(text) }
function startNew() { newConversation(); composer.value?.setDraft('') }
onMounted(() => { if (!chatState.conversations.length) loadConversations().catch(() => undefined) })
</script>

<template>
  <div class="workspace" :class="{ 'is-empty': !hasMessages() }"><section ref="scroller" class="message-scroll" aria-label="知识对话" :aria-busy="chatState.sending" @scroll.passive="trackScroll"><div v-if="!hasMessages()" class="welcome"><div class="welcome-brand"><span class="brand-mark small">K</span><span>KnowHub</span></div><h1>今天，有什么知识问题？</h1><p>检索企业知识、梳理文档内容，让每一次问答都有依据。</p></div><div v-else class="message-thread"><ConversationMessage v-for="message in chatState.messages" :key="message.id" :message="message" /></div></section><div class="composer-dock"><MessageComposer ref="composer" :sending="chatState.sending" @send="send" @stop="stopMessage" /><div v-if="!hasMessages()" class="starter-list"><button v-for="item in starters" :key="item" @click="starter(item)">{{ item }}</button></div><p v-if="chatState.error" class="workspace-error" role="alert">{{ chatState.error }}</p></div><footer v-if="!hasMessages()" class="workspace-footer">KnowHub 可能会生成不准确内容，请结合原始资料判断。</footer></div>
</template>
