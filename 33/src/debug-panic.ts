import * as path from 'path'
import { TdxDataParser } from './data/TdxDataParser'
import { Indicator } from './strategy/Indicator'

console.log('='.repeat(80))
console.log('🔍 恐慌数据调试')
console.log('='.repeat(80))

const dataPath = path.join(__dirname, '../data/tdx/test_panic_data.csv')
const data = TdxDataParser.parseCSV(dataPath)

console.log(`\n📊 数据加载: ${data.length} 条`)

console.log('\n' + '='.repeat(80))
console.log('📈 查找大跌日:')
console.log('='.repeat(80))

const rsi14 = Indicator.RSI(data, 14)

for (let i = 30; i < data.length; i++) {
  const bar = data[i]
  const prevBar = data[i - 1]
  
  const drop = (bar.close - prevBar.close) / prevBar.close
  const intradayDrop = (bar.close - bar.open) / bar.open
  const lowDrop = (bar.low - prevBar.close) / prevBar.close
  
  const maxDrop = Math.min(drop, intradayDrop, lowDrop)
  
  if (maxDrop <= -0.02) {
    const date = new Date(bar.timestamp).toLocaleDateString('zh-CN')
    const avgVol = data.slice(Math.max(0, i - 20), i + 1).reduce((sum, b) => sum + b.volume, 0) / 21
    const volRatio = bar.volume / avgVol
    const rsi = rsi14[i] || 50
    
    console.log(`\n📅 ${date}:`)
    console.log(`   收盘价: ${prevBar.close.toFixed(2)} -> ${bar.close.toFixed(2)}`)
    console.log(`   日跌幅: ${(drop * 100).toFixed(2)}%`)
    console.log(`   日内最大跌幅: ${(maxDrop * 100).toFixed(2)}%`)
    console.log(`   成交量: ${bar.volume} (平均: ${Math.round(avgVol)}, 量比: ${volRatio.toFixed(2)})`)
    console.log(`   RSI: ${rsi.toFixed(2)}`)
    console.log(`   K线: 开${bar.open.toFixed(2)} 高${bar.high.toFixed(2)} 低${bar.low.toFixed(2)} 收${bar.close.toFixed(2)}`)
  }
}

console.log('\n' + '='.repeat(80))
console.log('✅ 调试完成')
console.log('='.repeat(80))
