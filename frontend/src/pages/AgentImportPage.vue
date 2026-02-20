<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ImportForm from '../components/ImportForm.vue'
import api from '../services/api'
import { useAppStore } from '../stores/app'

const token = localStorage.getItem('token') || ''
const store = useAppStore()
const status = ref('')

const runImport = async (payload: any) => {
  const body = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (key === 'images' && Array.isArray(value)) {
      value.forEach((file: File) => body.append('images', file))
      return
    }
    body.append(key, String(value ?? ''))
  })

  await api.post('/agent/import', body, {
    headers: { Authorization: `Bearer ${token}` }
  })

  status.value = 'Product uploaded successfully.'
  await store.getImportHistory(token)
}

onMounted(() => store.getImportHistory(token))
</script>
<template>
  <section>
    <h1 class="mb-2 text-2xl font-bold">Sell on Tengai</h1>
    <p class="mb-4 text-sm text-gray-600">Upload product details manually with images (scraper disabled).</p>
    <ImportForm @submit="runImport" />
    <p v-if="status" class="mt-3 rounded bg-green-100 p-2 text-green-700">{{ status }}</p>
    <ul class="mt-4 space-y-2">
      <li v-for="it in store.importHistory" :key="it.created_at" class="rounded bg-white p-2 shadow-sm">{{ it.asin }} - {{ it.created_at }}</li>
    </ul>
  </section>
</template>
