<script setup lang="ts">
import { onMounted, ref } from 'vue'
import ProductCard from '../components/ProductCard.vue'
import SearchBar from '../components/SearchBar.vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()
const query = ref('')

onMounted(() => store.searchProducts())
</script>
<template>
  <section>
    <h1 class="mb-2 text-xl font-bold">Products</h1>
    <SearchBar v-model="query" />
    <button @click="store.searchProducts(query)" class="my-2 rounded bg-blue-600 px-3 py-2 text-white">Search</button>
    <p class="mb-3 text-xs text-gray-500">Data provided via Amazon Product API</p>
    <div class="grid gap-3 md:grid-cols-3">
      <ProductCard v-for="product in store.products" :key="product.id" :product="product" />
    </div>
  </section>
</template>
