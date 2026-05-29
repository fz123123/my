#!/usr/bin/env ts-node
import * as fs from 'fs'
import * as path from 'path'
import { BarData } from './types'

interface StockData {
  symbol: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface PanicAnalysis {
  symbol: string
  drop: number
  intradayDrop: number
  volumeRatio: number
  reason: string
  recommendation: string
  score: number
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
      stocks.push({
        symbol: parts[0].trim(),
        date: parts[1].trim(),
        open: parseFloat(parts[2].trim()),
        high: parseFloat(parts[3].trim()),
        low: parseFloat(parts[4].trim()),
        close: parseFloat(parts[5].trim()),
        volume: parseInt(parts[6].trim()) || 0
      })
    }
  }
  
  return stocks
}

function analyzePanic(stocks: StockData[], avgVolumes: Map<string, number>): PanicAnalysis[] {
  const results: PanicAnalysis[] = []
  
  for (const stock of stocks) {
    const drop = (stock.close - stock.open) / stock.open
    const lowDrop = (stock.low - stock.open) / stock.open
    const avgVol = avgVolumes.get(stock.symbol) || stock.volume * 0.8
    const volumeRatio = stock.volume / avgVol
    
    const maxDrop = Math.min(drop, lowDrop)
    
    let score = 0
    let reasons: string[] = []
    
    if (maxDrop <= -0.08) {
      score += 50
      reasons.push(`恐慌性抛售 ${Math.abs(maxDrop * 100).toFixed(2)}%`)
    } else if (maxDrop <= -0.06) {
      score += 40
      reasons.push(`大幅下跌 ${Math.abs(maxDrop * 100).toFixed(2)}%`)
    } else if (maxDrop <= -0.04) {
      score += 30
      reasons.push(`明显下跌 ${Math.abs(maxDrop * 100).toFixed(2)}%`)
    } else if (maxDrop <= -0.03) {
      score += 20
      reasons.push(`中等下跌 ${Math.abs(maxDrop * 100).toFixed(2)}%`)
    } else if (maxDrop <= -0.02) {
      score += 10
      reasons.push(`小幅下跌 ${Math.abs(maxDrop * 100).toFixed(2)}%`)
    }
    
    if (volumeRatio >= 3.0) {
      score += 40
      reasons.push(`天量恐慌 ${volumeRatio.toFixed(1)}倍`)
    } else if (volumeRatio >= 2.5) {
      score += 35
      reasons.push(`巨量下跌 ${volumeRatio.toFixed(1)}倍`)
    } else if (volumeRatio >= 2.0) {
      score += 30
      reasons.push(`明显放量 ${volumeRatio.toFixed(1)}倍`)
    } else if (volumeRatio >= 1.5) {
      score += 20
      reasons.push(`温和放量 ${volumeRatio.toFixed(1)}倍`)
    }
    
    if (score >= 15) {
      const recommendation = score >= 60 ? '🔥 强烈建议关注' : 
                            score >= 40 ? '📊 建议关注' : 
                            score >= 20 ? '👀 观察等待' : '❌ 暂不推荐'
      
      results.push({
        symbol: stock.symbol,
        drop: maxDrop,
        intradayDrop: drop,
        volumeRatio,
        reason: reasons.join(' + '),
        recommendation,
        score
      })
    }
  }
  
  return results.sort((a, b) => b.score - a.score)
}

function main() {
  console.log('='.repeat(80))
  console.log('🔍 今日恐慌盘扫描系统')
  console.log('='.repeat(80))
  
  const dataPath = path.join(__dirname, '../data/tdx/today_data.csv')
  
  if (!fs.existsSync(dataPath)) {
    console.log('❌ 未找到今日数据文件！')
    console.log(`📁 请将数据文件放入: ${dataPath}`)
    return
  }
  
  const stocks = parseTodayData(dataPath)
  
  if (stocks.length === 0) {
    console.log('❌ 数据文件为空或格式错误！')
    return
  }
  
  console.log(`\n📊 加载数据: ${stocks.length} 只股票`)
  
  const avgVolumes = new Map<string, number>()
  for (const stock of stocks) {
    avgVolumes.set(stock.symbol, stock.volume * 0.8)
  }
  
  const panicStocks = analyzePanic(stocks, avgVolumes)
  
  console.log('\n' + '='.repeat(80))
  console.log('📈 恐慌盘分析结果')
  console.log('='.repeat(80))
  
  if (panicStocks.length === 0) {
    console.log('\n✅ 今日市场无恐慌盘迹象，市场情绪稳定')
  } else {
    console.log(`\n🔥 发现 ${panicStocks.length} 只恐慌抛压股票:\n`)
    
    for (let i = 0; i < panicStocks.length; i++) {
      const stock = panicStocks[i]
      const emoji = stock.recommendation === '强烈建议关注' ? '🔥' : 
                   stock.recommendation === '建议关注' ? '📊' : '👀'
      
      console.log(`${i + 1}. ${emoji} ${stock.symbol}`)
      console.log(`   ${stock.reason}`)
      console.log(`   评分: ${stock.score}分 | ${stock.recommendation}`)
      console.log('')
    }
    
    console.log('='.repeat(80))
    console.log('💡 操作建议:')
    console.log('='.repeat(80))
    
    const strong = panicStocks.filter(s => s.recommendation === '强烈建议关注')
    const moderate = panicStocks.filter(s => s.recommendation === '建议关注')
    
    if (strong.length > 0) {
      console.log('\n🔥 强烈关注标的 (可考虑低吸):')
      strong.forEach(s => console.log(`  - ${s.symbol}: ${s.reason}`))
    }
    
    if (moderate.length > 0) {
      console.log('\n📊 建议观察标的:')
      moderate.forEach(s => console.log(`  - ${s.symbol}: ${s.reason}`))
    }
    
    console.log('\n💰 低吸策略要点:')
    console.log('  1. 等待缩量企稳后再买入')
    console.log('  2. 分批建仓，控制仓位')
    console.log('  3. 设置止损位，一般不超过6%')
    console.log('  4. 目标收益8%左右及时止盈')
    console.log('  5. 持仓不超过15个交易日')
  }
  
  console.log('\n' + '='.repeat(80))
  console.log('✅ 扫描完成')
  console.log('='.repeat(80))
}

main()
