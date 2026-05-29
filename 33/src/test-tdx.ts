import { TdxDataParser } from './data/TdxDataParser'
import { SimpleT1Strategy } from './strategy/SimpleT1Strategy'

async function testTdx() {
  console.log('=== 通达信数据测试 ===\n')
  
  const filePath = 'data/tdx/000001.SZ.csv'
  console.log(`加载数据文件: ${filePath}`)
  
  const data = TdxDataParser.parseCSV(filePath)
  console.log(`成功加载 ${data.length} 条数据`)
  
  if (data.length > 0) {
    const first = data[0]
    const last = data[data.length - 1]
    console.log(`时间范围: ${new Date(first.timestamp).toLocaleDateString()} ~ ${new Date(last.timestamp).toLocaleDateString()}`)
    console.log(`价格范围: ${first.close} ~ ${last.close}`)
    console.log('')
    
    const strategy = new SimpleT1Strategy({
      name: 'Test',
      parameters: { profitTarget: 0.015, stopLoss: 0.02 }
    })
    
    console.log('测试策略信号生成...')
    let buyCount = 0
    let sellCount = 0
    
    for (let i = 0; i < data.length; i++) {
      const signal = strategy.generateSignal(data, i)
      if (signal.type === 'buy') buyCount++
      if (signal.type === 'sell') sellCount++
    }
    
    console.log(`生成信号: 买入 ${buyCount} 次, 卖出 ${sellCount} 次`)
    
    if (buyCount > 0) {
      console.log('\n前3个买入信号:')
      let count = 0
      for (let i = 0; i < data.length && count < 3; i++) {
        const signal = strategy.generateSignal(data, i)
        if (signal.type === 'buy') {
          count++
          console.log(`  ${new Date(signal.timestamp).toLocaleDateString()}: ¥${signal.price} - ${signal.reason}`)
        }
      }
    }
  }
  
  console.log('\n✅ 测试完成')
}

testTdx().catch(console.error)
