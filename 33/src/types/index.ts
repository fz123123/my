export interface BarData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface TradeSignal {
  timestamp: number
  type: 'buy' | 'sell' | 'hold'
  symbol: string
  price: number
  quantity?: number
  reason: string
}

export interface Position {
  symbol: string
  quantity: number
  avgCost: number
  currentPrice: number
  marketValue: number
  profit: number
  profitPercent: number
}

export interface Portfolio {
  cash: number
  positions: Position[]
  totalValue: number
  initialCapital: number
  return: number
  returnPercent: number
}

export interface BacktestResult {
  startDate: string
  endDate: string
  initialCapital: number
  finalCapital: number
  totalReturn: number
  totalReturnPercent: number
  annualizedReturn: number
  maxDrawdown: number
  sharpeRatio: number
  winRate: number
  profitFactor: number
  trades: number
  equityCurve: number[]
}

export interface StrategyConfig {
  name: string
  parameters: Record<string, number | string | boolean>
}

export interface RiskConfig {
  maxPositionSize: number
  maxDrawdown: number
  stopLoss: number
  takeProfit: number
  maxOpenPositions: number
}

export interface Config {
  tushare: {
    token: string
    enabled: boolean
  }
  data: {
    cacheDir: string
    useTushare: boolean
  }
}
