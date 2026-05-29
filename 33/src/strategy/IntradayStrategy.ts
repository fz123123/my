import { BarData, TradeSignal, StrategyConfig } from '../types'
import { Strategy } from './Strategy'
import { Indicator } from './Indicator'

export interface IntradayConfig {
  buyTime: number
  sellTime: number
  minVolume: number
  profitTarget: number
  stopLoss: number
}

export class T1Strategy extends Strategy {
  private buyTime: number
  private sellTime: number
  private minVolume: number
  private profitTarget: number
  private stopLoss: number
  private holdingPosition: boolean = false
  private entryPrice: number = 0
  private entryDay: number = -1
  private entryIndex: number = -1
  private prevDayHigh: number = 0

  constructor(config: StrategyConfig) {
    super(config)
    this.buyTime = config.parameters.buyTime as number || 1450
    this.sellTime = config.parameters.sellTime as number || 1030
    this.minVolume = config.parameters.minVolume as number || 2000000
    this.profitTarget = config.parameters.profitTarget as number || 0.015
    this.stopLoss = config.parameters.stopLoss as number || 0.02
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

    const todayVolume = data[index].volume
    const avgVolume = this.calculateAvgVolume(data, index, 20)
    const volumeOk = todayVolume >= avgVolume * 0.8 && todayVolume >= this.minVolume

    const rsi = Indicator.RSI(data, 14)
    const currRsi = rsi[index]

    const sma20 = Indicator.SMA(data, 20)[index]
    const sma60 = Indicator.SMA(data, 60)[index]
    const priceAboveSma20 = price >= sma20 * 0.99
    const smaTrendUp = sma20 >= sma60 * 0.995

    const todayChange = (price - data[index].open) / data[index].open
    const hasUpwardMomentum = todayChange >= -0.005

    const volatility = this.calculateVolatility(data, index, 10)
    const lowVolatility = volatility < 0.02

    const momentum = this.calculateMomentum(data, index, 5)
    const positiveMomentum = momentum >= 0

    if (!this.holdingPosition) {
      const isBuyCondition = 
        volumeOk && 
        currRsi >= 30 && currRsi <= 60 && 
        priceAboveSma20 && 
        smaTrendUp && 
        hasUpwardMomentum &&
        lowVolatility &&
        positiveMomentum

      if (isBuyCondition) {
        this.holdingPosition = true
        this.entryPrice = price
        this.entryDay = dayOfYear
        this.entryIndex = index
        this.prevDayHigh = data[index].high
        
        return {
          timestamp,
          type: 'buy',
          symbol,
          price,
          reason: `T+1 Entry: Volume=${todayVolume.toLocaleString()}, RSI=${currRsi.toFixed(1)}, SMA20=${sma20.toFixed(2)}`
        }
      }
    } else {
      const daysHeld = dayOfYear - this.entryDay

      if (daysHeld >= 1 && index > this.entryIndex) {
        const todayOpen = data[index].open
        const todayHigh = data[index].high
        const todayLow = data[index].low
        
        const gapUp = (todayOpen - this.prevDayHigh) / this.prevDayHigh
        
        let exitPrice = todayHigh
        let exitReason = ''
        
        const targetPrice = this.entryPrice * (1 + this.profitTarget)
        const stopLossPrice = this.entryPrice * (1 - this.stopLoss)

        if (todayHigh >= targetPrice) {
          exitPrice = Math.min(todayHigh, targetPrice)
          exitReason = `Profit target reached ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        } else if (todayLow <= stopLossPrice) {
          exitPrice = Math.max(todayLow, stopLossPrice)
          exitReason = `Stop loss hit ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        } else if (gapUp > 0.005 && todayHigh >= this.entryPrice * 1.005) {
          exitPrice = todayHigh
          exitReason = `Gap up profit ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}% (gap=${(gapUp*100).toFixed(2)}%)`
        } else if (daysHeld >= 1) {
          exitPrice = todayOpen
          exitReason = `End of day 1 sell (gap=${(gapUp*100).toFixed(2)}%)`
        }

        if (exitReason) {
          this.holdingPosition = false
          return {
            timestamp,
            type: 'sell',
            symbol,
            price: exitPrice,
            reason: `T+1 Exit: ${exitReason}`
          }
        }
      }
    }

    return {
      timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
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

  private calculateVolatility(data: BarData[], index: number, period: number): number {
    let sum = 0
    const start = Math.max(0, index - period + 1)
    for (let i = start; i <= index; i++) {
      const range = data[i].high - data[i].low
      sum += range / data[i].close
    }
    return sum / (index - start + 1)
  }

  private calculateMomentum(data: BarData[], index: number, period: number): number {
    const start = Math.max(0, index - period)
    return data[index].close - data[start].close
  }

  getName(): string {
    return `T+1 Strategy (${this.buyTime}->${this.sellTime})`
  }
}

export class T1GapUpStrategy extends Strategy {
  private minGap: number
  private maxGap: number
  private profitTarget: number
  private stopLoss: number
  private holdingPosition: boolean = false
  private entryPrice: number = 0

  constructor(config: StrategyConfig) {
    super(config)
    this.minGap = config.parameters.minGap as number || 0.015
    this.maxGap = config.parameters.maxGap as number || 0.08
    this.profitTarget = config.parameters.profitTarget as number || 0.012
    this.stopLoss = config.parameters.stopLoss as number || 0.015
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const symbol = 'DEFAULT'
    const price = data[index].close
    const timestamp = data[index].timestamp

    if (index < 2) {
      return {
        timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }

    if (!this.holdingPosition) {
      const prevClose = data[index - 1].close
      const todayOpen = data[index].open
      const gap = (todayOpen - prevClose) / prevClose

      if (gap >= this.minGap && gap <= this.maxGap) {
        const sma20 = Indicator.SMA(data, 20)[index - 1]
        const aboveSma = todayOpen >= sma20
        
        if (aboveSma) {
          this.holdingPosition = true
          this.entryPrice = todayOpen
          
          return {
            timestamp,
            type: 'buy',
            symbol,
            price: todayOpen,
            reason: `Gap up entry: gap=${(gap*100).toFixed(2)}%, open=${todayOpen.toFixed(2)}, SMA20=${sma20.toFixed(2)}`
          }
        }
      }
    } else {
      const todayHigh = data[index].high
      const todayLow = data[index].low
      
      const profitAtHigh = (todayHigh - this.entryPrice) / this.entryPrice
      const lossAtLow = (todayLow - this.entryPrice) / this.entryPrice
      
      if (profitAtHigh >= this.profitTarget) {
        this.holdingPosition = false
        const exitPrice = Math.min(todayHigh, this.entryPrice * (1 + this.profitTarget))
        return {
          timestamp,
          type: 'sell',
          symbol,
          price: exitPrice,
          reason: `Gap up exit: Profit target ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        }
      }
      
      if (lossAtLow <= -this.stopLoss) {
        this.holdingPosition = false
        const exitPrice = Math.max(todayLow, this.entryPrice * (1 - this.stopLoss))
        return {
          timestamp,
          type: 'sell',
          symbol,
          price: exitPrice,
          reason: `Gap up exit: Stop loss ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        }
      }
    }

    return {
      timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
  }

  getName(): string {
    return `T+1 Gap Up Strategy`
  }
}
