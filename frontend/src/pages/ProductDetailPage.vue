<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import OfferList from '../components/OfferList.vue'
import { useAppStore } from '../stores/app'

const route = useRoute()
const store = useAppStore()
onMounted(() => store.getProduct(route.params.id as string))
</script>
<template>
  <section v-if="store.product">
    <h1 class="text-xl font-bold">{{ store.product.title }}</h1>
    <p class="text-gray-600">{{ store.product.brand }}</p>
    <p class="text-xs text-gray-500">Data provided via Amazon Product API · Last updated: {{ store.product.last_synced_at }}</p>
    <OfferList :offers="store.product.offers || []" class="mt-3" />
  </section>
</template>
