<script setup lang="ts">
import { reactive, ref } from 'vue'

const emit = defineEmits(['submit'])
const fileInput = ref<HTMLInputElement | null>(null)

const form = reactive({
  title: '',
  brand: '',
  category: '',
  description: '',
  manual_price: '',
  currency: 'AED',
  amazon_url: ''
})

const submit = () => {
  const files = fileInput.value?.files ? Array.from(fileInput.value.files) : []
  emit('submit', { ...form, images: files })
}
</script>

<template>
  <div class="rounded bg-white p-4 shadow">
    <h3 class="mb-3 text-lg font-semibold">Manual Product Upload</h3>
    <div class="grid gap-3 md:grid-cols-2">
      <input v-model="form.title" class="rounded border p-2" placeholder="Product title" />
      <input v-model="form.brand" class="rounded border p-2" placeholder="Brand" />
      <input v-model="form.category" class="rounded border p-2" placeholder="Category" />
      <input v-model="form.manual_price" class="rounded border p-2" placeholder="Price" type="number" step="0.01" />
      <input v-model="form.currency" class="rounded border p-2" placeholder="Currency" />
      <input v-model="form.amazon_url" class="rounded border p-2" placeholder="Reference URL (optional)" />
      <textarea v-model="form.description" class="rounded border p-2 md:col-span-2" rows="4" placeholder="Description"></textarea>
      <input ref="fileInput" class="md:col-span-2" type="file" multiple accept="image/*" />
    </div>
    <button class="amazon-btn mt-4" @click="submit">Upload Product</button>
  </div>
</template>
