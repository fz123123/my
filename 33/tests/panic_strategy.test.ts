#!/usr/bin/env ts-node
import { PanicBuyStrategy } from '../src/strategy/PanicBuyStrategy'
import { Backtester } from '../src/backtest/Backtester'
import { RiskManager } from '../src/risk/RiskManager'
import { BarData } from '../src/types'

function createTestData(count: number): BarData[] {
  const data: BarData[] = []
  let price = 50
  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 4
    const open = price
    const close = price + change
    const high = Math.max(open, close) + Math.random() * 2
    const low = Math.min(open, close) - Math.random() * 2
    
    data.push({
      timestamp: new Date(2024, 0, 1 + i).getTime(),
      open,
      high,
      low,
      close,
      volume: Math.floor(Math.random() * 1000000) + 100000
    })
    price = close
  }
  return data
}

function testPanicStrategy() {
  console.log('🧪 开始测试恐慌盘策略...')
  
  // 测试1: 策略初始化
  console.log('\n1. 测试策略初始化')
  const strategy = new PanicBuyStrategy({
    name: 'TestPanicBuy',
    parameters: {
      minDrop: 0.05,
      volumeRatio: 1.5,
      rsiOversold: 30,
      profitTarget: 0.08,
      stopLoss: 0.06
    }
  })
  console.log('✅ 策略初始化成功')
  
  // 测试2: 风险管理初始化
  console.log('\n2. 测试风险管理初始化')
  const riskManager = new RiskManager({
    maxPositionSize: 0.95,
    maxDrawdown: 0.5,
    stopLoss: 0.06,
    takeProfit: 0.08,
    maxOpenPositions: 1
  })
  console.log('✅ 风险管理初始化成功')
  
  // 测试3: 回测器初始化
  console.log('\n3. 测试回测器初始化')
  const backtester = new Backtester(strategy, riskManager, 100000)
  console.log('✅ 回测器初始化成功')
  
  // 测试4: 运行回测
  console.log('\n4. 测试回测运行')
  const testData = createTestData(100)
  const result = backtester.run(testData)
  
  console.log(`   初始资金: $100,000`)
  console.log(`   最终资金: $${result.finalCapital.toLocaleString()}`)
  console.log(`   总收益率: ${result.totalReturnPercent.toFixed(2)}%`)
  console.log(`   最大回撤: ${result.maxDrawdown.toFixed(2)}%`)
  console.log(`   夏普比率: ${result.sharpeRatio.toFixed(2)}`)
  
  assert(result.finalCapital >= 0, '最终资金不能为负')
  assert(result.maxDrawdown >= 0, '最大回撤不能为负')
  console.log('✅ 回测运行成功')
  
  // 测试5: 获取交易记录
  console.log('\n5. 测试交易记录获取')
  const trades = backtester.getTrades()
  console.log(`   交易次数: ${trades.length}`)
  assert(Array.isArray(trades), '交易记录应为数组')
  console.log('✅ 交易记录获取成功')
  
  console.log('\n🎉 所有恐慌盘策略单元测试通过！')
}

function assert(condition: boolean, message: string) {
  if (!condition) {
    throw new Error(`测试失败: ${message}`)
  }
}

testPanicStrategy()
