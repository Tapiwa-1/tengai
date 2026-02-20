import { createRouter, createWebHistory } from 'vue-router'
import ProductsPage from '../pages/ProductsPage.vue'
import ProductDetailPage from '../pages/ProductDetailPage.vue'
import AgentImportPage from '../pages/AgentImportPage.vue'
import AgentOffersPage from '../pages/AgentOffersPage.vue'
import CheckoutPage from '../pages/CheckoutPage.vue'
import OrdersPage from '../pages/OrdersPage.vue'
import AdminOffersPage from '../pages/AdminOffersPage.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/products' },
    { path: '/products', component: ProductsPage },
    { path: '/p/:id', component: ProductDetailPage },
    { path: '/agent/import', component: AgentImportPage },
    { path: '/agent/offers', component: AgentOffersPage },
    { path: '/checkout', component: CheckoutPage },
    { path: '/orders', component: OrdersPage },
    { path: '/admin/offers', component: AdminOffersPage }
  ]
})
