import { DataFetcher } from './data/DataFetcher'
import { SMAStrategy, RSIStrategy, MACDStrategy, BollingerBandStrategy } from './strategy/Strategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { Logger } from './utils/Logger'

async function main() {
  Logger.info('Quant Trading System Starting...')

  const dataFetcher = new DataFetcher()
  
  const data = await dataFetcher.fetchDailyData('AAPL', '2020-01-01', '2023-12-31')
  Logger.info(`Fetched ${data.length} days of data`)

  const strategies = [
    new SMAStrategy({ name: 'SMA', parameters: { shortPeriod: 50, longPeriod: 200 } }),
    new RSIStrategy({ name: 'RSI', parameters: { period: 14, overbought: 70, oversold: 30 } }),
    new MACDStrategy({ name: 'MACD', parameters: { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 } }),
    new BollingerBandStrategy({ name: 'Bollinger', parameters: { period: 20, stdDev: 2 } })
  ]

  const riskManager = new RiskManager({
    maxPositionSize: 0.1,
    maxDrawdown: 0.2,
    stopLoss: 0.02,
    takeProfit: 0.05,
    maxOpenPositions: 1
  })

  for (const strategy of strategies) {
    Logger.info(`Testing ${strategy.getName()}...`)
    
    const backtester = new Backtester(strategy, riskManager, 100000)
    const result = backtester.run(data)

    Logger.success(`Backtest completed for ${strategy.getName()}`, {
      TotalReturn: `$${result.totalReturn.toFixed(2)}`,
      TotalReturnPercent: `${result.totalReturnPercent.toFixed(2)}%`,
      AnnualizedReturn: `${result.annualizedReturn.toFixed(2)}%`,
      MaxDrawdown: `${result.maxDrawdown.toFixed(2)}%`,
      SharpeRatio: result.sharpeRatio.toFixed(2),
      WinRate: `${result.winRate.toFixed(2)}%`,
      Trades: result.trades
    })
  }

  Logger.info('All strategies tested successfully')
}

main().catch(error => {
  Logger.error('Error running quant trading system', error)
  process.exit(1)
})
