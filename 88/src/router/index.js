import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import StockList from '../views/StockList.vue'
import StockDetail from '../views/StockDetail.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/stocks', name: 'StockList', component: StockList },
  { path: '/stock/:code', name: 'StockDetail', component: StockDetail }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router