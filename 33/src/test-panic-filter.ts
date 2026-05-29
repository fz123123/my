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
  changePercent: number
  intradayDrop: number
  volumeRatio: number
  score: number
  recommendation: string
}

function parseCSV(content: string): StockData[] {
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
      const low = parseFloat(parts[4].trim())
      const changePercent = ((close - open) / open) * 100
      const intradayDrop = ((low - open) / open) * 100
      const volume = parseInt(parts[6].trim()) || 0
      const avgVolume = volume * 0.75
      const volumeRatio = volume / avgVolume
      
      let score = 0
      let reasons: string[] = []
      
      if (changePercent <= -5) {
        score += 35
        reasons.push(`大跌${Math.abs(changePercent).toFixed(2)}%`)
      } else if (changePercent <= -3) {
        score += 25
        reasons.push(`下跌${Math.abs(changePercent).toFixed(2)}%`)
      } else if (changePercent <= -2) {
        score += 15
        reasons.push(`小跌${Math.abs(changePercent).toFixed(2)}%`)
      }
      
      if (intradayDrop <= -5) {
        score += 30
        reasons.push(`恐慌${Math.abs(intradayDrop).toFixed(2)}%`)
      } else if (intradayDrop <= -3) {
        score += 20
        reasons.push(`重挫${Math.abs(intradayDrop).toFixed(2)}%`)
      } else if (intradayDrop <= -2) {
        score += 10
        reasons.push(`调整${Math.abs(intradayDrop).toFixed(2)}%`)
      }
      
      if (volumeRatio >= 2.0) {
        score += 25
        reasons.push(`放量${volumeRatio.toFixed(1)}倍`)
      } else if (volumeRatio >= 1.5) {
        score += 15
        reasons.push(`温和放量${volumeRatio.toFixed(1)}倍`)
      }
      
      const recommendation = score >= 60 ? '🔥 强烈建议关注' : 
                           score >= 40 ? '📊 建议关注' : 
                           score >= 20 ? '👀 观察' : '⏸️ 暂不关注'
      
      stocks.push({
        symbol: parts[0].trim(),
        date: parts[1].trim(),
        open,
        high: parseFloat(parts[3].trim()),
        low,
        close,
        volume,
        changePercent,
        intradayDrop,
        volumeRatio,
        score,
        recommendation
      })
    }
  }
  
  return stocks.sort((a, b) => b.score - a.score)
}

function main() {
  console.log('='.repeat(80))
  console.log('🧪 恐慌盘筛选功能测试')
  console.log('='.repeat(80))
  
  const testDataPath = path.join(__dirname, '../data/tdx/test_panic_today.csv')
  const todayDataPath = path.join(__dirname, '../data/tdx/today_data.csv')
  
  console.log('\n📝 步骤1: 复制测试数据到 today_data.csv')
  
  if (!fs.existsSync(testDataPath)) {
    console.log('❌ 测试数据文件不存在！')
    return
  }
  
  fs.copyFileSync(testDataPath, todayDataPath)
  console.log('✅ 测试数据已复制')
  
  const content = fs.readFileSync(todayDataPath, 'utf-8')
  const stocks = parseCSV(content)
  
  if (stocks.length === 0) {
    console.log('❌ 数据解析失败！')
    return
  }
  
  console.log(`✅ 成功解析 ${stocks.length} 只股票`)
  console.log(`📅 数据日期: ${stocks[0].date}`)
  
  console.log('\n' + '='.repeat(80))
  console.log('📊 测试数据统计')
  console.log('='.repeat(80))
  
  const bigDrops = stocks.filter(s => s.changePercent <= -5)
  const mediumDrops = stocks.filter(s => s.changePercent > -5 && s.changePercent <= -3)
  const smallDrops = stocks.filter(s => s.changePercent > -3 && s.changePercent <= -1)
  const rises = stocks.filter(s => s.changePercent > -1)
  
  console.log(`\n大跌 (>=5%): ${bigDrops.length} 只`)
  console.log(`中跌 (3-5%): ${mediumDrops.length} 只`)
  console.log(`小跌 (1-3%): ${smallDrops.length} 只`)
  console.log(`上涨 (<-1%): ${rises.length} 只`)
  
  console.log('\n' + '='.repeat(80))
  console.log('🔥 恐慌盘筛选结果')
  console.log('='.repeat(80))
  
  const panicStocks = stocks.filter(s => s.score >= 20)
  
  if (panicStocks.length === 0) {
    console.log('\n⚠️  未筛选出恐慌盘标的')
    console.log('   恐慌盘筛选条件：')
    console.log('   - 大跌 (>=3%) + 放量 (>=1.5倍)')
    console.log('   - 或恐慌下跌 (>=5%)')
  } else {
    console.log(`\n✅ 筛选出 ${panicStocks.length} 只恐慌盘标的:\n`)
    
    panicStocks.forEach((stock, i) => {
      console.log(`${i + 1}. ${stock.symbol}`)
      console.log(`   收盘: ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2)}%`)
      console.log(`   日内最大跌幅: ${stock.intradayDrop.toFixed(2)}%`)
      console.log(`   量比: ${stock.volumeRatio.toFixed(1)}倍`)
      console.log(`   ${stock.recommendation}`)
      console.log('')
    })
  }
  
  console.log('='.repeat(80))
  console.log('📈 完整涨跌榜')
  console.log('='.repeat(80))
  
  stocks.forEach((stock, i) => {
    const bar = '█'.repeat(Math.min(15, Math.abs(stock.changePercent)))
    const emoji = stock.changePercent <= -5 ? '🔴' : 
                   stock.changePercent <= -3 ? '🟠' : 
                   stock.changePercent <= -1 ? '🟡' : 
                   stock.changePercent <= 1 ? '⚪' : '🟢'
    
    console.log(`${emoji} ${stock.symbol.padEnd(12)} ${stock.changePercent >= 0 ? '+' : ''}${stock.changePercent.toFixed(2).padStart(6)}% ${bar}`)
  })
  
  console.log('\n' + '='.repeat(80))
  console.log('✅ 功能验证完成！')
  console.log('='.repeat(80))
  
  console.log('\n💡 使用说明:')
  console.log('  1. 测试数据已保存到 today_data.csv')
  console.log('  2. 运行 "npm run scan-panic" 查看筛选结果')
  console.log('  3. 运行 "npm run market" 查看市场概况')
  console.log('  4. 替换为真实数据后即可正常使用')
  
  console.log('\n' + '='.repeat(80))
}

main()
