<template>
  <div class="stock-detail">
    <div class="back-btn" @click="goBack">← 返回列表</div>
    
    <div class="stock-header" v-if="stock">
      <div class="stock-info">
        <h1>{{ stock.name }}</h1>
        <span class="stock-code">{{ stock.code }}</span>
      </div>
      <div class="stock-price-section">
        <span :class="stock.change >= 0 ? 'up' : 'down'" class="price">¥{{ stock.price }}</span>
        <span :class="stock.change >= 0 ? 'up' : 'down'" class="change">
          {{ stock.change >= 0 ? '+' : '' }}{{ stock.change }}%
        </span>
      </div>
    </div>
    
    <div class="stock-metrics" v-if="stock">
      <div class="metric-item">
        <span class="label">开盘价</span>
        <span class="value">{{ stock.open }}</span>
      </div>
      <div class="metric-item">
        <span class="label">最高价</span>
        <span class="value up">{{ stock.high }}</span>
      </div>
      <div class="metric-item">
        <span class="label">最低价</span>
        <span class="value down">{{ stock.low }}</span>
      </div>
      <div class="metric-item">
        <span class="label">成交量</span>
        <span class="value">{{ stock.volume }}</span>
      </div>
      <div class="metric-item">
        <span class="label">成交额</span>
        <span class="value">{{ stock.turnover }}</span>
      </div>
      <div class="metric-item">
        <span class="label">市盈率</span>
        <span class="value">{{ stock.pe }}</span>
      </div>
    </div>
    
    <div class="charts-section">
      <div class="chart-container">
        <h3>K线图</h3>
        <div ref="klineChart" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>MACD指标</h3>
        <div ref="macdChart" class="chart"></div>
      </div>
      
      <div class="chart-container">
        <h3>KDJ指标</h3>
        <div ref="kdjChart" class="chart"></div>
      </div>
    </div>
    
    <div class="analysis-section">
      <h3>📊 综合分析</h3>
      <div class="analysis-card" v-if="analysis">
        <div class="analysis-item">
          <span class="label">综合评分:</span>
          <span :class="getScoreClass(analysisScore)" class="score">{{ analysisScore }}分</span>
        </div>
        <div class="analysis-item">
          <span class="label">评分理由:</span>
          <span class="reason">{{ analysisReason }}</span>
        </div>
        <div class="indicator-analysis">
          <h4>技术指标分析</h4>
          <div class="indicator-item">
            <span class="indicator-label">MACD:</span>
            <span :class="macdSignal" class="indicator-value">{{ macdSignalText }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">KDJ:</span>
            <span :class="kdjSignal" class="indicator-value">{{ kdjSignalText }}</span>
          </div>
          <div class="indicator-item">
            <span class="indicator-label">RSI:</span>
            <span :class="rsiSignal" class="indicator-value">{{ rsiSignalText }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { stockService } from '../services/stockService'
import { stockSelector } from '../utils/stockSelector'
import * as echarts from 'echarts'

const route = useRoute()
const router = useRouter()

const stock = ref(null)
const klineData = ref(null)
const analysis = ref(null)

const klineChart = ref(null)
const macdChart = ref(null)
const kdjChart = ref(null)

const analysisScore = ref(50)
const analysisReason = ref('')

const macdSignal = ref('neutral')
const macdSignalText = ref('')
const kdjSignal = ref('neutral')
const kdjSignalText = ref('')
const rsiSignal = ref('neutral')
const rsiSignalText = ref('')

const goBack = () => {
  router.push('/stocks')
}

const getScoreClass = (score) => {
  if (score >= 80) return 'high'
  if (score >= 70) return 'medium'
  return 'low'
}

const initKlineChart = () => {
  if (!klineChart.value || !klineData.value) return
  
  const chart = echarts.init(klineChart.value)
  const data = klineData.value.data
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    grid: [
      { left: '10%', right: '5%', top: '5%', height: '60%' },
      { left: '10%', right: '5%', top: '72%', height: '20%' }
    ],
    xAxis: [
      { type: 'category', data: data.map(d => d.date), axisLine: { lineStyle: { color: '#ccc' } } },
      { type: 'category', gridIndex: 1, data: data.map(d => d.date), axisLine: { lineStyle: { color: '#ccc' } } }
    ],
    yAxis: [
      { type: 'value', scale: true, splitArea: { show: true } },
      { type: 'value', gridIndex: 1, scale: true }
    ],
    dataZoom: [
      { type: 'inside', xAxisIndex: [0, 1], start: 50, end: 100 },
      { show: true, xAxisIndex: [0, 1], type: 'slider', bottom: '2%', start: 50, end: 100 }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: data.map(d => [d.open, d.close, d.low, d.high]),
        itemStyle: {
          color: '#ef4444',
          color0: '#22c55e',
          borderColor: '#ef4444',
          borderColor0: '#22c55e'
        }
      },
      {
        name: 'MA5',
        type: 'line',
        data: analysis.value?.indicators?.ma5,
        smooth: true,
        lineStyle: { color: '#ef4444', width: 1 }
      },
      {
        name: 'MA10',
        type: 'line',
        data: analysis.value?.indicators?.ma10,
        smooth: true,
        lineStyle: { color: '#f59e0b', width: 1 }
      },
      {
        name: 'VOL',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: data.map(d => d.volume),
        itemStyle: {
          color: (params) => params.data >= data[params.dataIndex - 1]?.volume ? '#ef4444' : '#22c55e'
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => chart.resize())
}

const initMACDChart = () => {
  if (!macdChart.value || !analysis.value) return
  
  const chart = echarts.init(macdChart.value)
  const data = klineData.value.data
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '15%' },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLine: { lineStyle: { color: '#ccc' } } },
    yAxis: { type: 'value', scale: true },
    series: [
      { name: 'DIF', type: 'line', data: analysis.value.indicators.macd.DIF, lineStyle: { color: '#ef4444' } },
      { name: 'DEA', type: 'line', data: analysis.value.indicators.macd.DEA, lineStyle: { color: '#22c55e' } },
      { 
        name: 'MACD', 
        type: 'bar', 
        data: analysis.value.indicators.macd.MACD,
        itemStyle: {
          color: (params) => params.data >= 0 ? '#ef4444' : '#22c55e'
        }
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initKDJChart = () => {
  if (!kdjChart.value || !analysis.value) return
  
  const chart = echarts.init(kdjChart.value)
  const data = klineData.value.data
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '5%', top: '10%', bottom: '15%' },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLine: { lineStyle: { color: '#ccc' } } },
    yAxis: { type: 'value', min: 0, max: 100 },
    series: [
      { name: 'K', type: 'line', data: analysis.value.indicators.kdj.K, lineStyle: { color: '#ef4444' } },
      { name: 'D', type: 'line', data: analysis.value.indicators.kdj.D, lineStyle: { color: '#22c55e' } },
      { name: 'J', type: 'line', data: analysis.value.indicators.kdj.J, lineStyle: { color: '#3b82f6' } }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const analyzeSignals = () => {
  if (!analysis.value) return
  
  const macd = analysis.value.indicators.macd
  const kdj = analysis.value.indicators.kdj
  const rsi = analysis.value.indicators.rsi
  
  const latestDIF = macd.DIF[macd.DIF.length - 1]
  const latestDEA = macd.DEA[macd.DEA.length - 1]
  const latestMACD = macd.MACD[macd.MACD.length - 1]
  
  if (latestDIF && latestDEA && latestMACD) {
    if (latestDIF > latestDEA && latestMACD > 0) {
      macdSignal.value = 'bullish'
      macdSignalText.value = '金叉向上，多头信号'
    } else if (latestDIF > latestDEA) {
      macdSignal.value = 'neutral'
      macdSignalText.value = '即将金叉，关注'
    } else {
      macdSignal.value = 'bearish'
      macdSignalText.value = '死叉向下，空头信号'
    }
  }
  
  const latestK = kdj.K[kdj.K.length - 1]
  const latestD = kdj.D[kdj.D.length - 1]
  
  if (latestK && latestD) {
    if (latestK > latestD && latestK < 70) {
      kdjSignal.value = 'bullish'
      kdjSignalText.value = 'K线上穿D线，买入信号'
    } else if (latestK > 80) {
      kdjSignal.value = 'bearish'
      kdjSignalText.value = '超买区域，警惕回调'
    } else if (latestK < 20) {
      kdjSignal.value = 'bullish'
      kdjSignalText.value = '超卖区域，可能反弹'
    } else {
      kdjSignal.value = 'neutral'
      kdjSignalText.value = '震荡整理中'
    }
  }
  
  const latestRSI = rsi[rsi.length - 1]
  if (latestRSI) {
    if (latestRSI > 70) {
      rsiSignal.value = 'bearish'
      rsiSignalText.value = '超买，可能回调'
    } else if (latestRSI < 30) {
      rsiSignal.value = 'bullish'
      rsiSignalText.value = '超卖，可能反弹'
    } else {
      rsiSignal.value = 'neutral'
      rsiSignalText.value = '正常区间'
    }
  }
}

const loadData = async () => {
  const code = route.params.code
  try {
    stock.value = await stockService.getStockDetail(code)
    klineData.value = await stockService.getKLineData(code)
    analysis.value = stockSelector.analyzeStock(stock.value, klineData.value)
    analysisScore.value = await stockSelector.evaluateStock(stock.value, klineData.value)
    analysisReason.value = stockSelector.getReason(analysisScore.value)
    analyzeSignals()
    
    setTimeout(() => {
      initKlineChart()
      initMACDChart()
      initKDJChart()
    }, 100)
  } catch (error) {
    console.error('加载股票详情失败:', error)
  }
}

onMounted(() => {
  loadData()
})

watch(() => route.params.code, () => {
  loadData()
})
</script>

<style scoped>
.stock-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.back-btn {
  cursor: pointer;
  color: white;
  margin-bottom: 1rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.stock-header {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.stock-info h1 {
  color: #333;
  margin-bottom: 0.5rem;
}

.stock-code {
  color: #9ca3af;
  font-size: 0.9rem;
}

.stock-price-section {
  text-align: right;
}

.price {
  font-size: 2.5rem;
  font-weight: bold;
}

.change {
  font-size: 1.2rem;
  margin-left: 0.5rem;
}

.up {
  color: #ef4444;
}

.down {
  color: #22c55e;
}

.stock-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-item {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 15px;
  padding: 1.5rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.metric-item .label {
  display: block;
  color: #9ca3af;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.metric-item .value {
  font-weight: bold;
  color: #333;
}

.charts-section {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.chart-container {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.chart-container h3 {
  color: #333;
  margin-bottom: 1rem;
}

.chart {
  height: 300px;
}

.analysis-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
}

.analysis-section h3 {
  color: #333;
  margin-bottom: 1rem;
}

.analysis-card {
  padding: 1rem;
}

.analysis-item {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.analysis-item .label {
  color: #6b7280;
}

.analysis-item .score {
  font-size: 1.5rem;
  font-weight: bold;
}

.score.high {
  color: #ef4444;
}

.score.medium {
  color: #f59e0b;
}

.score.low {
  color: #22c55e;
}

.analysis-item .reason {
  color: #333;
  font-weight: 500;
}

.indicator-analysis {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.indicator-analysis h4 {
  color: #6b7280;
  margin-bottom: 1rem;
}

.indicator-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.indicator-label {
  color: #6b7280;
  font-weight: 500;
}

.indicator-value {
  padding: 0.25rem 0.75rem;
  border-radius: 10px;
  font-size: 0.85rem;
}

.indicator-value.bullish {
  background: #dcfce7;
  color: #22c55e;
}

.indicator-value.bearish {
  background: #fee2e2;
  color: #ef4444;
}

.indicator-value.neutral {
  background: #f3f4f6;
  color: #6b7280;
}
</style>