import axios from 'axios'
import { BarData } from '../types'

export class TushareClient {
  private token: string
  private baseUrl = 'https://api.tushare.pro'

  constructor(token: string) {
    this.token = token
  }

  private async request(apiName: string, params: any = {}, fields?: string): Promise<any> {
    try {
      const response = await axios.post(this.baseUrl, {
        api_name: apiName,
        token: this.token,
        params,
        fields
      })

      if (response.data.code !== 0) {
        throw new Error(`Tushare API Error: ${response.data.msg}`)
      }

      return response.data.data
    } catch (error) {
      console.error('Tushare请求失败:', error)
      throw error
    }
  }

  async getStockList(): Promise<any[]> {
    const data = await this.request('stock_basic', {
      exchange: '',
      list_status: 'L',
      fields: 'ts_code,symbol,name,industry,list_date'
    })
    return data.items || []
  }

  async getDailyData(tsCode: string, startDate: string, endDate: string): Promise<BarData[]> {
    const data = await this.request('daily', {
      ts_code: tsCode,
      start_date: startDate,
      end_date: endDate
    })

    if (!data.items || data.items.length === 0) {
      return []
    }

    const barData: BarData[] = data.items.map((item: any) => {
      const [tradeDate, _, open, high, low, close, preClose, change, pctChg, vol, amount] = item
      
      const date = new Date(tradeDate.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'))
      
      return {
        timestamp: date.getTime(),
        open: parseFloat(open) || 0,
        high: parseFloat(high) || 0,
        low: parseFloat(low) || 0,
        close: parseFloat(close) || 0,
        volume: parseInt(vol) || 0
      }
    })

    return barData.reverse()
  }

  async getIndexData(tsCode: string, startDate: string, endDate: string): Promise<BarData[]> {
    const data = await this.request('index_daily', {
      ts_code: tsCode,
      start_date: startDate,
      end_date: endDate
    })

    if (!data.items || data.items.length === 0) {
      return []
    }

    const barData: BarData[] = data.items.map((item: any) => {
      const [tradeDate, _, open, high, low, close, preClose, change, pctChg, vol, amount] = item
      
      const date = new Date(tradeDate.replace(/(\d{4})(\d{2})(\d{2})/, '$1-$2-$3'))
      
      return {
        timestamp: date.getTime(),
        open: parseFloat(open) || 0,
        high: parseFloat(high) || 0,
        low: parseFloat(low) || 0,
        close: parseFloat(close) || 0,
        volume: parseInt(vol) || 0
      }
    })

    return barData.reverse()
  }

  async getTradeCalendar(exchange: string = 'SSE', startDate: string, endDate: string): Promise<any[]> {
    const data = await this.request('trade_cal', {
      exchange,
      start_date: startDate,
      end_date: endDate
    })
    return data.items || []
  }

  static formatTsCode(symbol: string): string {
    if (symbol.includes('.')) {
      return symbol
    }
    
    if (symbol.startsWith('6')) {
      return `${symbol}.SH`
    } else if (symbol.startsWith('0') || symbol.startsWith('3')) {
      return `${symbol}.SZ`
    }
    return symbol
  }
}
