<script setup lang="ts">
import { onMounted } from 'vue'
import OrderTimeline from '../components/OrderTimeline.vue'
import { useAppStore } from '../stores/app'

const store = useAppStore()
onMounted(() => store.getOrders())
</script>
<template>
  <section>
    <h1 class="mb-3 text-xl font-bold">My Orders</h1>
    <OrderTimeline :orders="store.orders" />
  </section>
</template>
