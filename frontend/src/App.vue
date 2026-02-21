<script setup>
import { computed, onMounted, reactive, ref } from 'vue';

const products = ref([]);
const categories = ref([]);
const deals = ref([]);
const cart = ref([]);
const orders = ref([]);
const error = ref('');
const info = ref('');
const isLoading = ref(false);
const navLinks = ["Today's Deals", 'Customer Service', 'Registry', 'Gift Cards', 'Sell'];

const filters = reactive({
  q: '',
  category: '',
  sort: ''
});

const couponCode = ref('');
const appliedCoupon = ref(null);
const isCheckingOut = ref(false);

const cartCount = computed(() => cart.value.reduce((total, item) => total + item.quantity, 0));
const cartSubtotal = computed(() => cart.value.reduce((total, item) => total + item.price * item.quantity, 0));
const cartDiscount = computed(() => {
  if (!appliedCoupon.value) {
    return 0;
  }

  return cartSubtotal.value * (appliedCoupon.value.discountPercent / 100);
});
const cartTotal = computed(() => Math.max(cartSubtotal.value - cartDiscount.value, 0));

async function request(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};

  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }

  return payload;
}

async function fetchProducts() {
  isLoading.value = true;
  try {
    const query = new URLSearchParams(filters).toString();
    products.value = await request(`/api/products?${query}`);
    error.value = '';
  } catch (err) {
    products.value = [];
    error.value = err.message || 'Could not load products. Start the Express server to use live data.';
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

async function fetchDeals() {
  try {
    deals.value = await request('/api/deals');
  } catch (_err) {
    deals.value = [];
  }
}

async function fetchOrders() {
  try {
    orders.value = await request('/api/orders');
  } catch (_err) {
    orders.value = [];
  }
}

async function fetchCart() {
  try {
    cart.value = await request('/api/cart');
    if (cart.value.length === 0) {
      appliedCoupon.value = null;
    }
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
    info.value = 'Added item to cart.';
    error.value = '';
    await fetchCart();
  } catch (err) {
    error.value = err.message || 'Could not add item to cart.';
  }
}

async function removeFromCart(itemId) {
  try {
    await request(`/api/cart/${itemId}`, { method: 'DELETE' });
    info.value = 'Removed item from cart.';
    error.value = '';
    await fetchCart();
  } catch (err) {
    error.value = err.message || 'Could not remove item from cart.';
  }
}

async function clearCart() {
  try {
    await request('/api/cart', { method: 'DELETE' });
    appliedCoupon.value = null;
    info.value = 'Cart cleared.';
    error.value = '';
    await fetchCart();
  } catch (err) {
    error.value = err.message || 'Could not clear cart.';
  }
}

async function applyCoupon() {
  try {
    const data = await request('/api/cart/apply-coupon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: couponCode.value })
    });

    appliedCoupon.value = {
      code: data.code,
      discountPercent: data.discountPercent
    };
    info.value = `Coupon ${data.code} applied.`;
    error.value = '';
  } catch (err) {
    appliedCoupon.value = null;
    error.value = err.message || 'Could not apply coupon.';
  }
}

async function checkout() {
  isCheckingOut.value = true;
  try {
    const data = await request('/api/checkout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ couponCode: appliedCoupon.value?.code || '' })
    });

    info.value = `Order #${data.orderId} placed successfully.`;
    error.value = '';
    couponCode.value = '';
    appliedCoupon.value = null;
    await Promise.all([fetchCart(), fetchOrders()]);
  } catch (err) {
    error.value = err.message || 'Could not complete checkout.';
  } finally {
    isCheckingOut.value = false;
  }
}

onMounted(async () => {
  await Promise.all([fetchProducts(), fetchCategories(), fetchCart(), fetchDeals(), fetchOrders()]);
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

        <section class="orders-box">
          <h3>Recent Orders</h3>
          <p v-if="orders.length === 0" class="muted">No orders yet.</p>
          <ul v-else>
            <li v-for="order in orders" :key="order.id">
              <strong>#{{ order.id }}</strong>
              <span>${{ order.total.toFixed(2) }}</span>
            </li>
          </ul>
        </section>
      </aside>

      <section>
        <div class="section-head">
          <h1>Vue storefront</h1>
          <div>
            <p v-if="error" class="error">{{ error }}</p>
            <p v-else-if="info" class="info">{{ info }}</p>
          </div>
        </div>

        <section class="deals-strip" v-if="deals.length">
          <h2>Deals for you</h2>
          <div class="deal-list">
            <article v-for="deal in deals" :key="deal.id" class="deal-card">
              <img :src="deal.image" :alt="deal.title" />
              <div>
                <p>{{ deal.title }}</p>
                <small>{{ deal.badge || 'Special offer' }} • ⭐ {{ deal.rating }}</small>
                <p class="price">${{ deal.price.toFixed(2) }}</p>
              </div>
            </article>
          </div>
        </section>

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

        <div class="coupon-row">
          <input v-model.trim="couponCode" placeholder="Coupon code" />
          <button :disabled="!couponCode" @click="applyCoupon">Apply</button>
        </div>

        <p class="subtotal">Subtotal: ${{ cartSubtotal.toFixed(2) }}</p>
        <p v-if="appliedCoupon" class="discount">Discount ({{ appliedCoupon.code }}): -${{ cartDiscount.toFixed(2) }}</p>
        <p class="subtotal">Total: ${{ cartTotal.toFixed(2) }}</p>

        <div class="cart-actions">
          <button :disabled="cart.length === 0 || isCheckingOut" @click="checkout">{{ isCheckingOut ? 'Placing order...' : 'Buy now' }}</button>
          <button :disabled="cart.length === 0" @click="clearCart">Clear cart</button>
        </div>
      </aside>
    </main>
  </div>
</template>
