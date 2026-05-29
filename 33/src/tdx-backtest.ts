import * as path from 'path'
import { TdxDataParser } from './data/TdxDataParser'
import { T1Strategy, T1GapUpStrategy } from './strategy/IntradayStrategy'
import { SimpleT1Strategy } from './strategy/SimpleT1Strategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { Logger } from './utils/Logger'
import { BarData } from './types'

async function runTdxBacktest(filePath: string) {
  Logger.info('=== 通达信数据回测 ===\n')

  if (!filePath) {
    console.error('❌ 请指定通达信数据文件路径')
    console.log('用法: npx ts-node src/tdx-backtest.ts <数据文件路径>')
    process.exit(1)
  }

  console.log(`📁 正在加载数据文件: ${filePath}`)
  
  let data: BarData[]
  const ext = path.extname(filePath).toLowerCase()
  
  try {
    if (ext === '.csv') {
      data = TdxDataParser.parseCSV(filePath)
    } else if (ext === '.txt') {
      data = TdxDataParser.parseTXT(filePath)
    } else {
      console.error(`❌ 不支持的文件格式: ${ext}`)
      process.exit(1)
    }
  } catch (error) {
    console.error('❌ 加载数据文件失败:', error)
    process.exit(1)
  }

  if (data.length === 0) {
    console.error('❌ 未解析到任何数据')
    process.exit(1)
  }

  const symbol = path.basename(filePath, ext).toUpperCase()
  const startDate = new Date(data[0].timestamp).toLocaleDateString('zh-CN')
  const endDate = new Date(data[data.length - 1].timestamp).toLocaleDateString('zh-CN')

  console.log(`✅ 成功加载 ${data.length} 条数据`)
  console.log(`📅 数据时间范围: ${startDate} ~ ${endDate}`)
  console.log('')

  const strategies = [
    new SimpleT1Strategy({
      name: 'SimpleT1',
      parameters: {
        profitTarget: 0.015,
        stopLoss: 0.02
      }
    }),
    new T1Strategy({
      name: 'T1_Main',
      parameters: {
        buyTime: 1450,
        sellTime: 1030,
        minVolume: 1000000,
        profitTarget: 0.015,
        stopLoss: 0.02
      }
    })
  ]

  const riskManager = new RiskManager({
    maxPositionSize: 0.2,
    maxDrawdown: 0.15,
    stopLoss: 0.02,
    takeProfit: 0.03,
    maxOpenPositions: 1
  })

  const transactionCost = {
    commissionRate: 0.0003,
    slippage: 0.0005,
    impactCost: 0.0003,
    minCommission: 5
  }

  console.log('='.repeat(70))
  console.log(`T+1 超短线策略回测报告 - ${symbol}`)
  console.log('='.repeat(70))
  console.log('交易成本参数:')
  console.log(`  - 佣金率: ${(transactionCost.commissionRate * 100).toFixed(3)}%`)
  console.log(`  - 滑点: ${(transactionCost.slippage * 100).toFixed(3)}%`)
  console.log(`  - 冲击成本: ${(transactionCost.impactCost * 100).toFixed(3)}%`)
  console.log(`  - 最低佣金: ¥${transactionCost.minCommission}`)
  console.log('='.repeat(70) + '\n')

  for (const strategy of strategies) {
    Logger.info(`Testing ${strategy.getName()}...`)
    
    const backtester = new Backtester(strategy, riskManager, 100000, transactionCost)
    const result = backtester.run(data)
    const trades = backtester.getTrades()
    
    const buySignals = trades.filter(t => t.type === 'buy').length
    const sellSignals = trades.filter(t => t.type === 'sell').length

    console.log(`\n【策略】${strategy.getName()}`)
    console.log(''.padEnd(50, '-'))
    console.log(`日期范围: ${result.startDate} ~ ${result.endDate}`)
    console.log(`初始资金: ¥${result.initialCapital.toLocaleString()}`)
    console.log(`最终资金: ¥${result.finalCapital.toLocaleString()}`)
    console.log(''.padEnd(50, '-'))
    console.log(`【收益指标】`)
    console.log(`  总收益率: ${result.totalReturnPercent >= 0 ? '+' : ''}${result.totalReturnPercent.toFixed(2)}% (¥${result.totalReturn.toLocaleString()})`)
    console.log(`  年化收益率: ${result.annualizedReturn >= 0 ? '+' : ''}${result.annualizedReturn.toFixed(2)}%`)
    console.log(`  夏普比率: ${result.sharpeRatio.toFixed(2)}`)
    console.log(''.padEnd(50, '-'))
    console.log(`【风控指标】`)
    console.log(`  最大回撤: ${result.maxDrawdown.toFixed(2)}%`)
    console.log(''.padEnd(50, '-'))
    console.log(`【交易统计】`)
    console.log(`  交易次数: ${result.trades} (买入: ${buySignals}, 卖出: ${sellSignals})`)
    console.log(`  胜率: ${result.winRate.toFixed(2)}%`)
    console.log(`  盈亏比: ${result.profitFactor.toFixed(2)}`)
    console.log(''.padEnd(50, '-'))
    
    if (trades.length > 0) {
      console.log(`【最近5笔交易】`)
      const recentTrades = trades.slice(-5).reverse()
      for (const trade of recentTrades) {
        const date = new Date(trade.timestamp).toLocaleDateString('zh-CN')
        console.log(`  ${trade.type === 'buy' ? '[买入]' : '[卖出]'} ${date} ¥${trade.price.toFixed(2)} x ${trade.quantity || 1} - ${trade.reason}`)
      }
    }
    
    console.log('')
  }

  console.log('='.repeat(70))
  Logger.info('通达信数据回测完成')
}

const filePath = process.argv[2]
runTdxBacktest(filePath).catch(error => {
  Logger.error('Error running TDX backtest', error)
  process.exit(1)
})
