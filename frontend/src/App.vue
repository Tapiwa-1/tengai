<template>
  <div class="mx-auto max-w-6xl p-4">
    <nav class="mb-4 flex gap-3 text-sm">
      <router-link to="/products">Products</router-link>
      <router-link to="/agent/import">Agent Import</router-link>
      <router-link to="/agent/offers">Agent Offers</router-link>
      <router-link to="/checkout">Checkout</router-link>
      <router-link to="/orders">Orders</router-link>
      <router-link to="/admin/offers">Admin</router-link>
    </nav>
    <router-view />
  </div>
</template>
