import { reactive } from 'vue'
import { api, type Identity } from './api'

export const authState = reactive<{ identity: Identity | null; ready: boolean }>({ identity: null, ready: false })

export async function restoreAuth() {
  if (authState.ready) return authState.identity
  try { authState.identity = await api.auth.current() } catch { authState.identity = null }
  authState.ready = true
  return authState.identity
}

export async function clearAuth() {
  try { await api.auth.logout() } catch { /* The local state still must be cleared. */ }
  authState.identity = null
}
