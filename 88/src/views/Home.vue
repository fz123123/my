<template>
  <div class="home">
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon">⚡</span>
          <span>智能股票分析</span>
        </div>
        <h1>涨停先知</h1>
        <p class="tagline">提前洞察每一次涨停机会</p>
        <p class="description">基于先进的技术分析算法，实时监控市场动态</p>
        <button @click="goToStocks" class="cta-button">
          <span>🚀</span>
          开始分析牛股
        </button>
        <div class="hero-stats">
          <div class="stat-item">
            <span class="stat-value">98%</span>
            <span class="stat-label">技术指标准确率</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">实时</span>
            <span class="stat-label">数据更新</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">24/7</span>
            <span class="stat-label">全天候监控</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="features">
      <div class="feature-card">
        <div class="icon">📈</div>
        <h3>实时行情</h3>
        <p>对接新浪财经API，毫秒级延迟</p>
        <div class="feature-tag">Live Data</div>
      </div>
      <div class="feature-card">
        <div class="icon">📊</div>
        <h3>技术分析</h3>
        <p>MACD、KDJ、RSI等20+指标</p>
        <div class="feature-tag">20+ Indicators</div>
      </div>
      <div class="feature-card">
        <div class="icon">🎯</div>
        <h3>智能选股</h3>
        <p>多维度AI评分筛选牛股</p>
        <div class="feature-tag">AI Powered</div>
      </div>
      <div class="feature-card">
        <div class="icon">⚡</div>
        <h3>涨停预测</h3>
        <p>基于历史数据的涨停概率</p>
        <div class="feature-tag">涨停先知</div>
      </div>
    </div>
    
    <div class="bull-stocks-section">
      <div class="section-header">
        <h2>🔥 今日潜力牛股</h2>
        <p class="section-desc">基于多维度技术指标综合评分，筛选具备上涨潜力的股票</p>
      </div>
      <div class="bull-stocks" v-if="bullStocks.length > 0">
        <div 
          v-for="stock in bullStocks" 
          :key="stock.code" 
          class="bull-stock-card"
          @click="goToStockDetail(stock.code)"
        >
          <div class="stock-header">
            <span class="stock-name">{{ stock.name }}</span>
            <span class="stock-code">{{ stock.code }}</span>
          </div>
          <div class="stock-price">
            <span class="price">¥{{ stock.price }}</span>
            <span :class="stock.change >= 0 ? 'up' : 'down'" class="change">
              {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
            </span>
          </div>
          <div class="stock-score">
            <span class="score-label">评分:</span>
            <span :class="getScoreClass(stock.score)" class="score-value">{{ stock.score }}分</span>
          </div>
          <div class="stock-reason">{{ stock.reason }}</div>
          <div class="stock-tags">
            <span class="tag" :class="stock.change >= 0 ? 'up-tag' : 'down-tag'">
              {{ stock.change >= 0 ? '📈 涨' : '📉 跌' }}
            </span>
          </div>
        </div>
      </div>
      <div v-else class="loading">
        <div class="spinner"></div>
        <p>正在分析市场数据...</p>
      </div>
    </div>
    
    <div class="features-grid">
      <h2>💡 核心功能</h2>
      <div class="features-list">
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div class="feature-content">
            <h4>K线图分析</h4>
            <p>专业的K线图表，实时展示开盘价、收盘价、最高价、最低价</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📈</div>
          <div class="feature-content">
            <h4>均线系统</h4>
            <p>MA5、MA10、MA20、MA60多周期均线，捕捉趋势变化</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🎯</div>
          <div class="feature-content">
            <h4>MACD指标</h4>
            <p>指数平滑异同移动平均线，准确判断买卖信号</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">⚡</div>
          <div class="feature-content">
            <h4>KDJ随机指标</h4>
            <p>超买超卖分析，把握入场和出场时机</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📉</div>
          <div class="feature-content">
            <h4>RSI相对强弱</h4>
            <p>衡量价格变动速度，判断市场热度</p>
          </div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🎨</div>
          <div class="feature-content">
            <h4>BOLL布林带</h4>
            <p>价格波动区间分析，识别支撑位和压力位</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { stockService } from '../services/stockService'
import { stockSelector } from '../utils/stockSelector'
import { useRouter } from 'vue-router'

const router = useRouter()
const bullStocks = ref([])

const goToStocks = () => {
  router.push('/stocks')
}

const goToStockDetail = (code) => {
  router.push(`/stock/${code}`)
}

const getScoreClass = (score) => {
  if (score >= 80) return 'high'
  if (score >= 70) return 'medium'
  return 'low'
}

const loadBullStocks = async () => {
  try {
    const stocks = await stockService.getStockList()
    const klineData = {}
    for (const stock of stocks) {
      try {
        klineData[stock.code] = await stockService.getKLineData(stock.code)
      } catch (e) {
        console.log('获取K线数据失败')
      }
    }
    bullStocks.value = await stockSelector.selectBullStocks(stocks, klineData)
  } catch (error) {
    console.error('加载牛股数据失败:', error)
  }
}

onMounted(() => {
  loadBullStocks()
})
</script>

<style scoped>
.home {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.hero-section {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 30px;
  padding: 4rem;
  text-align: center;
  margin-bottom: 2rem;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 215, 0, 0.1) 0%, transparent 70%);
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%);
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 50px;
  font-size: 0.9rem;
  margin-bottom: 1.5rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.hero-content h1 {
  font-size: 4rem;
  background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 50%, #ffd700 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 1rem;
  letter-spacing: 5px;
  text-shadow: 0 0 40px rgba(255, 215, 0, 0.5);
}

