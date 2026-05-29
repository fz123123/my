import { BarData, TradeSignal, Portfolio, Position, BacktestResult } from '../types'
import { Strategy } from '../strategy/Strategy'
import { RiskManager } from '../risk/RiskManager'

export interface TransactionCostConfig {
  commissionRate: number
  slippage: number
  impactCost: number
  minCommission: number
}

export class Backtester {
  private strategy: Strategy
  private riskManager: RiskManager
  private initialCapital: number
  private portfolio: Portfolio
  private equityCurve: number[]
  private trades: TradeSignal[]
  private winTrades: number
  private totalProfit: number
  private totalLoss: number
  private transactionCost: TransactionCostConfig
  private dailyHighs: number[]
  private dailyLows: number[]

  constructor(strategy: Strategy, riskManager: RiskManager, initialCapital: number, transactionCost?: Partial<TransactionCostConfig>) {
    this.strategy = strategy
    this.riskManager = riskManager
    this.initialCapital = initialCapital
    this.transactionCost = {
      commissionRate: transactionCost?.commissionRate || 0.0003,
      slippage: transactionCost?.slippage || 0.0005,
      impactCost: transactionCost?.impactCost || 0.0003,
      minCommission: transactionCost?.minCommission || 5
    }
    this.portfolio = {
      cash: initialCapital,
      positions: [],
      totalValue: initialCapital,
      initialCapital,
      return: 0,
      returnPercent: 0
    }
    this.equityCurve = [initialCapital]
    this.trades = []
    this.winTrades = 0
    this.totalProfit = 0
    this.totalLoss = 0
    this.dailyHighs = []
    this.dailyLows = []
  }

  run(data: BarData[]): BacktestResult {
    for (let i = 0; i < data.length; i++) {
      this.dailyHighs.push(data[i].high)
      this.dailyLows.push(data[i].low)
      
      const signal = this.strategy.generateSignal(data, i)
      this.processSignal(signal, data[i])
      this.updatePortfolio(data[i])
      this.equityCurve.push(this.portfolio.totalValue)
    }
    return this.calculateResults(data)
  }

  private processSignal(signal: TradeSignal, bar: BarData): void {
    if (signal.type === 'buy') {
      if (!this.riskManager.canOpenPosition(this.portfolio, signal.symbol)) {
        return
      }

      const executionPrice = this.calculateBuyPrice(bar)
      const positionSize = this.riskManager.calculatePositionSize(this.portfolio, executionPrice)
      const cost = positionSize * executionPrice
      const commission = this.calculateCommission(cost)
      const totalCost = cost + commission

      if (totalCost <= this.portfolio.cash) {
        this.portfolio.cash -= totalCost
        this.portfolio.positions.push({
          symbol: signal.symbol,
          quantity: positionSize,
          avgCost: executionPrice,
          currentPrice: bar.close,
          marketValue: positionSize * bar.close,
          profit: positionSize * (bar.close - executionPrice) - commission,
          profitPercent: 0
        })
        signal.quantity = positionSize
        signal.price = executionPrice
        this.trades.push(signal)
      }
    } else if (signal.type === 'sell') {
      const positionIndex = this.portfolio.positions.findIndex(p => p.symbol === signal.symbol)
      if (positionIndex !== -1) {
        const position = this.portfolio.positions[positionIndex]
        const executionPrice = this.calculateSellPrice(bar)
        const proceeds = position.quantity * executionPrice
        const commission = this.calculateCommission(proceeds)
        const netProceeds = proceeds - commission
        const profit = netProceeds - position.quantity * position.avgCost

        this.portfolio.cash += netProceeds
        this.portfolio.positions.splice(positionIndex, 1)
        signal.quantity = position.quantity
        signal.price = executionPrice
        this.trades.push(signal)

        if (profit > 0) {
          this.winTrades++
          this.totalProfit += profit
        } else {
          this.totalLoss += Math.abs(profit)
        }
      }
    }
  }

