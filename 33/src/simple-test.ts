import * as path from 'path'
import { TdxDataParser } from './data/TdxDataParser'
import { PanicBuyStrategy } from './strategy/PanicBuyStrategy'
import { StrategyConfig } from './types'

console.log('='.repeat(80))
console.log('🧪 简单策略测试')
console.log('='.repeat(80))

const dataPath = path.join(__dirname, '../data/tdx/test_panic_data.csv')
const data = TdxDataParser.parseCSV(dataPath)

console.log(`\n📊 加载数据: ${data.length} 条`)

const config: StrategyConfig = {
  name: '测试策略',
  parameters: {
    minDrop: 0.04,
    volumeRatio: 1.3,
    rsiOversold: 35,
    profitTarget: 0.06,
    stopLoss: 0.04
  }
}

const strategy = new PanicBuyStrategy(config)

console.log('\n' + '='.repeat(80))
console.log('📈 查找买入信号:')
console.log('='.repeat(80))

let buyCount = 0

for (let i = 30; i < data.length; i++) {
  const signal = strategy.generateSignal(data, i)
  
  if (signal.type === 'buy') {
    buyCount++
    const date = new Date(data[i].timestamp).toLocaleDateString('zh-CN')
    console.log(`✅ ${date}: ${signal.reason}`)
  }
}

console.log(`\n📊 总买入信号: ${buyCount} 个`)

console.log('\n' + '='.repeat(80))
console.log('✅ 测试完成')
console.log('='.repeat(80))
