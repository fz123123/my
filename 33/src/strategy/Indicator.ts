import { BarData } from '../types'

export class Indicator {
  static SMA(data: BarData[], period: number): number[] {
    const result: number[] = []
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(NaN)
      } else {
        let sum = 0
        for (let j = i - period + 1; j <= i; j++) {
          sum += data[j].close
        }
        result.push(sum / period)
      }
    }
    return result
  }

  static EMA(data: BarData[], period: number): number[] {
    const result: number[] = []
    const alpha = 2 / (period + 1)
    
    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        result.push(data[i].close)
      } else {
        const prevEma = result[i - 1]
        result.push(alpha * data[i].close + (1 - alpha) * prevEma)
      }
    }
    return result
  }

  static RSI(data: BarData[], period: number): number[] {
    const result: number[] = []
    
    for (let i = 0; i < data.length; i++) {
      if (i < period) {
        result.push(NaN)
      } else {
        let gains = 0
        let losses = 0
        
        for (let j = i - period + 1; j <= i; j++) {
          const change = data[j].close - data[j - 1].close
          if (change > 0) {
            gains += change
          } else {
            losses += Math.abs(change)
          }
        }
        
        const avgGain = gains / period
        const avgLoss = losses / period
        
        if (avgLoss === 0) {
          result.push(100)
        } else {
          const rs = avgGain / avgLoss
          result.push(100 - (100 / (1 + rs)))
        }
      }
    }
    return result
  }

  static MACD(data: BarData[], fastPeriod: number = 12, slowPeriod: number = 26, signalPeriod: number = 9): { macd: number[], signal: number[], histogram: number[] } {
    const fastEma = this.EMA(data, fastPeriod)
    const slowEma = this.EMA(data, slowPeriod)
    
    const macd: number[] = []
    for (let i = 0; i < data.length; i++) {
      macd.push(fastEma[i] - slowEma[i])
    }
    
    const signal = this.EMAFromArray(macd, signalPeriod)
    
    const histogram: number[] = []
    for (let i = 0; i < data.length; i++) {
      histogram.push(macd[i] - signal[i])
    }
    
    return { macd, signal, histogram }
  }

  private static EMAFromArray(data: number[], period: number): number[] {
    const result: number[] = []
    const alpha = 2 / (period + 1)
    
    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        result.push(data[i])
      } else {
        const prevEma = result[i - 1]
        result.push(alpha * data[i] + (1 - alpha) * prevEma)
      }
    }
    return result
  }

  static BollingerBands(data: BarData[], period: number, stdDev: number): { upper: number[], middle: number[], lower: number[] } {
    const middle = this.SMA(data, period)
    const upper: number[] = []
    const lower: number[] = []
    
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        upper.push(NaN)
        lower.push(NaN)
      } else {
        let sumSquaredDiff = 0
        for (let j = i - period + 1; j <= i; j++) {
          sumSquaredDiff += Math.pow(data[j].close - middle[i], 2)
        }
        const std = Math.sqrt(sumSquaredDiff / period)
        upper.push(middle[i] + stdDev * std)
        lower.push(middle[i] - stdDev * std)
      }
    }
    
    return { upper, middle, lower }
  }

  static ATR(data: BarData[], period: number): number[] {
    const result: number[] = []
    
    for (let i = 0; i < data.length; i++) {
      if (i === 0) {
        result.push(NaN)
      } else {
        const tr = Math.max(
          data[i].high - data[i].low,
          Math.abs(data[i].high - data[i - 1].close),
          Math.abs(data[i].low - data[i - 1].close)
        )
        
        if (i < period) {
          let sumTr = 0
          for (let j = 1; j <= i; j++) {
            const prevTr = Math.max(
              data[j].high - data[j].low,
              Math.abs(data[j].high - data[j - 1].close),
              Math.abs(data[j].low - data[j - 1].close)
            )
            sumTr += prevTr
          }
          result.push(sumTr / i)
        } else {
          result.push((result[i - 1] * (period - 1) + tr) / period)
        }
      }
    }
    
    return result
  }

  static VWAP(data: BarData[]): number[] {
    const result: number[] = []
    let cumulativeVolume = 0
    let cumulativeTypicalPriceVolume = 0
    
    for (let i = 0; i < data.length; i++) {
      const typicalPrice = (data[i].high + data[i].low + data[i].close) / 3
      cumulativeVolume += data[i].volume
      cumulativeTypicalPriceVolume += typicalPrice * data[i].volume
      
      if (cumulativeVolume > 0) {
        result.push(cumulativeTypicalPriceVolume / cumulativeVolume)
      } else {
        result.push(NaN)
      }
    }
    
    return result
  }
}
