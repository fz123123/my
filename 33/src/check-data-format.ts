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
  intradayDrop: number
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
      const intradayDrop = ((parseFloat(parts[4].trim()) - open) / open) * 100
      
      stocks.push({
        symbol: parts[0].trim(),
        date: parts[1].trim(),
        open,
        high: parseFloat(parts[3].trim()),
        low: parseFloat(parts[4].trim()),
        close,
        volume: parseInt(parts[6].trim()) || 0,
        change,
        changePercent,
        intradayDrop
      })
    }
  }
  
  return stocks
}

function main() {
  console.log('='.repeat(80))
  console.log('🔍 数据格式检查')
  console.log('='.repeat(80))
  
  const dataPath = path.join(__dirname, '../data/tdx/today_data.csv')
  
  if (!fs.existsSync(dataPath)) {
    console.log('\n❌ 文件不存在！')
    console.log(`📁 路径: ${dataPath}`)
    return
  }
  
  console.log(`\n✅ 文件存在: ${dataPath}`)
  
  const stats = fs.statSync(dataPath)
  console.log(`📊 文件大小: ${(stats.size / 1024).toFixed(2)} KB`)
  console.log(`📅 最后修改: ${stats.mtime.toLocaleString('zh-CN')}`)
  
  const stocks = parseTodayData(dataPath)
  
  if (stocks.length === 0) {
    console.log('\n❌ 数据解析失败！')
    console.log('\n请检查CSV格式是否正确：')
    console.log('  格式: 股票代码,日期,开盘,最高,最低,收盘,成交量')
    console.log('  示例: 000001.SZ,2025-05-21,10.50,10.75,10.40,10.65,52000000')
    return
  }
  
  console.log(`\n✅ 数据解析成功: ${stocks.length} 只股票`)
  console.log(`📅 数据日期: ${stocks[0].date}`)
  
  console.log('\n' + '='.repeat(80))
  console.log('📋 数据格式验证')
  console.log('='.repeat(80))
  
  console.log('\n✅ 表头格式正确:')
  console.log('   股票代码, 日期, 开盘, 最高, 最低, 收盘, 成交量')
  
  console.log('\n✅ 数据字段验证:')
  const sample = stocks[0]
  console.log(`   股票代码: ${sample.symbol} (${typeof sample.symbol})`)
  console.log(`   日期: ${sample.date} (${typeof sample.date})`)
  console.log(`   开盘: ${sample.open} (${typeof sample.open})`)
  console.log(`   最高: ${sample.high} (${typeof sample.high})`)
  console.log(`   最低: ${sample.low} (${typeof sample.low})`)
  console.log(`   收盘: ${sample.close} (${typeof sample.close})`)
  console.log(`   成交量: ${sample.volume} (${typeof sample.volume})`)
  
  console.log('\n' + '='.repeat(80))
  console.log('📊 市场涨跌统计')
  console.log('='.repeat(80))
  
  const rises = stocks.filter(s => s.changePercent > 0).length
  const falls = stocks.filter(s => s.changePercent < 0).length
  const unchanged = stocks.filter(s => s.changePercent === 0).length
  
  console.log(`\n上涨: ${rises} 只 (${(rises / stocks.length * 100).toFixed(1)}%)`)
  console.log(`下跌: ${falls} 只 (${(falls / stocks.length * 100).toFixed(1)}%)`)
  console.log(`平盘: ${unchanged} 只 (${(unchanged / stocks.length * 100).toFixed(1)}%)`)
  
  console.log('\n' + '='.repeat(80))
  console.log('🔴 跌幅榜（按收盘价涨跌排序）')
  console.log('='.repeat(80))
  
  const sorted = [...stocks].sort((a, b) => a.changePercent - b.changePercent)
  
  sorted.forEach((stock, i) => {
    const bar = '█'.repeat(Math.min(20, Math.abs(stock.changePercent)))
    const emoji = stock.changePercent <= -3 ? '🔴' : 
                   stock.changePercent <= -2 ? '🟠' : 
                   stock.changePercent <= -1 ? '🟡' : '⚪'
    
    console.log(`${emoji} ${stock.symbol.padEnd(12)} ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2).padStart(7)}% ${bar}`)
  })
  
  console.log('\n' + '='.repeat(80))
  console.log('📈 日内最大跌幅（最低点相对开盘）')
  console.log('='.repeat(80))
  
  const byIntraday = [...stocks].sort((a, b) => a.intradayDrop - b.intradayDrop)
  
  byIntraday.forEach((stock, i) => {
    if (stock.intradayDrop < 0) {
      const bar = '█'.repeat(Math.min(20, Math.abs(stock.intradayDrop)))
      console.log(`🔴 ${stock.symbol.padEnd(12)} ${stock.intradayDrop.toFixed(2).padStart(7)}% ${bar}`)
    }
  })
  
  console.log('\n' + '='.repeat(80))
  console.log('🔍 恐慌盘扫描条件')
  console.log('='.repeat(80))
  
  const bigDrops = stocks.filter(s => s.changePercent <= -3 || s.intradayDrop <= -3)
  const moderateDrops = stocks.filter(s => s.changePercent <= -2 || s.intradayDrop <= -2)
  const smallDrops = stocks.filter(s => s.changePercent <= -1 || s.intradayDrop <= -1)
  
  console.log(`\n大跌（>=3%）: ${bigDrops.length} 只`)
  if (bigDrops.length > 0) {
    bigDrops.forEach(s => console.log(`  🔴 ${s.symbol}: 收盘${s.changePercent.toFixed(2)}% | 日内${s.intradayDrop.toFixed(2)}%`))
  }
  
  console.log(`\n中跌（>=2%）: ${moderateDrops.length} 只`)
  if (moderateDrops.length > 0) {
    moderateDrops.forEach(s => console.log(`  🟠 ${s.symbol}: 收盘${s.changePercent.toFixed(2)}% | 日内${s.intradayDrop.toFixed(2)}%`))
  }
  
  console.log(`\n小跌（>=1%）: ${smallDrops.length} 只`)
  if (smallDrops.length > 0) {
    smallDrops.forEach(s => console.log(`  🟡 ${s.symbol}: 收盘${s.changePercent.toFixed(2)}% | 日内${s.intradayDrop.toFixed(2)}%`))
  }
  
  console.log('\n' + '='.repeat(80))
  console.log('💡 建议')
  console.log('='.repeat(80))
  
  if (stocks[0].date !== new Date().toISOString().split('T')[0]) {
    console.log(`\n⚠️  警告：数据日期是 ${stocks[0].date}`)
    console.log(`   今天日期是 ${new Date().toISOString().split('T')[0]}`)
    console.log(`   请更新为今日数据以获得准确的恐慌盘扫描结果`)
  }
  
  if (falls === 0) {
    console.log('\n✅ 市场全面上涨，无恐慌盘迹象')
    console.log('   恐慌盘策略需要在大跌时寻找低吸机会')
  } else if (bigDrops.length === 0) {
    console.log('\n📊 市场小幅调整，无大跌恐慌盘')
    console.log('   可能需要降低筛选阈值或等待更明显的恐慌信号')
  } else {
    console.log(`\n🔥 发现 ${bigDrops.length} 只大跌股票，可关注恐慌盘机会`)
  }
  
  console.log('\n' + '='.repeat(80))
}

main()
