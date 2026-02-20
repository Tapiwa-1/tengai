const { createApp } = Vue;

createApp({
  data() {
    return {
      products: [],
      categories: [],
      cart: [],
      error: '',
      isLoading: false,
      navLinks: ['Today\'s Deals', 'Customer Service', 'Registry', 'Gift Cards', 'Sell'],
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

      const text = await res.text();
      return text ? JSON.parse(text) : {};
    },
    async fetchProducts() {
      this.isLoading = true;

      try {
        const params = new URLSearchParams(this.filters).toString();
        this.products = await this.request(`/api/products?${params}`);
        this.error = '';
      } catch (_error) {
        this.products = [];
        this.error = 'Could not load products. Start the Express server to use live data.';
      } finally {
        this.isLoading = false;
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
      try {
        await this.request('/api/cart', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ productId })
        });
        await this.fetchCart();
      } catch (_error) {
        this.error = 'Could not add item to cart.';
      }
    },
    async removeFromCart(itemId) {
      try {
        await this.request(`/api/cart/${itemId}`, { method: 'DELETE' });
        await this.fetchCart();
      } catch (_error) {
        this.error = 'Could not remove item from cart.';
      }
    },
    async clearCart() {
      try {
        await this.request('/api/cart', { method: 'DELETE' });
        await this.fetchCart();
      } catch (_error) {
        this.error = 'Could not clear cart.';
      }
    }
  },
  async mounted() {
    await Promise.all([this.fetchProducts(), this.fetchCategories(), this.fetchCart()]);
  }
}).mount('#app');
