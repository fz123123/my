import * as path from 'path'
import * as fs from 'fs'
import { TdxDataParser } from './data/TdxDataParser'
import { SimpleT1Strategy } from './strategy/SimpleT1Strategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { Logger } from './utils/Logger'
import { BarData } from './types'

async function runLiveBacktest() {
  Logger.info('=== 通达信今日数据回测 ===\n')

  const tdxDir = 'data/tdx/'
  const todayDataFile = path.join(tdxDir, 'today_data.csv')

  if (!fs.existsSync(todayDataFile)) {
    console.log('📋 请先准备今日收盘数据文件: data/tdx/today_data.csv')
    console.log('')
    console.log('格式示例:')
    console.log('股票代码,日期,开盘,最高,最低,收盘,成交量')
    console.log('000001.SZ,2024-03-31,19.10,19.28,19.02,19.22,70000000')
    console.log('600519.SH,2024-03-31,1680.00,1720.00,1650.00,1700.00,5200000')
    console.log('')
    process.exit(0)
  }

  console.log('📁 正在加载今日数据...')
  const todayContent = fs.readFileSync(todayDataFile, 'utf-8')
  const lines = todayContent.split('\n').filter(line => line.trim())
  
  const todayData: Record<string, BarData> = {}
  let hasHeader = false
  
  for (const line of lines) {
    if (!hasHeader) {
      if (line.includes('股票代码') || line.includes('代码')) {
        hasHeader = true
        continue
      }
    }
    
    const parts = line.split(/[,;\s\t]+/).filter(p => p.trim())
    if (parts.length >= 7) {
      const symbol = parts[0].trim()
      const dateStr = parts[1].trim()
      
      let timestamp: number
      if (dateStr.includes('-')) {
        timestamp = new Date(dateStr).getTime()
      } else if (/^\d{8}$/.test(dateStr)) {
        const year = parseInt(dateStr.substring(0, 4))
        const month = parseInt(dateStr.substring(4, 6)) - 1
        const day = parseInt(dateStr.substring(6, 8))
        timestamp = new Date(year, month, day).getTime()
      } else {
        timestamp = new Date(dateStr).getTime()
      }
      
      todayData[symbol] = {
        timestamp,
        open: parseFloat(parts[2].trim()),
        high: parseFloat(parts[3].trim()),
        low: parseFloat(parts[4].trim()),
        close: parseFloat(parts[5].trim()),
        volume: parseInt(parts[6].trim()) || 0
      }
    }
  }

  console.log(`✅ 成功加载 ${Object.keys(todayData).length} 只股票的今日数据`)
  console.log('')

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

  console.log('📊 今日选股结果:')
  console.log('='.repeat(70))

  let totalStocks = 0
  let buySignals = 0

  for (const [symbol, todayBar] of Object.entries(todayData)) {
    const historyFile = path.join(tdxDir, `${symbol}.csv`)
    
    let allData: BarData[] = []
    
    if (fs.existsSync(historyFile)) {
      const historyData = TdxDataParser.parseCSV(historyFile)
      allData = [...historyData, todayBar]
    } else {
      allData = [todayBar]
    }

    if (allData.length < 5) {
      continue
    }

    totalStocks++
    const strategy = new SimpleT1Strategy({
      name: 'LiveT1',
      parameters: { profitTarget: 0.015, stopLoss: 0.02 }
    })

    const lastIndex = allData.length - 1
    const signal = strategy.generateSignal(allData, lastIndex)

    if (signal.type === 'buy') {
      buySignals++
      
      const date = new Date(todayBar.timestamp).toLocaleDateString('zh-CN')
      const change = ((todayBar.close - todayBar.open) / todayBar.open * 100).toFixed(2)
      
      console.log(`\n【买入信号】${symbol}`)
      console.log(`├── 日期: ${date}`)
      console.log(`├── 收盘价: ¥${todayBar.close.toFixed(2)}`)
      console.log(`├── 涨跌幅: ${change}%`)
      console.log(`├── 成交量: ${(todayBar.volume / 10000).toFixed(0)}万`)
      console.log(`└── 理由: ${signal.reason}`)

      if (allData.length >= 30) {
        const backtester = new Backtester(strategy, riskManager, 100000, transactionCost)
        const result = backtester.run(allData.slice(0, -1))
        
        if (result.trades > 0) {
          console.log(`   └── 历史回测: 收益率 ${result.totalReturnPercent.toFixed(2)}%, 胜率 ${result.winRate.toFixed(1)}%`)
        }
      }
    }
  }

  console.log('='.repeat(70))
  console.log(`\n📈 扫描完成: 共 ${totalStocks} 只股票, 发出 ${buySignals} 个买入信号`)
  
  if (buySignals === 0) {
    console.log('\n💡 今日没有符合条件的买入信号')
  }

  Logger.info('今日数据回测完成')
}

runLiveBacktest().catch(error => {
  Logger.error('Error running live backtest', error)
  process.exit(1)
})