.tagline {
  font-size: 1.5rem;
  color: #ffd700;
  margin-bottom: 0.5rem;
}

.description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 2rem;
}

.cta-button {
  background: linear-gradient(135deg, #ffd700 0%, #ff6b6b 100%);
  color: white;
  border: none;
  padding: 1rem 3rem;
  font-size: 1.1rem;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(255, 215, 0, 0.3);
}

.cta-button:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 40px rgba(255, 215, 0, 0.5);
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 3rem;
  margin-top: 3rem;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #ffd700;
  text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}

.stat-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  text-align: center;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  transform: translateY(-10px);
  border-color: rgba(255, 215, 0, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.feature-card .icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  color: #ffd700;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.feature-tag {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.bull-stocks-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.section-header {
  text-align: center;
  margin-bottom: 2rem;
}

.section-header h2 {
  color: #ffd700;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.section-desc {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.bull-stocks {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.bull-stock-card {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 107, 107, 0.1) 100%);
  border: 1px solid rgba(255, 215, 0, 0.2);
  border-radius: 20px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.bull-stock-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(255, 215, 0, 0.2);
  border-color: #ffd700;
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.stock-name {
  font-weight: bold;
  color: #fff;
  font-size: 1.2rem;
}

.stock-code {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
}

.stock-price {
  margin-bottom: 1rem;
}

.stock-price .price {
  font-size: 1.8rem;
  font-weight: bold;
  color: #fff;
}

.stock-price .change {
  margin-left: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
}

.stock-price .up {
  color: #ff4444;
}

.stock-price .down {
  color: #00ff00;
}

.stock-score {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;
}

.score-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
}

.score-value {
  margin-left: 0.5rem;
  font-weight: bold;
  font-size: 1.1rem;
}

.score-value.high {
  color: #ff4444;
}

.score-value.medium {
  color: #ff9900;
}

.score-value.low {
  color: #00ff00;
}

.stock-reason {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.stock-tags {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tag {
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}

.up-tag {
  background: rgba(255, 68, 68, 0.2);
  color: #ff4444;
}

.down-tag {
  background: rgba(0, 255, 0, 0.2);
  color: #00ff00;
}

.loading {
  text-align: center;
  padding: 3rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 215, 0, 0.2);
  border-top: 4px solid #ffd700;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.features-grid {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
}

.features-grid h2 {
  color: #ffd700;
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  transition: all 0.3s;
}

.feature-item:hover {
  background: rgba(255, 215, 0, 0.1);
  border-color: rgba(255, 215, 0, 0.3);
}

.feature-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.feature-content h4 {
  color: #ffd700;
  margin-bottom: 0.5rem;
}

.feature-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .home {
    padding: 1rem;
  }
  
  .hero-section {
    padding: 2rem;
  }
  
  .hero-content h1 {
    font-size: 2.5rem;
  }
  
  .hero-stats {
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .features-list {
    grid-template-columns: 1fr;
  }
}
</style>
