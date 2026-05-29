import { BarData, TradeSignal, StrategyConfig } from '../types'
import { Strategy } from './Strategy'

export class SimpleT1Strategy extends Strategy {
  private profitTarget: number
  private stopLoss: number
  private holdingPosition: boolean = false
  private entryPrice: number = 0
  private entryIndex: number = -1

  constructor(config: StrategyConfig) {
    super(config)
    this.profitTarget = config.parameters.profitTarget as number || 0.015
    this.stopLoss = config.parameters.stopLoss as number || 0.02
  }

  generateSignal(data: BarData[], index: number): TradeSignal {
    const symbol = 'DEFAULT'
    const price = data[index].close
    const timestamp = data[index].timestamp

    if (index < 5) {
      return {
        timestamp,
        type: 'hold',
        symbol,
        price,
        reason: 'Waiting for enough data'
      }
    }

    const todayChange = (price - data[index].open) / data[index].open
    const prevChange = (data[index - 1].close - data[index - 1].open) / data[index - 1].open

    if (!this.holdingPosition) {
      const isBuyCondition = todayChange >= -0.01 && todayChange <= 0.03 && prevChange >= -0.01

      if (isBuyCondition) {
        this.holdingPosition = true
        this.entryPrice = price
        this.entryIndex = index
        
        return {
          timestamp,
          type: 'buy',
          symbol,
          price,
          reason: `T+1 Entry: Price=${price.toFixed(2)}, Change=${(todayChange*100).toFixed(2)}%`
        }
      }
    } else {
      const daysHeld = index - this.entryIndex

      if (daysHeld >= 1) {
        const todayOpen = data[index].open
        const todayHigh = data[index].high
        const todayLow = data[index].low
        
        let exitPrice = price
        let exitReason = ''
        
        const targetPrice = this.entryPrice * (1 + this.profitTarget)
        const stopPrice = this.entryPrice * (1 - this.stopLoss)

        if (todayHigh >= targetPrice) {
          exitPrice = Math.min(todayHigh, targetPrice)
          exitReason = `Profit target ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        } else if (todayLow <= stopPrice) {
          exitPrice = Math.max(todayLow, stopPrice)
          exitReason = `Stop loss ${((exitPrice - this.entryPrice) / this.entryPrice * 100).toFixed(2)}%`
        } else if (daysHeld >= 1) {
          exitPrice = todayOpen
          exitReason = `End of day 1 sell`
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

  getName(): string {
    return 'Simple T+1 Strategy'
  }
}
