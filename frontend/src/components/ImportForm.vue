<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits(['submit'])
const urlOrAsin = ref('')
</script>
<template>
  <div class="rounded bg-white p-4 shadow">
    <input v-model="urlOrAsin" class="w-full rounded border p-2" placeholder="Amazon URL or ASIN" />
    <button @click="emit('submit', urlOrAsin)" class="mt-2 rounded bg-blue-600 px-3 py-2 text-white">Import</button>
  </div>
</template>
