const { createApp } = Vue;

createApp({
  data() {
    return {
      products: [],
      categories: [],
      cart: [],
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
    async fetchProducts() {
      const params = new URLSearchParams(this.filters).toString();
      const res = await fetch(`/api/products?${params}`);
      this.products = await res.json();
    },
    async fetchCategories() {
      const res = await fetch('/api/categories');
      this.categories = await res.json();
    },
    async fetchCart() {
      const res = await fetch('/api/cart');
      this.cart = await res.json();
    },
    async addToCart(productId) {
      await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ productId })
      });
      await this.fetchCart();
    },
    async removeFromCart(itemId) {
      await fetch(`/api/cart/${itemId}`, { method: 'DELETE' });
      await this.fetchCart();
    },
    async clearCart() {
      await fetch('/api/cart', { method: 'DELETE' });
      await this.fetchCart();
    }
  },
  async mounted() {
    await Promise.all([this.fetchProducts(), this.fetchCategories(), this.fetchCart()]);
  }
}).mount('#app');
