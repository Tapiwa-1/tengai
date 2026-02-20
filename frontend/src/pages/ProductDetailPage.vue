<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import OfferList from '../components/OfferList.vue'
import { useAppStore } from '../stores/app'

const route = useRoute()
const store = useAppStore()

const toImageUrl = (value?: string) => {
  if (!value) return ''
  if (value.startsWith('http')) return value
  return `http://localhost:5000${value}`
}

onMounted(() => store.getProduct(route.params.id as string))
</script>
<template>
  <section v-if="store.product" class="rounded bg-white p-4 shadow">
    <div class="grid gap-4 md:grid-cols-2">
      <img v-if="store.product.images?.[0]" :src="toImageUrl(store.product.images[0])" class="h-72 w-full object-contain" />
      <div>
        <h1 class="text-2xl font-bold">{{ store.product.title }}</h1>
        <p class="text-gray-600">{{ store.product.brand }}</p>
        <p class="mt-2 text-sm text-gray-700">{{ store.product.description }}</p>
        <p class="mt-2 text-xs text-gray-500">Manual upload catalog · Last updated: {{ store.product.last_synced_at }}</p>
      </div>
    </div>
    <OfferList :offers="store.product.offers || []" class="mt-5" />
  </section>
</template>
