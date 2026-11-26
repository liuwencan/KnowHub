import { reactive } from 'vue'
import { api, type SseEvent } from './api'

export interface ChatConversation { id: string; title: string; messageCount: number }
export interface ChatMessage { id: string; role: 'user' | 'assistant'; content: string; status: 'streaming' | 'completed' | 'failed' | 'cancelled'; references?: Array<Record<string, unknown>>; error?: string }

export const chatState = reactive({
  conversations: [] as ChatConversation[],
  activeId: null as string | null,
  messages: [] as ChatMessage[],
  loading: false,
  sending: false,
  abortController: null as AbortController | null,
  error: '',
})

function normalizeMessage(raw: Record<string, unknown>): ChatMessage {
  return { id: String(raw.message_id ?? raw.id ?? crypto.randomUUID()), role: raw.role === 'user' ? 'user' : 'assistant', content: String(raw.content ?? ''), status: 'completed', references: Array.isArray(raw.references) ? raw.references as Array<Record<string, unknown>> : [] }
}

export async function loadConversations() {
  chatState.loading = true
  try {
    const rows = await api.conversations()
    chatState.conversations = rows.map((row) => ({ id: row.conversation_id, title: row.conversation_id.slice(0, 18), messageCount: Number(row.message_count) || 0 }))
  } finally { chatState.loading = false }
}

export async function selectConversation(id: string) {
  chatState.activeId = id
  chatState.messages = (await api.messages(id)).map(normalizeMessage)
}

export function newConversation() { chatState.activeId = null; chatState.messages = []; chatState.error = '' }
export function resetChat() { chatState.conversations = []; newConversation() }

export async function sendMessage(content: string) {
  const text = content.trim()
  if (!text || chatState.sending) return
  chatState.error = ''
  chatState.sending = true
  chatState.abortController = new AbortController()
  const user: ChatMessage = { id: `local-user-${Date.now()}`, role: 'user', content: text, status: 'completed' }
  const assistant: ChatMessage = { id: `local-assistant-${Date.now()}`, role: 'assistant', content: '', status: 'streaming', references: [] }
  chatState.messages.push(user, assistant)
  try {
    await api.streamChat(text, chatState.activeId ?? undefined, (event: SseEvent) => applyEvent(assistant, event), chatState.abortController?.signal)
    if (assistant.status === 'streaming') assistant.status = chatState.abortController?.signal.aborted ? 'cancelled' : 'completed'
  } catch (error) {
    assistant.status = chatState.abortController?.signal.aborted ? 'cancelled' : 'failed'
    assistant.error = error instanceof Error ? error.message : '流式响应失败'
    chatState.error = assistant.error
  } finally {
    chatState.sending = false
    chatState.abortController = null
    await loadConversations()
  }
}

function applyEvent(assistant: ChatMessage, event: SseEvent) {
  if (event.type === 'token') assistant.content += String(event.content ?? '')
  if (event.type === 'reference' && Array.isArray(event.data)) assistant.references = event.data as Array<Record<string, unknown>>
  if (event.type === 'done' && event.conversation_id) {
    chatState.activeId = String(event.conversation_id)
    assistant.status = 'completed'
  }
  if (event.type === 'error') { assistant.status = 'failed'; assistant.error = String(event.message ?? '流式响应失败') }
}

export function stopMessage() { chatState.abortController?.abort(); if (chatState.messages.at(-1)?.status === 'streaming') chatState.messages.at(-1)!.status = 'cancelled' }
