<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { authState } from '../authState'

const router = useRouter(); const route = useRoute(); const mode = ref<'login' | 'register'>('login'); const staff = ref(false); const busy = ref(false); const error = ref('')
const form = reactive({ username: '', realName: '', password: '', confirmPassword: '' })
const title = computed(() => mode.value === 'login' ? '登录知识工作台' : '创建企业账号')
function changeMode(next: 'login' | 'register') { if (busy.value) return; mode.value = next; error.value = ''; form.password = ''; form.confirmPassword = '' }
async function submit() {
  error.value = ''; const username = form.username.trim()
  if (!username || !form.password) { error.value = '请输入账号和密码'; return }
  if (mode.value === 'register' && (!form.realName.trim() || form.password !== form.confirmPassword)) { error.value = !form.realName.trim() ? '请输入真实姓名' : '两次输入的密码不一致'; return }
  if (form.password.length < 6) { error.value = '密码至少需要 6 位'; return }
  busy.value = true
  try {
    const result = mode.value === 'register' ? await api.auth.register(username, form.realName.trim(), form.password) : staff.value ? await api.auth.staffLogin(username, form.password) : await api.auth.login(username, form.password)
    authState.identity = result.identity; authState.ready = true
    router.replace(String(route.query.redirect || '/chat'))
  } catch (e) { error.value = e instanceof Error ? e.message : '请求失败，请稍后重试' } finally { busy.value = false }
}
</script>

<template>
  <main class="login-page"><header class="login-header"><RouterLink to="/login" class="brand-link"><span class="brand-mark">K</span><span class="brand-copy"><strong>KnowHub</strong><small>企业知识助手</small></span></RouterLink><span class="login-space-label">企业内部工作空间</span></header><div class="login-content"><section class="login-intro"><h1>让知识，<br />在对话中流动。</h1><p>从检索企业资料，到沉淀每一次问答。<br />一个对话，把复杂信息理清楚。</p><div class="intro-rule"><span /><i>KNOWLEDGE WORKSPACE</i><span /></div><ul><li>企业知识检索</li><li>智能问答协作</li><li>内容审核沉淀</li></ul></section><section class="login-panel"><div class="login-card"><div class="auth-mode"><button :class="{ active: mode === 'login' }" :disabled="busy" @click="changeMode('login')">登录</button><button :class="{ active: mode === 'register' }" :disabled="busy" @click="changeMode('register')">注册</button></div><h2>{{ title }}</h2><p class="login-description">{{ mode === 'login' ? '使用企业账号，继续你的知识工作。' : '注册后即可使用 KnowHub 企业知识空间。' }}</p><form @submit.prevent="submit"><label>企业账号<input v-model="form.username" autocomplete="username" placeholder="用户名或员工工号" :disabled="busy" /></label><label v-if="mode === 'register'">真实姓名<input v-model="form.realName" autocomplete="name" placeholder="请输入真实姓名" :disabled="busy" /></label><label>密码<input v-model="form.password" type="password" :autocomplete="mode === 'login' ? 'current-password' : 'new-password'" placeholder="至少 6 位" :disabled="busy" /></label><label v-if="mode === 'register'">确认密码<input v-model="form.confirmPassword" type="password" autocomplete="new-password" placeholder="再次输入密码" :disabled="busy" /></label><label v-if="mode === 'login'" class="check"><input v-model="staff" type="checkbox" :disabled="busy" />员工登录</label><p v-if="error" class="form-error" role="alert">{{ error }}</p><button class="primary-button" type="submit" :disabled="busy">{{ busy ? '处理中…' : mode === 'login' ? '登录' : '创建账号' }}</button></form></div></section></div><footer class="login-footer">KnowHub<span>仅供企业内部使用</span></footer></main>
</template>
