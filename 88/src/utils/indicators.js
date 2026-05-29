export const indicators = {
  calculateMA(data, days) {
    const result = []
    for (let i = 0; i < data.length; i++) {
      if (i < days - 1) {
        result.push(null)
        continue
      }
      let sum = 0
      for (let j = i - days + 1; j <= i; j++) {
        sum += data[j].close
      }
      result.push(parseFloat((sum / days).toFixed(2)))
    }
    return result
  },

  calculateMACD(data) {
    const EMA12 = this.calculateEMA(data, 12)
    const EMA26 = this.calculateEMA(data, 26)
    const DIF = EMA12.map((val, i) => val && EMA26[i] ? parseFloat((val - EMA26[i]).toFixed(4)) : null)
    const DEA = this.calculateEMA({ data: DIF.filter(v => v !== null) }, 9)
    const MACD = DIF.map((val, i) => val && DEA[i] ? parseFloat(((val - DEA[i]) * 2).toFixed(4)) : null)
    
    while (DEA.length < DIF.length) {
      DEA.unshift(null)
    }
    
    return { DIF, DEA, MACD }
  },

  calculateEMA(data, days) {
    const result = []
    const alpha = 2 / (days + 1)
    let ema = null
    
    for (let i = 0; i < data.length; i++) {
      const close = data[i].close
      if (close === null) {
        result.push(null)
        continue
      }
      if (ema === null) {
        ema = close
      } else {
        ema = parseFloat(((close * alpha) + (ema * (1 - alpha))).toFixed(4))
      }
      result.push(ema)
    }
    return result
  },

  calculateKDJ(data) {
    const lowList = []
    const highList = []
    const K = []
    const D = []
    const J = []
    
    for (let i = 0; i < data.length; i++) {
      if (i < 8) {
        lowList.push(data[i].low)
        highList.push(data[i].high)
        K.push(null)
        D.push(null)
        J.push(null)
        continue
      }
      
      const slice = data.slice(i - 8, i + 1)
      const low = Math.min(...slice.map(d => d.low))
      const high = Math.max(...slice.map(d => d.high))
      const close = data[i].close
      
      const RSV = ((close - low) / (high - low)) * 100
      const currentK = K[i - 1] ? ((2 / 3) * K[i - 1] + (1 / 3) * RSV) : RSV
      const currentD = D[i - 1] ? ((2 / 3) * D[i - 1] + (1 / 3) * currentK) : currentK
      const currentJ = 3 * currentK - 2 * currentD
      
      K.push(parseFloat(currentK.toFixed(2)))
      D.push(parseFloat(currentD.toFixed(2)))
      J.push(parseFloat(currentJ.toFixed(2)))
    }
    
    return { K, D, J }
  },

  calculateRSI(data, days = 14) {
    const result = []
    let upSum = 0
    let downSum = 0
    
    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close
      if (change > 0) {
        upSum += change
      } else {
        downSum += Math.abs(change)
      }
      
      if (i >= days) {
        const avgUp = upSum / days
        const avgDown = downSum / days
        const rsi = avgDown === 0 ? 100 : parseFloat((100 - (100 / (1 + avgUp / avgDown))).toFixed(2))
        result.push(rsi)
        
        const firstChange = data[i - days + 1].close - data[i - days].close
        if (firstChange > 0) {
          upSum -= firstChange
        } else {
          downSum -= Math.abs(firstChange)
        }
      } else {
        result.push(null)
      }
    }
    
    while (result.length < data.length) {
      result.unshift(null)
    }
    
    return result
  },

  calculateBOLL(data, days = 20) {
    const middle = this.calculateMA(data, days)
    const upper = []
    const lower = []
    
    for (let i = 0; i < data.length; i++) {
      if (i < days - 1) {
        upper.push(null)
        lower.push(null)
        continue
      }
      
      const slice = data.slice(i - days + 1, i + 1)
      const avg = middle[i]
      let variance = 0
      for (let j = 0; j < slice.length; j++) {
        variance += Math.pow(slice[j].close - avg, 2)
      }
      const std = Math.sqrt(variance / days)
      upper.push(parseFloat((avg + 2 * std).toFixed(2)))
      lower.push(parseFloat((avg - 2 * std).toFixed(2)))
    }
    
    return { upper, middle, lower }
  }
}