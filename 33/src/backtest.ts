import * as yargs from 'yargs'
import { DataFetcher } from './data/DataFetcher'
import { SMAStrategy, RSIStrategy, MACDStrategy, BollingerBandStrategy, Strategy } from './strategy/Strategy'
import { Backtester } from './backtest/Backtester'
import { RiskManager } from './risk/RiskManager'
import { Logger } from './utils/Logger'

interface StrategyConstructor {
  new(config: { name: string; parameters: Record<string, number | string | boolean> }): Strategy
}

const strategyMap: Record<string, StrategyConstructor> = {
  sma: SMAStrategy,
  rsi: RSIStrategy,
  macd: MACDStrategy,
  bollinger: BollingerBandStrategy
}

async function runBacktest(strategyName: string, symbol: string, startDate: string, endDate: string, initialCapital: number) {
  const StrategyClass = strategyMap[strategyName.toLowerCase()]
  if (!StrategyClass) {
    Logger.error(`Unknown strategy: ${strategyName}`)
    process.exit(1)
  }

  const dataFetcher = new DataFetcher()
  const data = await dataFetcher.fetchDailyData(symbol, startDate, endDate)
  
  Logger.info(`Fetched ${data.length} days of data for ${symbol}`)

  const strategy = new StrategyClass({ name: strategyName, parameters: {} })
  const riskManager = new RiskManager({
    maxPositionSize: 0.1,
    maxDrawdown: 0.2,
    stopLoss: 0.02,
    takeProfit: 0.05,
    maxOpenPositions: 1
  })

  const backtester = new Backtester(strategy, riskManager, initialCapital)
  const result = backtester.run(data)

  console.log('\n=== Backtest Results ===')
  console.log(`Strategy: ${strategy.getName()}`)
  console.log(`Symbol: ${symbol}`)
  console.log(`Date Range: ${startDate} to ${endDate}`)
  console.log(`Initial Capital: $${initialCapital.toLocaleString()}`)
  console.log(`Final Capital: $${result.finalCapital.toLocaleString()}`)
  console.log(`Total Return: $${result.totalReturn.toFixed(2)} (${result.totalReturnPercent.toFixed(2)}%)`)
  console.log(`Annualized Return: ${result.annualizedReturn.toFixed(2)}%`)
  console.log(`Max Drawdown: ${result.maxDrawdown.toFixed(2)}%`)
  console.log(`Sharpe Ratio: ${result.sharpeRatio.toFixed(2)}`)
  console.log(`Win Rate: ${result.winRate.toFixed(2)}%`)
  console.log(`Total Trades: ${result.trades}`)
  console.log(`Profit Factor: ${result.profitFactor.toFixed(2)}`)
}

yargs
  .command('backtest', 'Run backtest with specified strategy', (yargs) => {
    return yargs
      .option('strategy', {
        alias: 's',
        type: 'string',
        demandOption: true,
        choices: ['sma', 'rsi', 'macd', 'bollinger'],
        description: 'Strategy to use'
      })
      .option('symbol', {
        alias: 'sym',
        type: 'string',
        default: 'AAPL',
        description: 'Stock symbol'
      })
      .option('start', {
        alias: 'st',
        type: 'string',
        default: '2020-01-01',
        description: 'Start date (YYYY-MM-DD)'
      })
      .option('end', {
        alias: 'e',
        type: 'string',
        default: '2023-12-31',
        description: 'End date (YYYY-MM-DD)'
      })
      .option('capital', {
        alias: 'c',
        type: 'number',
        default: 100000,
        description: 'Initial capital'
      })
  }, async (argv) => {
    await runBacktest(argv.strategy, argv.symbol, argv.start, argv.end, argv.capital)
  })
  .help()
  .argv