  private calculateBuyPrice(bar: BarData): number {
    const slippageAmount = bar.close * this.transactionCost.slippage
    const impactAmount = bar.close * this.transactionCost.impactCost
    return bar.close + slippageAmount + impactAmount
  }

  private calculateSellPrice(bar: BarData): number {
    const slippageAmount = bar.close * this.transactionCost.slippage
    const impactAmount = bar.close * this.transactionCost.impactCost
    return bar.close - slippageAmount - impactAmount
  }

  private calculateCommission(amount: number): number {
    const commission = amount * this.transactionCost.commissionRate
    return Math.max(commission, this.transactionCost.minCommission)
  }

  private updatePortfolio(bar: BarData): void {
    let totalMarketValue = 0
    for (const position of this.portfolio.positions) {
      position.currentPrice = bar.close
      position.marketValue = position.quantity * position.currentPrice
      position.profit = position.marketValue - position.quantity * position.avgCost
      position.profitPercent = (position.profit / (position.quantity * position.avgCost)) * 100
      totalMarketValue += position.marketValue
    }
    this.portfolio.totalValue = this.portfolio.cash + totalMarketValue
    this.portfolio.return = this.portfolio.totalValue - this.portfolio.initialCapital
    this.portfolio.returnPercent = (this.portfolio.return / this.portfolio.initialCapital) * 100
  }

  private calculateResults(data: BarData[]): BacktestResult {
    const startDate = new Date(data[0].timestamp).toISOString().split('T')[0]
    const endDate = new Date(data[data.length - 1].timestamp).toISOString().split('T')[0]
    const finalCapital = this.portfolio.totalValue
    const totalReturn = finalCapital - this.initialCapital
    const totalReturnPercent = (totalReturn / this.initialCapital) * 100

    const days = (data[data.length - 1].timestamp - data[0].timestamp) / (1000 * 60 * 60 * 24)
    const years = days / 365
    const annualizedReturn = years > 0 ? Math.pow(1 + totalReturnPercent / 100, 1 / years) - 1 : 0

    let maxDrawdown = 0
    let peak = this.initialCapital
    for (const equity of this.equityCurve) {
      peak = Math.max(peak, equity)
      const drawdown = (peak - equity) / peak
      maxDrawdown = Math.max(maxDrawdown, drawdown)
    }

    const dailyReturns: number[] = []
    for (let i = 1; i < this.equityCurve.length; i++) {
      dailyReturns.push((this.equityCurve[i] - this.equityCurve[i - 1]) / this.equityCurve[i - 1])
    }

    const meanReturn = dailyReturns.reduce((sum, r) => sum + r, 0) / dailyReturns.length || 0
    const volatility = Math.sqrt(dailyReturns.reduce((sum, r) => sum + Math.pow(r - meanReturn, 2), 0) / dailyReturns.length) || 0
    const sharpeRatio = volatility > 0 ? (meanReturn / volatility) * Math.sqrt(252) : 0

    const winRate = this.trades.length > 0 ? (this.winTrades / this.trades.length) * 100 : 0
    const profitFactor = this.totalLoss > 0 ? this.totalProfit / this.totalLoss : Infinity

    return {
      startDate,
      endDate,
      initialCapital: this.initialCapital,
      finalCapital,
      totalReturn,
      totalReturnPercent: totalReturnPercent,
      annualizedReturn: annualizedReturn * 100,
      maxDrawdown: maxDrawdown * 100,
      sharpeRatio,
      winRate,
      profitFactor,
      trades: this.trades.length,
      equityCurve: this.equityCurve
    }
  }

  getTrades(): TradeSignal[] {
    return this.trades
  }

  getEquityCurve(): number[] {
    return this.equityCurve
  }

  getTransactionCostConfig(): TransactionCostConfig {
    return { ...this.transactionCost }
  }
}
