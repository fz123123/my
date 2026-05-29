import * as path from 'path'
import * as fs from 'fs'
import * as XLSX from 'xlsx'
import { TdxDataParser } from './data/TdxDataParser'
import { SimpleT1Strategy } from './strategy/SimpleT1Strategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { BarData } from './types'

interface StockAnalysis {
  symbol: string
  name: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  change: number
  changePercent: string
  signal: string
  signalReason: string
  hasHistory: boolean
  historyReturn?: string
  historyWinRate?: string
  historyTrades?: number
}

const stockNames: Record<string, string> = {
  '000001.SZ': '平安银行',
  '000002.SZ': '万科A',
  '600519.SH': '贵州茅台',
  '000858.SZ': '五粮液',
  '601318.SH': '中国平安',
  '300750.SZ': '宁德时代',
  '002594.SZ': '比亚迪',
  '601012.SH': '隆基绿能',
  '002475.SZ': '立讯精密',
  '603501.SH': '韦尔股份',
  '000725.SZ': '京东方A',
  '300059.SZ': '东方财富',
  '000333.SZ': '美的集团',
  '600036.SH': '招商银行'
}

async function exportToExcel() {
  console.log('📊 正在生成回测报告...')

  const tdxDir = 'data/tdx/'
  const todayDataFile = path.join(tdxDir, 'today_data.csv')

  if (!fs.existsSync(todayDataFile)) {
    console.error('❌ 今日数据文件不存在: data/tdx/today_data.csv')
    process.exit(1)
  }

  const todayContent = fs.readFileSync(todayDataFile, 'utf-8')
  const lines = todayContent.split('\n').filter(line => line.trim())
  
  const analyses: StockAnalysis[] = []
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

      const open = parseFloat(parts[2].trim())
      const close = parseFloat(parts[5].trim())
      const changePercent = ((close - open) / open * 100).toFixed(2)

      const analysis: StockAnalysis = {
        symbol,
        name: stockNames[symbol] || symbol,
        date: new Date(timestamp).toLocaleDateString('zh-CN'),
        open,
        high: parseFloat(parts[3].trim()),
        low: parseFloat(parts[4].trim()),
        close,
        volume: parseInt(parts[6].trim()) || 0,
        change: close - open,
        changePercent: `${parseFloat(changePercent) >= 0 ? '+' : ''}${changePercent}%`,
        signal: '持有',
        signalReason: '',
        hasHistory: false
      }

      const historyFile = path.join(tdxDir, `${symbol}.csv`)
      let allData: BarData[] = []

      if (fs.existsSync(historyFile)) {
        const historyData = TdxDataParser.parseCSV(historyFile)
        allData = [...historyData, {
          timestamp,
          open,
          high: analysis.high,
          low: analysis.low,
          close,
          volume: analysis.volume
        }]
        analysis.hasHistory = true
      } else {
        allData = [{
          timestamp,
          open,
          high: analysis.high,
          low: analysis.low,
          close,
          volume: analysis.volume
        }]
      }

      if (allData.length >= 5) {
        const strategy = new SimpleT1Strategy({
          name: 'LiveT1',
          parameters: { profitTarget: 0.015, stopLoss: 0.02 }
        })

        const lastIndex = allData.length - 1
        const signal = strategy.generateSignal(allData, lastIndex)

        if (signal.type === 'buy') {
          analysis.signal = '买入'
          analysis.signalReason = signal.reason || '符合T+1策略条件'
        }

        if (allData.length >= 30 && analysis.hasHistory) {
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

          const backtester = new Backtester(strategy, riskManager, 100000, transactionCost)
          const result = backtester.run(allData.slice(0, -1))

          analysis.historyReturn = `${result.totalReturnPercent >= 0 ? '+' : ''}${result.totalReturnPercent.toFixed(2)}%`
          analysis.historyWinRate = `${result.winRate.toFixed(1)}%`
          analysis.historyTrades = result.trades
        }
      }

      analyses.push(analysis)
    }
  }

  const exportData = analyses.map(a => ({
    '股票代码': a.symbol,
    '股票名称': a.name,
    '日期': a.date,
    '开盘价': a.open.toFixed(2),
    '最高价': a.high.toFixed(2),
    '最低价': a.low.toFixed(2),
    '收盘价': a.close.toFixed(2),
    '涨跌额': a.change.toFixed(2),
    '涨跌幅': a.changePercent,
    '成交量(万)': (a.volume / 10000).toFixed(0),
    '交易信号': a.signal,
    '信号理由': a.signalReason,
    '历史回测收益': a.historyReturn || '-',
    '历史胜率': a.historyWinRate || '-',
    '历史交易次数': a.historyTrades || '-'
  }))

  const workbook = XLSX.utils.book_new()
  const worksheet = XLSX.utils.json_to_sheet(exportData)

  worksheet['!cols'] = [
    { wch: 12 },
    { wch: 12 },
    { wch: 12 },
    { wch: 10 },
    { wch: 10 },
    { wch: 10 },
    { wch: 10 },
    { wch: 10 },
    { wch: 10 },
    { wch: 12 },
    { wch: 10 },
    { wch: 20 },
    { wch: 14 },
    { wch: 10 },
    { wch: 14 }
  ]

  XLSX.utils.book_append_sheet(workbook, worksheet, '回测结果')

  const now = new Date()
  const fileName = `回测报告_${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}.xlsx`
  const filePath = path.join('data', 'reports', fileName)

  if (!fs.existsSync('data/reports')) {
    fs.mkdirSync('data/reports', { recursive: true })
  }

  XLSX.writeFile(workbook, filePath)

  console.log('✅ Excel文件已生成!')
  console.log(`📁 文件路径: ${filePath}`)
  console.log(`📊 共导出 ${analyses.length} 只股票数据`)

  const buySignals = analyses.filter(a => a.signal === '买入').length
  console.log(`🚀 买入信号: ${buySignals} 个`)
}

exportToExcel().catch(error => {
  console.error('❌ 导出失败:', error)
  process.exit(1)
})
