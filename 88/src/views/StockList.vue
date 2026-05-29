<template>
  <div class="stock-list">
    <div class="search-bar">
      <input 
        v-model="searchText" 
        type="text" 
        placeholder="搜索股票名称或代码..."
        class="search-input"
      />
      <button @click="refreshStocks" class="refresh-btn">🔄 刷新</button>
    </div>
    
    <div class="filter-bar">
      <button 
        v-for="filter in filters" 
        :key="filter.value"
        :class="['filter-btn', { active: currentFilter === filter.value }]"
        @click="currentFilter = filter.value"
      >
        {{ filter.label }}
      </button>
    </div>
    
    <div class="stock-table-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th>股票名称</th>
            <th>代码</th>
            <th>最新价</th>
            <th>涨跌幅</th>
            <th>成交量</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="stock in filteredStocks" 
            :key="stock.code"
            class="stock-row"
          >
            <td class="stock-name">{{ stock.name }}</td>
            <td class="stock-code">{{ stock.code }}</td>
            <td :class="stock.change >= 0 ? 'up' : 'down'">{{ stock.price }}</td>
            <td :class="stock.change >= 0 ? 'up' : 'down'">
              {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
            </td>
            <td>{{ stock.volume }}</td>
            <td>
              <button @click="viewDetail(stock.code)" class="detail-btn">查看详情</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { stockService } from '../services/stockService'
import { useRouter } from 'vue-router'

const router = useRouter()
const stocks = ref([])
const searchText = ref('')
const currentFilter = ref('all')

const filters = [
  { label: '全部', value: 'all' },
  { label: '上涨', value: 'up' },
  { label: '下跌', value: 'down' }
]

const filteredStocks = computed(() => {
  let result = stocks.value
  
  if (currentFilter.value === 'up') {
    result = result.filter(s => s.change >= 0)
  } else if (currentFilter.value === 'down') {
    result = result.filter(s => s.change < 0)
  }
  
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(s => 
      s.name.toLowerCase().includes(search) || 
      s.code.includes(search)
    )
  }
  
  return result
})

const viewDetail = (code) => {
  router.push(`/stock/${code}`)
}

const refreshStocks = async () => {
  await loadStocks()
}

const loadStocks = async () => {
  try {
    stocks.value = await stockService.getStockList()
  } catch (error) {
    console.error('加载股票列表失败:', error)
  }
}

onMounted(() => {
  loadStocks()
})
</script>

<style scoped>
.stock-list {
  max-width: 1000px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #667eea;
}

.refresh-btn {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: transform 0.3s;
}

.refresh-btn:hover {
  transform: translateY(-2px);
}

.filter-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.filter-btn {
  padding: 0.5rem 1.5rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  border-color: #667eea;
}

.filter-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

.stock-table-container {
  overflow-x: auto;
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th {
  padding: 1rem;
  text-align: left;
  background: #f9fafb;
  color: #6b7280;
  font-weight: 600;
}

.stock-table td {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.stock-row:hover {
  background: #f9fafb;
}

.stock-name {
  font-weight: 600;
  color: #333;
}

.stock-code {
  color: #9ca3af;
  font-size: 0.9rem;
}

.stock-table .up {
  color: #ef4444;
}

.stock-table .down {
  color: #22c55e;
}

.detail-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: transform 0.3s;
}

.detail-btn:hover {
  transform: translateY(-2px);
}
</style>