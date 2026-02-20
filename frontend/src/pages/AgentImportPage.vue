<script setup lang="ts">
import { onMounted } from 'vue'
import ImportForm from '../components/ImportForm.vue'
import api from '../services/api'
import { useAppStore } from '../stores/app'

const token = localStorage.getItem('token') || ''
const store = useAppStore()

const runImport = async (urlOrAsin: string) => {
  await api.post('/agent/import', { url_or_asin: urlOrAsin }, { headers: { Authorization: `Bearer ${token}` } })
  await store.getImportHistory(token)
}

onMounted(() => store.getImportHistory(token))
</script>
<template>
  <section>
    <h1 class="mb-2 text-xl font-bold">Import Product</h1>
    <ImportForm @submit="runImport" />
    <ul class="mt-4 space-y-2">
      <li v-for="it in store.importHistory" :key="it.created_at" class="rounded bg-white p-2">{{ it.asin }} - {{ it.created_at }}</li>
    </ul>
  </section>
</template>
