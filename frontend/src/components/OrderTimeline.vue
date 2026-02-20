<script setup lang="ts">
defineProps<{ orders: any[] }>()
</script>
<template>
  <div class="space-y-3">
    <div v-for="order in orders" :key="order.id" class="rounded bg-white p-3 shadow">
      <p>Order #{{ order.id }}</p>
      <p class="text-sm">Status: {{ order.status }}</p>
      <p class="text-sm">Total: AED {{ order.selling_total }}</p>
    </div>
  </div>
</template>
