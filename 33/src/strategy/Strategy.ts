import { BarData, TradeSignal, StrategyConfig } from '../types'
import { Indicator } from './Indicator'

export abstract class Strategy {
  protected config: StrategyConfig

  constructor(config: StrategyConfig) {
    this.config = config
  }

  abstract generateSignal(data: BarData[], index: number): TradeSignal

  abstract getName(): string
}

export class SMAStrategy extends Strategy {
  private shortPeriod: number
  private longPeriod: number

  constructor(config: StrategyConfig) {
    super(config)
    this.shortPeriod = config.parameters.shortPeriod as number || 50
    this.longPeriod = config.parameters.longPeriod as number || 200
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const smaShort = Indicator.SMA(data, this.shortPeriod)
    const smaLong = Indicator.SMA(data, this.longPeriod)
    
    const symbol = 'DEFAULT'
    const price = data[index].close
    
    if (index < this.longPeriod - 1) {
      return {
        timestamp: data[index].timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }
    
    const prevShort = smaShort[index - 1]
    const prevLong = smaLong[index - 1]
    const currShort = smaShort[index]
    const currLong = smaLong[index]
    
    if (prevShort <= prevLong && currShort > currLong) {
      return {
        timestamp: data[index].timestamp,
        type: 'buy',
        symbol,
        price,
        reason: `Golden cross: ${this.shortPeriod}-period SMA crossed above ${this.longPeriod}-period SMA`
      }
    } else if (prevShort >= prevLong && currShort < currLong) {
      return {
        timestamp: data[index].timestamp,
        type: 'sell',
        symbol,
        price,
        reason: `Death cross: ${this.shortPeriod}-period SMA crossed below ${this.longPeriod}-period SMA`
      }
    }
    
    return {
      timestamp: data[index].timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
  }

  getName(): string {
    return 'SMA Crossover Strategy'
  }
}

export class RSIStrategy extends Strategy {
  private period: number
  private overbought: number
  private oversold: number

  constructor(config: StrategyConfig) {
    super(config)
    this.period = config.parameters.period as number || 14
    this.overbought = config.parameters.overbought as number || 70
    this.oversold = config.parameters.oversold as number || 30
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const rsi = Indicator.RSI(data, this.period)
    const symbol = 'DEFAULT'
    const price = data[index].close
    
    if (index < this.period) {
      return {
        timestamp: data[index].timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }
    
    const currRsi = rsi[index]
    const prevRsi = rsi[index - 1]
    
    if (prevRsi >= this.oversold && currRsi < this.oversold) {
      return {
        timestamp: data[index].timestamp,
        type: 'buy',
        symbol,
        price,
        reason: `RSI crossed below ${this.oversold} (oversold)`
      }
    } else if (prevRsi <= this.overbought && currRsi > this.overbought) {
      return {
        timestamp: data[index].timestamp,
        type: 'sell',
        symbol,
        price,
        reason: `RSI crossed above ${this.overbought} (overbought)`
      }
    }
    
    return {
      timestamp: data[index].timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
  }

  getName(): string {
    return 'RSI Strategy'
  }
}

export class MACDStrategy extends Strategy {
  private fastPeriod: number
  private slowPeriod: number
  private signalPeriod: number

  constructor(config: StrategyConfig) {
    super(config)
    this.fastPeriod = config.parameters.fastPeriod as number || 12
    this.slowPeriod = config.parameters.slowPeriod as number || 26
    this.signalPeriod = config.parameters.signalPeriod as number || 9
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const { macd, signal } = Indicator.MACD(data, this.fastPeriod, this.slowPeriod, this.signalPeriod)
    const symbol = 'DEFAULT'
    const price = data[index].close
    
    if (index < this.slowPeriod + this.signalPeriod) {
      return {
        timestamp: data[index].timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }
    
    const prevMacd = macd[index - 1]
    const prevSignal = signal[index - 1]
    const currMacd = macd[index]
    const currSignal = signal[index]
    
    if (prevMacd <= prevSignal && currMacd > currSignal) {
      return {
        timestamp: data[index].timestamp,
        type: 'buy',
        symbol,
        price,
        reason: 'MACD line crossed above signal line'
      }
    } else if (prevMacd >= prevSignal && currMacd < currSignal) {
      return {
        timestamp: data[index].timestamp,
        type: 'sell',
        symbol,
        price,
        reason: 'MACD line crossed below signal line'
      }
    }
    
    return {
      timestamp: data[index].timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
  }

  getName(): string {
    return 'MACD Strategy'
  }
}

export class BollingerBandStrategy extends Strategy {
  private period: number
  private stdDev: number

  constructor(config: StrategyConfig) {
    super(config)
    this.period = config.parameters.period as number || 20
    this.stdDev = config.parameters.stdDev as number || 2
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const { upper, lower, middle } = Indicator.BollingerBands(data, this.period, this.stdDev)
    const symbol = 'DEFAULT'
    const price = data[index].close
    
    if (index < this.period - 1) {
      return {
        timestamp: data[index].timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }
    
    const prevPrice = data[index - 1].close
    const currUpper = upper[index]
    const currLower = lower[index]
    
    if (prevPrice >= currLower && price < currLower) {
      return {
        timestamp: data[index].timestamp,
        type: 'buy',
        symbol,
        price,
        reason: 'Price crossed below lower Bollinger Band'
      }
    } else if (prevPrice <= currUpper && price > currUpper) {
      return {
        timestamp: data[index].timestamp,
        type: 'sell',
        symbol,
        price,
        reason: 'Price crossed above upper Bollinger Band'
      }
    }
    
    return {
      timestamp: data[index].timestamp,
      type: 'hold',
      symbol,
      price,
      reason: 'No signal'
    }
  }

  getName(): string {
    return 'Bollinger Band Strategy'
  }
}
