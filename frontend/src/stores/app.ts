import { defineStore } from 'pinia'
import api from '../services/api'

export const useAppStore = defineStore('app', {
  state: () => ({ products: [] as any[], product: null as any, orders: [] as any[], importHistory: [] as any[] }),
  actions: {
    async searchProducts(query = '') {
      const { data } = await api.get('/products', { params: { query } })
      this.products = data.items
    },
    async getProduct(id: string) {
      const { data } = await api.get(`/products/${id}`)
      this.product = data
    },
    async getOrders() {
      const { data } = await api.get('/orders')
      this.orders = data.items
    },
    async getImportHistory(token: string) {
      const { data } = await api.get('/agent/imports', { headers: { Authorization: `Bearer ${token}` } })
      this.importHistory = data.items
    }
  }
})
