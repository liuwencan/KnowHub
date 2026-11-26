<script setup lang="ts">
import { RouterView } from 'vue-router'

</script>

<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" v-if="Component" />
    <div v-else class="route-loading">正在加载工作台…</div>
  </RouterView>
</template>
