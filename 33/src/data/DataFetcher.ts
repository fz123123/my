import axios from 'axios'
import * as fs from 'fs'
import * as path from 'path'
import { BarData } from '../types'
import { TushareClient } from './TushareClient'
import { configManager } from '../config'

export class DataFetcher {
  private cacheDir = path.join(__dirname, '../../data/cache')
  private tushareClient: TushareClient | null = null

  constructor() {
    if (!fs.existsSync(this.cacheDir)) {
      fs.mkdirSync(this.cacheDir, { recursive: true })
    }

    if (configManager.useTushare() && configManager.getTushareToken()) {
      this.tushareClient = new TushareClient(configManager.getTushareToken())
    }
  }

  async fetchDailyData(symbol: string, startDate: string, endDate: string): Promise<BarData[]> {
    const cacheKey = `${symbol}_${startDate}_${endDate}.json`
    const cachePath = path.join(this.cacheDir, cacheKey)

    if (fs.existsSync(cachePath)) {
      const data = fs.readFileSync(cachePath, 'utf-8')
      return JSON.parse(data)
    }

    let data: BarData[] = []

    if (configManager.useTushare() && this.tushareClient) {
      try {
        const tsCode = TushareClient.formatTsCode(symbol)
        const formattedStart = startDate.replace(/-/g, '')
        const formattedEnd = endDate.replace(/-/g, '')
        data = await this.tushareClient.getDailyData(tsCode, formattedStart, formattedEnd)
      } catch (error) {
        console.warn('使用Tushare获取数据失败，使用模拟数据:', error)
      }
    }

    if (data.length === 0) {
      data = await this.generateRealisticData(symbol, startDate, endDate)
    }

    fs.writeFileSync(cachePath, JSON.stringify(data))
    return data
  }

  private async generateRealisticData(symbol: string, startDate: string, endDate: string): Promise<BarData[]> {
    const start = new Date(startDate)
    const end = new Date(endDate)
    const data: BarData[] = []

    let currentDate = start
    let basePrice = 100
    let trend = 0
    let volatility = 0.015

    while (currentDate <= end) {
      if (currentDate.getDay() !== 0 && currentDate.getDay() !== 6) {
        const trendChange = (Math.random() - 0.5) * 0.002
        trend = Math.max(-0.003, Math.min(0.003, trend + trendChange))

        const volatilityChange = (Math.random() - 0.5) * 0.002
        volatility = Math.max(0.008, Math.min(0.025, volatility + volatilityChange))

        const randomFactor = (Math.random() - 0.5) * 2 * volatility * basePrice
        const change = trend * basePrice + randomFactor
        
        const open = basePrice
        const close = Math.max(open + change, 1)
        
        const range = volatility * basePrice
        const high = Math.max(open, close) + Math.random() * range * 0.5
        const low = Math.min(open, close) - Math.random() * range * 0.5
        
        const volume = Math.floor(Math.random() * 8000000) + 2000000

        data.push({
          timestamp: currentDate.getTime(),
          open: parseFloat(open.toFixed(2)),
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
          volume
        })

        basePrice = close
      }

      currentDate = new Date(currentDate.getTime() + 24 * 60 * 60 * 1000)
    }

    return data
  }

  async fetchMultipleSymbols(symbols: string[], startDate: string, endDate: string): Promise<Record<string, BarData[]>> {
    const results: Record<string, BarData[]> = {}
    for (const symbol of symbols) {
      results[symbol] = await this.fetchDailyData(symbol, startDate, endDate)
    }
    return results
  }

  loadFromCSV(filePath: string): BarData[] {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n').filter(line => line.trim())
    
    const data: BarData[] = []
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].split(',')
      if (parts.length >= 6) {
        data.push({
          timestamp: new Date(parts[0]).getTime(),
          open: parseFloat(parts[1]),
          high: parseFloat(parts[2]),
          low: parseFloat(parts[3]),
          close: parseFloat(parts[4]),
          volume: parseInt(parts[5])
        })
      }
    }
    return data
  }

  saveToCSV(data: BarData[], filePath: string): void {
    const headers = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    const lines = [headers.join(',')]
    
    for (const bar of data) {
      lines.push([
        new Date(bar.timestamp).toISOString().split('T')[0],
        bar.open,
        bar.high,
        bar.low,
        bar.close,
        bar.volume
      ].join(','))
    }
    
    fs.writeFileSync(filePath, lines.join('\n'))
  }
}
