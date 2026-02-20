<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

const products = ref([]);
const categories = ref([]);
const cart = ref([]);
const error = ref('');
const isLoading = ref(false);
const navLinks = ["Today's Deals", 'Customer Service', 'Registry', 'Gift Cards', 'Sell'];

const filters = reactive({
  q: '',
  category: '',
  sort: ''
});

const cartCount = computed(() => cart.value.reduce((total, item) => total + item.quantity, 0));
const cartSubtotal = computed(() => cart.value.reduce((total, item) => total + item.price * item.quantity, 0));

async function request(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

async function fetchProducts() {
  isLoading.value = true;
  try {
    const query = new URLSearchParams(filters).toString();
    products.value = await request(`/api/products?${query}`);
    error.value = '';
  } catch (_err) {
    products.value = [];
    error.value = 'Could not load products. Start the Express server to use live data.';
  } finally {
    isLoading.value = false;
  }
}

async function fetchCategories() {
  try {
    categories.value = await request('/api/categories');
  } catch (_err) {
    categories.value = [];
  }
}

async function fetchCart() {
  try {
    cart.value = await request('/api/cart');
  } catch (_err) {
    cart.value = [];
  }
}

async function addToCart(productId) {
  try {
    await request('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ productId })
    });
    await fetchCart();
  } catch (_err) {
    error.value = 'Could not add item to cart.';
  }
}

async function removeFromCart(itemId) {
  try {
    await request(`/api/cart/${itemId}`, { method: 'DELETE' });
    await fetchCart();
  } catch (_err) {
    error.value = 'Could not remove item from cart.';
  }
}

async function clearCart() {
  try {
    await request('/api/cart', { method: 'DELETE' });
    await fetchCart();
  } catch (_err) {
    error.value = 'Could not clear cart.';
  }
}

onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories(), fetchCart()]);
});
</script>

<template>
  <div class="page">
    <header class="top-nav">
      <div class="logo">tengai<span>.shop</span></div>
      <div class="search-wrap">
        <input v-model.trim="filters.q" @keyup.enter="fetchProducts" placeholder="Search Tengai products" />
        <button @click="fetchProducts">Search</button>
      </div>
      <div class="cart-chip">Cart: {{ cartCount }} items</div>
    </header>

    <div class="sub-nav">
      <span v-for="link in navLinks" :key="link">{{ link }}</span>
    </div>

    <main class="layout">
      <aside class="sidebar">
        <h2>Filters</h2>
        <label>Category</label>
        <select v-model="filters.category" @change="fetchProducts">
          <option value="">All</option>
          <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
        </select>

        <label>Sort</label>
        <select v-model="filters.sort" @change="fetchProducts">
          <option value="">Featured</option>
          <option value="price-asc">Price: Low to High</option>
          <option value="price-desc">Price: High to Low</option>
          <option value="rating">Avg. Customer Review</option>
        </select>
      </aside>

      <section>
        <div class="section-head">
          <h1>Vue storefront</h1>
          <p v-if="error" class="error">{{ error }}</p>
        </div>

        <div v-if="isLoading" class="state-card">Loading products…</div>
        <div v-else-if="products.length === 0" class="state-card">No products found. Try different filters.</div>

        <div v-else class="products-grid">
          <article v-for="product in products" :key="product.id" class="card">
            <span v-if="product.badge" class="badge">{{ product.badge }}</span>
            <img :src="product.image" :alt="product.title" />
            <h3>{{ product.title }}</h3>
            <p class="description">{{ product.description }}</p>
            <div class="meta">
              <span>⭐ {{ product.rating }}</span>
              <span class="price">${{ product.price.toFixed(2) }}</span>
            </div>
            <button @click="addToCart(product.id)">Add to Cart</button>
          </article>
        </div>
      </section>

      <aside class="cart-panel">
        <h2>Your Cart</h2>
        <p v-if="cart.length === 0" class="muted">Your cart is empty.</p>
        <div v-for="item in cart" :key="item.id" class="cart-item">
          <img :src="item.image" :alt="item.title" />
          <div>
            <p>{{ item.title }}</p>
            <small>${{ item.price.toFixed(2) }} × {{ item.quantity }}</small>
          </div>
          <button class="icon-btn" @click="removeFromCart(item.id)">✕</button>
        </div>
        <p class="subtotal">Subtotal: ${{ cartSubtotal.toFixed(2) }}</p>
        <button :disabled="cart.length === 0" @click="clearCart">Clear cart</button>
      </aside>
    </main>
  </div>
</template>
