import { Portfolio, RiskConfig } from '../types'

export class RiskManager {
  private config: RiskConfig

  constructor(config: RiskConfig) {
    this.config = {
      maxPositionSize: config.maxPositionSize || 0.1,
      maxDrawdown: config.maxDrawdown || 0.2,
      stopLoss: config.stopLoss || 0.02,
      takeProfit: config.takeProfit || 0.05,
      maxOpenPositions: config.maxOpenPositions || 5
    }
  }

  canOpenPosition(portfolio: Portfolio, symbol: string): boolean {
    if (portfolio.positions.length >= this.config.maxOpenPositions) {
      return false
    }

    const existingPosition = portfolio.positions.find(p => p.symbol === symbol)
    if (existingPosition) {
      return false
    }

    const currentDrawdown = this.calculateDrawdown(portfolio)
    if (currentDrawdown >= this.config.maxDrawdown) {
      return false
    }

    return true
  }

  calculatePositionSize(portfolio: Portfolio, price: number): number {
    const maxPositionValue = portfolio.totalValue * this.config.maxPositionSize
    const quantity = Math.floor(maxPositionValue / price)
    return Math.max(quantity, 1)
  }

  calculateDrawdown(portfolio: Portfolio): number {
    const peakValue = portfolio.initialCapital
    const currentValue = portfolio.totalValue
    return Math.max(0, (peakValue - currentValue) / peakValue)
  }

  shouldSell(position: any, currentPrice: number): { shouldSell: boolean, reason: string } {
    const profitPercent = ((currentPrice - position.avgCost) / position.avgCost)
    
    if (profitPercent <= -this.config.stopLoss) {
      return { shouldSell: true, reason: 'Stop loss triggered' }
    }
    
    if (this.config.takeProfit > 0 && profitPercent >= this.config.takeProfit) {
      return { shouldSell: true, reason: 'Take profit triggered' }
    }
    
    return { shouldSell: false, reason: '' }
  }

  updateConfig(config: Partial<RiskConfig>): void {
    this.config = { ...this.config, ...config }
  }

  getConfig(): RiskConfig {
    return { ...this.config }
  }
}
