<script setup lang="ts">
defineProps<{ modelValue: string }>()
const emit = defineEmits(['update:modelValue'])
</script>
<template>
  <input :value="modelValue" @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    placeholder="Search products" class="w-full rounded border p-2" />
</template>
