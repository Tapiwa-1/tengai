<script setup lang="ts">
defineProps<{ offers: any[] }>()
</script>
<template>
  <div class="space-y-2">
    <div v-for="offer in offers" :key="offer.id" class="rounded border bg-white p-3">
      <p class="font-semibold">AED {{ offer.selling_price }}</p>
      <p class="text-sm">Delivery {{ offer.delivery_days }} days</p>
      <p class="text-sm text-gray-600">{{ offer.notes }}</p>
    </div>
  </div>
</template>
