import { BarData, TradeSignal, StrategyConfig } from '../types'
import { Strategy } from './Strategy'
import { Indicator } from './Indicator'

export interface PanicBuyConfig {
  minDrop: number          // 单日最小跌幅
  volumeRatio: number      // 成交量放大倍数
  rsiOversold: number      // RSI超卖阈值
  profitTarget: number     // 止盈目标
  stopLoss: number         // 止损幅度
  maxHoldDays: number      // 最大持仓天数
}

export class PanicBuyStrategy extends Strategy {
  private minDrop: number
  private volumeRatio: number
  private rsiOversold: number
  private profitTarget: number
  private stopLoss: number
  private maxHoldDays: number
  
  private holdingPosition: boolean = false
  private entryPrice: number = 0
  private entryDay: number = -1
  
  constructor(config: StrategyConfig) {
    super(config)
    this.minDrop = config.parameters.minDrop as number || 0.03
    this.volumeRatio = config.parameters.volumeRatio as number || 1.2
    this.rsiOversold = config.parameters.rsiOversold as number || 30
    this.profitTarget = config.parameters.profitTarget as number || 0.08
    this.stopLoss = config.parameters.stopLoss as number || 0.06
    this.maxHoldDays = config.parameters.maxHoldDays as number || 15
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const symbol = 'DEFAULT'
    const price = data[index].close
    const timestamp = data[index].timestamp
    const dayOfYear = this.getDayOfYear(timestamp)

    if (index < 30) {
      return {
        timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }

    if (!this.holdingPosition) {
      const panicSignal = this.detectPanicSell(data, index)
      
      if (panicSignal.isPanic) {
        this.holdingPosition = true
        this.entryPrice = price
        this.entryDay = dayOfYear
        
        return {
          timestamp,
          type: 'buy',
          symbol,
          price,
          reason: `恐慌低吸: 跌幅${(panicSignal.drop*100).toFixed(2)}%, 量比${panicSignal.volRatio.toFixed(2)}x, RSI${panicSignal.rsi.toFixed(1)}`
        }
      }
    } else {
      const exitSignal = this.determineExit(data, index)
      
      if (exitSignal.shouldExit) {
        this.holdingPosition = false
        return {
          timestamp,
          type: 'sell',
          symbol,
          price: exitSignal.price,
          reason: exitSignal.reason
        }
      }
    }

    return {
      timestamp,
      type: 'hold',
      symbol,
      price,
      reason: '无信号'
    }
  }

  private detectPanicSell(data: BarData[], index: number): {
    isPanic: boolean
    drop: number
    volRatio: number
    rsi: number
  } {
    const bar = data[index]
    
    let totalDrop = 0
    let maxIntradayDrop = 0
    let maxVolume = 0
    
    for (let i = 0; i < 3; i++) {
      if (index - i <= 0) break
      const currentBar = data[index - i]
      const prevBar = data[index - i - 1]
      totalDrop += (currentBar.close - prevBar.close) / prevBar.close
      
      const intradayDrop = (currentBar.low - currentBar.open) / currentBar.open
      maxIntradayDrop = Math.min(maxIntradayDrop, intradayDrop)
      
      maxVolume = Math.max(maxVolume, currentBar.volume)
    }
    
    const avgVolume = this.calculateAvgVolume(data, index, 20)
    const volRatio = maxVolume / avgVolume
    
    const rsi = Indicator.RSI(data, 14)[index]
    
    const combinedDrop = Math.min(totalDrop, maxIntradayDrop)
    
    const isBigDrop = combinedDrop <= -this.minDrop
    const isHighVolume = volRatio >= this.volumeRatio
    const isOversold = rsi <= this.rsiOversold
    
    const isPanic = (isBigDrop || totalDrop <= -this.minDrop * 0.7) && isHighVolume && isOversold
    
    return {
      isPanic,
      drop: combinedDrop,
      volRatio,
      rsi
    }
  }

  private determineExit(data: BarData[], index: number): {
    shouldExit: boolean
    price: number
    reason: string
  } {
    const bar = data[index]
    const daysHeld = this.getDayOfYear(bar.timestamp) - this.entryDay
    
    const targetPrice = this.entryPrice * (1 + this.profitTarget)
    const stopLossPrice = this.entryPrice * (1 - this.stopLoss)
    
    if (bar.high >= targetPrice) {
      return {
        shouldExit: true,
        price: targetPrice,
        reason: `止盈: +${((targetPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
      }
    }
    
    if (bar.low <= stopLossPrice) {
      return {
        shouldExit: true,
        price: stopLossPrice,
        reason: `止损: ${((stopLossPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
      }
    }
    
    if (daysHeld >= this.maxHoldDays) {
      return {
        shouldExit: true,
        price: bar.close,
        reason: `持仓${daysHeld}天，时间止盈`
      }
    }
    
    return { shouldExit: false, price: 0, reason: '' }
  }

  private getDayOfYear(timestamp: number): number {
    const date = new Date(timestamp)
    const start = new Date(date.getFullYear(), 0, 0)
    const diff = date.getTime() - start.getTime()
    return Math.floor(diff / (1000 * 60 * 60 * 24))
  }

  private calculateAvgVolume(data: BarData[], index: number, period: number): number {
    let sum = 0
    const start = Math.max(0, index - period + 1)
    for (let i = start; i <= index; i++) {
      sum += data[i].volume
    }
    return sum / (index - start + 1)
  }

  getName(): string {
    return `恐慌低吸策略(跌幅>${(this.minDrop*100).toFixed(1)}%)`
  }
}
