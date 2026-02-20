<script setup lang="ts">
defineProps<{ product: any }>()
</script>
<template>
  <router-link :to="`/p/${product.id}`" class="block rounded bg-white p-4 shadow">
    <img v-if="product.images?.[0]" :src="product.images[0]" class="mb-2 h-32 w-full object-cover" />
    <h3 class="font-semibold">{{ product.title }}</h3>
    <p class="text-sm text-gray-600">{{ product.brand }}</p>
    <p class="mt-1 text-xs text-gray-500">Last updated: {{ product.last_synced_at || 'Not synced' }}</p>
  </router-link>
</template>
