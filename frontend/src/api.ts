export type Identity = { user_id: string; role: 'customer' | 'staff'; permissions: string[] }
export type AuthResponse = { identity: Identity; expires_in: number }
export type SseEvent = { type: 'progress' | 'token' | 'reference' | 'card' | 'warning' | 'error' | 'done'; [key: string]: unknown }
export type ApiResponse<T> = { success: boolean; message: string | null; errorCode: string | null; data: T | null }

const base = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api/v1'

async function readResponse<T>(response: Response, fallback: string): Promise<T> {
  const payload = await response.json().catch(() => ({})) as Partial<ApiResponse<T>> & { detail?: string }
  if (!response.ok || payload.success === false) {
    throw new Error(payload.message ?? payload.detail ?? `${fallback}: ${response.status}`)
  }
  return payload.data as T
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${base}${path}`, { credentials: 'include', ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) } })
  return readResponse<T>(response, '请求失败')
}

export const api = {
  auth: {
    login: (username: string, password: string) => request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
    staffLogin: (employee_no: string, password: string) => request<AuthResponse>('/auth/staffLogin', { method: 'POST', body: JSON.stringify({ employee_no, password }) }),
    register: (username: string, real_name: string, password: string) => request<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify({ username, real_name, password }) }),
    current: () => request<Identity>('/auth/userInfo'),
    logout: () => request<null>('/auth/logout', { method: 'POST' }),
  },
  documents: () => request<Array<{ doc_id: number; doc_title: string; status: string; current_version_id?: number }>>('/documents'),
  conversations: () => request<Array<{ conversation_id: string; message_count: string }>>('/chat/conversation/list'),
  messages: (id: string) => request<Array<Record<string, unknown>>>(`/chat/conversation/${id}/messages`),
  deleteConversation: (id: string) => request<{ success: boolean }>(`/chat/conversation/${id}`, { method: 'DELETE' }),
  archiveConversation: (id: string) => request<{ success: boolean }>(`/chat/conversation/${id}/archive`, { method: 'POST' }),
  feedback: (id: string, helpful: boolean, comment?: string) => request<Record<string, unknown>>(`/chat/message/${id}/feedback`, { method: 'POST', body: JSON.stringify({ helpful, comment }) }),
  qaCache: () => request<Array<Record<string, unknown>>>('/qa-cache'),
  review: (id: string, action: 'approve' | 'reject' | 'disable' | 'publish', body: Record<string, unknown> = {}) => request<Record<string, unknown>>(`/qa-cache/${id}/${action}`, { method: 'POST', body: JSON.stringify(body) }),
  async upload(file: File): Promise<Record<string, unknown>> {
    const form = new FormData(); form.append('file', file)
    const response = await fetch(`${base}/documents/upload`, { method: 'POST', credentials: 'include', body: form })
    return readResponse<Record<string, unknown>>(response, '上传失败')
  },
  split: (id: number, text: string, split_type: string, max_length: number) => request<Record<string, unknown>>(`/documents/${id}/split`, { method: 'POST', body: JSON.stringify({ text, split_type, max_length }) }),
  versions: (id: number) => request<Array<Record<string, unknown>>>(`/documents/${id}/versions`),
  segments: (id: number) => request<Array<Record<string, unknown>>>(`/documents/${id}/segments`),
  async streamChat(message: string, conversationId: string | undefined, onEvent: (event: SseEvent) => void, signal?: AbortSignal): Promise<void> {
    const response = await fetch(`${base}/chat/send`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message, conversation_id: conversationId }), signal })
    if (!response.ok || !response.body) throw new Error(`流式请求失败: ${response.status}`)
    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''
    while (true) {
      const { value, done } = await reader.read(); if (done) break
      buffer += decoder.decode(value, { stream: true })
      const chunks = buffer.split('\n\n'); buffer = chunks.pop() ?? ''
      for (const chunk of chunks) { const line = chunk.split('\n').find(item => item.startsWith('data: ')); if (line) onEvent(JSON.parse(line.slice(6)) as SseEvent) }
    }
  },
}
