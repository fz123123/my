import { indicators } from './indicators'

export const stockSelector = {
  async selectBullStocks(stocks, klineData) {
    const bullStocks = []
    
    for (const stock of stocks) {
      const score = await this.evaluateStock(stock, klineData[stock.code])
      if (score >= 60) {
        bullStocks.push({ ...stock, score, reason: this.getReason(score) })
      }
    }
    
    return bullStocks.sort((a, b) => b.score - a.score)
  },

  async evaluateStock(stock, klineData) {
    let score = 50
    
    if (stock.change > 2) {
      score += 15
    } else if (stock.change > 0) {
      score += 5
    }
    
    if (stock.pe < 30) {
      score += 10
    }
    
    if (klineData && klineData.data && klineData.data.length > 0) {
      const data = klineData.data
      const macd = indicators.calculateMACD(data)
      const kdj = indicators.calculateKDJ(data)
      const rsi = indicators.calculateRSI(data)
      const boll = indicators.calculateBOLL(data)
      
      const latestMACD = macd.MACD[macd.MACD.length - 1]
      const latestDIF = macd.DIF[macd.DIF.length - 1]
      const latestDEA = macd.DEA[macd.DEA.length - 1]
      
      if (latestMACD && latestDIF && latestDEA) {
        if (latestDIF > latestDEA && latestMACD > 0) {
          score += 15
        } else if (latestDIF > latestDEA) {
          score += 8
        }
      }
      
      const latestK = kdj.K[kdj.K.length - 1]
      const latestD = kdj.D[kdj.D.length - 1]
      
      if (latestK && latestD) {
        if (latestK > latestD && latestK < 70) {
          score += 10
        } else if (latestK > latestD) {
          score += 5
        }
      }
      
      const latestRSI = rsi[rsi.length - 1]
      if (latestRSI && latestRSI > 50 && latestRSI < 70) {
        score += 10
      }
      
      const latestClose = data[data.length - 1].close
      const middle = boll.middle[boll.middle.length - 1]
      if (middle && latestClose > middle) {
        score += 5
      }
    }
    
    const volume = parseFloat(stock.volume.replace('万', ''))
    if (volume > 50) {
      score += 5
    }
    
    return Math.min(score, 100)
  },

  getReason(score) {
    if (score >= 80) {
      return '强烈推荐 - 多项指标显示强势上涨信号'
    } else if (score >= 70) {
      return '推荐 - 技术面表现良好，有上涨潜力'
    } else if (score >= 60) {
      return '关注 - 存在一定上涨机会，建议观察'
    } else {
      return '观望 - 暂不具备明显上涨条件'
    }
  },

  analyzeStock(stock, klineData) {
    const analysis = {
      general: {},
      indicators: {}
    }
    
    analysis.general = {
      name: stock.name,
      code: stock.code,
      price: stock.price,
      change: stock.change,
      pe: stock.pe,
      pb: stock.pb
    }
    
    if (klineData && klineData.data && klineData.data.length > 0) {
      const data = klineData.data
      analysis.indicators = {
        macd: indicators.calculateMACD(data),
        kdj: indicators.calculateKDJ(data),
        rsi: indicators.calculateRSI(data),
        boll: indicators.calculateBOLL(data),
        ma5: indicators.calculateMA(data, 5),
        ma10: indicators.calculateMA(data, 10),
        ma20: indicators.calculateMA(data, 20),
        ma60: indicators.calculateMA(data, 60)
      }
    }
    
    return analysis
  }
}