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
    <h1 class="mb-2 text-2xl font-bold">Today's picks for you</h1>
    <SearchBar v-model="query" />
    <button @click="store.searchProducts(query)" class="amazon-btn my-3">Search</button>
    <p class="mb-3 text-xs text-gray-500">Products are uploaded by Tengai agents with manual verification.</p>
    <div class="grid gap-3 md:grid-cols-3">
      <ProductCard v-for="product in store.products" :key="product.id" :product="product" />
    </div>
  </section>
</template>
