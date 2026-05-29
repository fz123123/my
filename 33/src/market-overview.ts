#!/usr/bin/env ts-node
import * as fs from 'fs'
import * as path from 'path'

interface StockData {
  symbol: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  change: number
  changePercent: number
}

function parseTodayData(filePath: string): StockData[] {
  const content = fs.readFileSync(filePath, 'utf-8')
  const lines = content.split('\n').filter(line => line.trim())
  
  const stocks: StockData[] = []
  let headerSkipped = false
  
  for (const line of lines) {
    if (!headerSkipped) {
      if (line.includes('股票代码') || line.includes('symbol')) {
        headerSkipped = true
        continue
      }
    }
    
    const parts = line.split(/[,;\s\t]+/).filter(p => p.trim())
    
    if (parts.length >= 7) {
      const open = parseFloat(parts[2].trim())
      const close = parseFloat(parts[5].trim())
      const change = close - open
      const changePercent = (change / open) * 100
      
      stocks.push({
        symbol: parts[0].trim(),
        date: parts[1].trim(),
        open,
        high: parseFloat(parts[3].trim()),
        low: parseFloat(parts[4].trim()),
        close,
        volume: parseInt(parts[6].trim()) || 0,
        change,
        changePercent
      })
    }
  }
  
  return stocks
}

function main() {
  console.log('='.repeat(80))
  console.log('📊 今日市场概况')
  console.log('='.repeat(80))
  
  const dataPath = path.join(__dirname, '../data/tdx/today_data.csv')
  
  if (!fs.existsSync(dataPath)) {
    console.log('❌ 未找到今日数据文件！')
    return
  }
  
  const stocks = parseTodayData(dataPath)
  
  if (stocks.length === 0) {
    console.log('❌ 数据文件为空！')
    return
  }
  
  console.log(`\n📈 数据日期: ${stocks[0].date}`)
  console.log(`📊 股票数量: ${stocks.length} 只\n`)
  
  const sorted = [...stocks].sort((a, b) => b.changePercent - a.changePercent)
  
  console.log('='.repeat(80))
  console.log('🔴 跌幅榜 TOP 5:')
  console.log('='.repeat(80))
  
  const losers = sorted.slice(-5).reverse()
  losers.forEach((stock, i) => {
    const emoji = stock.changePercent <= -3 ? '🔴' : 
                 stock.changePercent <= -2 ? '🟠' : '🟡'
    console.log(`${emoji} ${stock.symbol.padEnd(12)} ${stock.changePercent.toFixed(2).padStart(7)}%  (${stock.open.toFixed(2)} → ${stock.close.toFixed(2)})`)
  })
  
  console.log('\n' + '='.repeat(80))
  console.log('🟢 涨幅榜 TOP 5:')
  console.log('='.repeat(80))
  
  const gainers = sorted.slice(0, 5)
  gainers.forEach((stock, i) => {
    const emoji = stock.changePercent >= 5 ? '🟢' : 
                 stock.changePercent >= 3 ? '🟢' : '🔵'
    console.log(`${emoji} ${stock.symbol.padEnd(12)} +${stock.changePercent.toFixed(2).padStart(6)}%  (${stock.open.toFixed(2)} → ${stock.close.toFixed(2)})`)
  })
  
  console.log('\n' + '='.repeat(80))
  console.log('📊 市场统计:')
  console.log('='.repeat(80))
  
  const rises = stocks.filter(s => s.changePercent > 0).length
  const falls = stocks.filter(s => s.changePercent < 0).length
  const unchanged = stocks.filter(s => s.changePercent === 0).length
  
  const avgChange = stocks.reduce((sum, s) => sum + s.changePercent, 0) / stocks.length
  const avgVolume = stocks.reduce((sum, s) => sum + s.volume, 0) / stocks.length
  
  console.log(`上涨: ${rises} 只`)
  console.log(`下跌: ${falls} 只`)
  console.log(`平盘: ${unchanged} 只`)
  console.log(`平均涨跌: ${avgChange >= 0 ? '+' : ''}${avgChange.toFixed(2)}%`)
  console.log(`平均成交量: ${(avgVolume / 10000).toFixed(0)}万`)
  
  const bigDrops = stocks.filter(s => s.changePercent <= -3)
  if (bigDrops.length > 0) {
    console.log('\n' + '='.repeat(80))
    console.log('🔥 重点关注 (跌幅>=3%):')
    console.log('='.repeat(80))
    
    bigDrops.forEach(stock => {
      console.log(`🔴 ${stock.symbol} 下跌 ${stock.changePercent.toFixed(2)}%`)
      console.log(`   开盘: ${stock.open.toFixed(2)}  收盘: ${stock.close.toFixed(2)}  最低: ${stock.low.toFixed(2)}`)
      console.log(`   日内最大跌幅: ${((stock.low - stock.open) / stock.open * 100).toFixed(2)}%`)
      console.log('')
    })
  }
  
  console.log('\n' + '='.repeat(80))
  console.log('💡 市场分析:')
  console.log('='.repeat(80))
  
  if (avgChange > 1) {
    console.log('市场表现强劲，整体上涨')
  } else if (avgChange > 0) {
    console.log('市场小幅上涨，观望情绪浓厚')
  } else if (avgChange > -1) {
    console.log('市场小幅调整，暂无恐慌迹象')
  } else if (avgChange > -3) {
    console.log('市场明显调整，建议关注超跌机会')
  } else {
    console.log('市场恐慌下跌，可能是布局机会！')
  }
  
  console.log('\n' + '='.repeat(80))
}

main()
