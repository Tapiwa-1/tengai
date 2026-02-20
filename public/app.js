const { createApp } = Vue;

createApp({
  data() {
    return {
      products: [],
      categories: [],
      cart: [],
      error: '',
      filters: {
        q: '',
        category: '',
        sort: ''
      }
    };
  },
  computed: {
    cartCount() {
      return this.cart.reduce((total, item) => total + item.quantity, 0);
    },
    cartSubtotal() {
      return this.cart.reduce((total, item) => total + item.price * item.quantity, 0);
    }
  },
  methods: {
    async request(url, options) {
      const res = await fetch(url, options);
      if (!res.ok) {
        throw new Error(`Request failed: ${res.status}`);
      }
      return res.json();
    },
    async fetchProducts() {
      try {
        const params = new URLSearchParams(this.filters).toString();
        this.products = await this.request(`/api/products?${params}`);
        this.error = '';
      } catch (_error) {
        this.error = 'Could not load products. Start the Express server to use live data.';
      }
    },
    async fetchCategories() {
      try {
        this.categories = await this.request('/api/categories');
      } catch (_error) {
        this.categories = [];
      }
    },
    async fetchCart() {
      try {
        this.cart = await this.request('/api/cart');
      } catch (_error) {
        this.cart = [];
      }
    },
    async addToCart(productId) {
      await this.request('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId })
      });
      await this.fetchCart();
    },
    async removeFromCart(itemId) {
      await this.request(`/api/cart/${itemId}`, { method: 'DELETE' });
      await this.fetchCart();
    },
    async clearCart() {
      await this.request('/api/cart', { method: 'DELETE' });
      await this.fetchCart();
    }
  },
  async mounted() {
    await Promise.all([this.fetchProducts(), this.fetchCategories(), this.fetchCart()]);
  }
}).mount('#app');
