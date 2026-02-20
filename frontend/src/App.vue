<template>
  <div>
    <header class="top-nav">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <div class="text-2xl font-bold tracking-wide text-orange-400">tengai</div>
        <nav class="flex flex-wrap items-center gap-2 text-sm">
          <router-link class="nav-link" to="/products">Products</router-link>
          <router-link class="nav-link" to="/agent/import">Sell on Tengai</router-link>
          <router-link class="nav-link" to="/agent/offers">Offers</router-link>
          <router-link class="nav-link" to="/checkout">Checkout</router-link>
          <router-link class="nav-link" to="/orders">Orders</router-link>
          <router-link class="nav-link" to="/admin/offers">Admin</router-link>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-6xl p-4">
      <router-view />
    </main>
  </div>
</template>
