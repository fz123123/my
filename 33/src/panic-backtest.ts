#!/usr/bin/env ts-node
import { PanicBuyStrategy } from './strategy/PanicBuyStrategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { TdxDataParser } from './data/TdxDataParser'
import { BarData } from './types'
import * as path from 'path'

async function testPanicStrategy() {
  console.log('='.repeat(80))
  console.log('🦅 恐慌盘低吸策略回测系统')
  console.log('='.repeat(80))
  
  const dataPath = path.join(__dirname, '../data/tdx/test_panic_data.csv')
  console.log(`\n📊 加载数据: ${dataPath}`)
  
  const data = TdxDataParser.parseCSV(dataPath)
  console.log(`✅ 加载 ${data.length} 条数据`)
  
  if (data.length === 0) {
    console.log('❌ 无数据，退出')
    return
  }
  
  const startDate = new Date(data[0].timestamp).toLocaleDateString('zh-CN')
  const endDate = new Date(data[data.length - 1].timestamp).toLocaleDateString('zh-CN')
  console.log(`📅 时间范围: ${startDate} - ${endDate}`)
  
  const configs = [
    { name: '保守型', minDrop: 0.05, volumeRatio: 1.5, rsiOversold: 32, profitTarget: 0.08, stopLoss: 0.06 },
    { name: '稳健型', minDrop: 0.04, volumeRatio: 1.3, rsiOversold: 35, profitTarget: 0.08, stopLoss: 0.06 },
    { name: '激进型', minDrop: 0.03, volumeRatio: 1.2, rsiOversold: 38, profitTarget: 0.08, stopLoss: 0.06 }
  ]
  
  console.log('\n📋 测试配置:')
  console.log(configs.map((c, i) => `  ${i + 1}. ${c.name}: 跌幅>=${(c.minDrop*100).toFixed(1)}%, 放量>=${c.volumeRatio}x, RSI<=${c.rsiOversold}`).join('\n'))
  
  const results: any[] = []
  
  for (const config of configs) {
    console.log(`\n\n${'='.repeat(80)}`)
    console.log(`🚀 开始回测 ${config.name} 策略`)
    console.log('='.repeat(80))
    
    const strategy = new PanicBuyStrategy({
      name: 'PanicBuy',
      parameters: config
    })
    
    const riskManager = new RiskManager({
      maxPositionSize: 0.95,
      maxDrawdown: 0.5,
      stopLoss: config.stopLoss,
      takeProfit: config.profitTarget,
      maxOpenPositions: 1
    })
    
    const backtester = new Backtester(strategy, riskManager, 100000)
    const result = backtester.run(data)
    const trades = backtester.getTrades()
    
    results.push({
      name: config.name,
      config,
      result,
      trades
    })
    
    printResult(config.name, result, trades)
  }
  
  console.log('\n\n' + '='.repeat(80))
  console.log('📊 策略对比汇总')
  console.log('='.repeat(80))
  
  console.log('\n' + ''.padEnd(12) + '收益率'.padEnd(12) + '最大回撤'.padEnd(12) + '夏普比率'.padEnd(12) + '胜率'.padEnd(10) + '交易次数'.padEnd(10))
  console.log('-'.repeat(70))
  
  for (const r of results) {
    const res = r.result
    console.log(
      r.name.padEnd(12) +
      `${res.totalReturnPercent.toFixed(2)}%`.padEnd(12) +
      `${res.maxDrawdown.toFixed(2)}%`.padEnd(12) +
      `${res.sharpeRatio.toFixed(2)}`.padEnd(12) +
      `${res.winRate.toFixed(2)}%`.padEnd(10) +
      `${res.trades}`.padEnd(10)
    )
  }
  
  const best = results.sort((a, b) => b.result.sharpeRatio - a.result.sharpeRatio)[0]
  console.log(`\n🏆 最佳策略: ${best.name} (夏普比率 ${best.result.sharpeRatio.toFixed(2)})`)
}

function printResult(name: string, result: any, trades: any[]) {
  console.log('\n📈 回测结果:')
  console.log(`  策略名称: ${name}`)
  console.log(`  初始资金: $100,000`)
  console.log(`  最终资金: $${result.finalCapital.toLocaleString()}`)
  console.log(`  总收益率: ${result.totalReturnPercent.toFixed(2)}%`)
  console.log(`  年化收益: ${result.annualizedReturn.toFixed(2)}%`)
  console.log(`  最大回撤: ${result.maxDrawdown.toFixed(2)}%`)
  console.log(`  夏普比率: ${result.sharpeRatio.toFixed(2)}`)
  console.log(`  胜率: ${result.winRate.toFixed(2)}%`)
  console.log(`  交易次数: ${trades.length}`)
  console.log(`  盈利因子: ${result.profitFactor.toFixed(2)}`)
  
  if (trades.length > 0) {
    console.log('\n📝 交易明细:')
    for (let i = 0; i < trades.length; i++) {
      const trade = trades[i]
      const date = new Date(trade.timestamp).toLocaleDateString('zh-CN')
      const type = trade.type === 'buy' ? '📈 买入' : '📉 卖出'
      console.log(`  ${i + 1}. ${date} ${type} @ $${trade.price.toFixed(2)} - ${trade.reason}`)
    }
  }
}

testPanicStrategy().catch(console.error)
