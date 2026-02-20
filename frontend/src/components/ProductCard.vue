<script setup lang="ts">
const props = defineProps<{ product: any }>()

const toImageUrl = (value?: string) => {
  if (!value) return ''
  if (value.startsWith('http')) return value
  return `http://localhost:5000${value}`
}
</script>
<template>
  <router-link :to="`/p/${props.product.id}`" class="block rounded bg-white p-4 shadow transition hover:-translate-y-0.5 hover:shadow-md">
    <img v-if="props.product.images?.[0]" :src="toImageUrl(props.product.images[0])" class="mb-2 h-44 w-full object-contain" />
    <h3 class="line-clamp-2 font-semibold">{{ props.product.title }}</h3>
    <p class="text-sm text-gray-600">{{ props.product.brand }}</p>
    <p v-if="props.product.manual_price" class="mt-1 text-lg font-bold text-gray-900">{{ props.product.currency || 'AED' }} {{ props.product.manual_price }}</p>
    <p class="mt-1 text-xs text-gray-500">Last updated: {{ props.product.last_synced_at || 'Not synced' }}</p>
  </router-link>
</template>
