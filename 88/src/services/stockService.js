import axios from 'axios'

const SINA_API = '/api/sina/'
const EAST_MONEY_API = '/api/em'
const EAST_MONEY_HIS_API = '/api/emhis'

let dataCache = new Map()
const CACHE_DURATION = 30000

let apiErrorCount = {
  sina: 0,
  eastmoney: 0
}

export const stockService = {
  async getStockList() {
    const cacheKey = 'stockList'
    const cached = this.getFromCache(cacheKey)
    if (cached) return cached
    
    try {
      const codes = [
        // 白酒行业
        'sh600519', 'sz000858', 'sz000568', 'sh002304',
        // 银行
        'sh600036', 'sh601318', 'sh601398', 'sh601939',
        'sz000001', 'sh601166', 'sh600000', 'sh601328',
        // 保险
        'sh601318', 'sh601601', 'sh601336', 'sz000627',
        // 券商
        'sh600030', 'sh601211', 'sh601688', 'sz000776',
        'sh600837', 'sh600958', 'sz002736',
        // 科技成长
        'sz300750', 'sz002594', 'sh601012', 'sh603986',
        'sz002415', 'sh600745', 'sz300059', 'sh688111',
        // 医药
        'sh600276', 'sh603259', 'sz300015', 'sz000538',
        'sh600196', 'sz002007', 'sh600329',
        // 消费家电
        'sz000333', 'sz000651', 'sh600690', 'sz000100',
        'sh600887', 'sz002032', 'sh600618',
        // 房地产
        'sz000002', 'sh600048', 'sh600383', 'sz001979',
        'sh601155', 'sh600606', 'sz000402',
        // 新能源
        'sh600900', 'sh600905', 'sz002459', 'sz300014',
        'sh601615', 'sz002129', 'sh600438',
        // 基建制造
        'sh601668', 'sh601186', 'sh601390', 'sz002048',
        'sh600031', 'sz000425', 'sh600170',
        // 通信电子
        'sh600941', 'sh601728', 'sh600050', 'sz000063',
        'sz002241', 'sh603160', 'sz300033',
        // 化工材料
        'sh600309', 'sh601216', 'sz002601', 'sh600989',
        'sz002092', 'sh600486', 'sh600596',
        // 军工
        'sh600893', 'sz000733', 'sh600760', 'sz002013',
        'sh601989', 'sz002025', 'sh600862',
        // 食品饮料
        'sh600132', 'sz000895', 'sh600597', 'sz002714',
        'sh600300', 'sz002507', 'sh603288',
        // 汽车
        'sz002594', 'sh600104', 'sz000625', 'sh601127',
        'sz002126', 'sh600742', 'sz002048',
        // 半导体
        'sh688981', 'sz002371', 'sh603501', 'sh688008',
        'sz300782', 'sh600584', 'sz002156',
        // 互联网科技
        'sh600570', 'sz300033', 'sh600588', 'sz002410',
        'sh600184', 'sz002230', 'sh600718'
      ]
      
      const response = await axios.get(`${SINA_API}${codes.join(',')}`, {
        headers: {
          'Referer': 'http://finance.sina.com.cn',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        timeout: 10000
      })
      
      const stocks = this.parseSinaData(response.data)
      if (stocks && stocks.length > 0) {
        apiErrorCount.sina = 0
        this.setToCache(cacheKey, stocks)
        return stocks
      }
      
      throw new Error('解析数据为空')
    } catch (error) {
      console.error('新浪财经API失败:', error.message)
      apiErrorCount.sina++
      
      try {
        const fallback = await this.getStockListFromEastMoney()
        if (fallback && fallback.length > 0) {
          this.setToCache(cacheKey, fallback)
          return fallback
        }
      } catch (e) {
        console.error('东方财富API也失败:', e.message)
      }
      
      return this.getFallbackStockList()
    }
  },

  async getStockListFromEastMoney() {
    try {
      const response = await axios.get(
        `${EAST_MONEY_API}/api/qt/ulist.np/get?secids=1.000001,1.600519,1.601318,1.600036,0.000858,0.002594,0.300750,0.000002&fields=f1,f2,f3,f4,f5,f6,f12,f13,f14,f15,f16,f17,f18&ut=bd1d9ddb04089700cf9c27f6f7426281`,
        {
          headers: {
            'Referer': 'http://quote.eastmoney.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
          },
          timeout: 10000
        }
      )
      
      if (response.data && response.data.data && response.data.data.diff) {
        return response.data.data.diff.map(item => ({
          code: item.f12,
          name: item.f14,
          price: item.f2 || 0,
          change: item.f3 || 0,
          volume: this.formatVolume((item.f5 || 0) * 100),
          open: item.f17 || 0,
          high: item.f15 || 0,
          low: item.f16 || 0,
          prevClose: item.f18 || 0
        }))
      }
      
      return null
    } catch (error) {
      console.error('东方财富列表API失败:', error.message)
      return null
    }
  },

  parseSinaData(data) {
    if (!data || typeof data !== 'string') {
      console.error('数据格式错误')
      return []
    }
    
    const stocks = []
    const lines = data.split('\n')
    
    lines.forEach(line => {
      if (!line || !line.includes('=') || !line.includes('"')) return
      
      const match = line.match(/hq_str_(\w+)="(.+)"/)
      if (!match) return
      
      const code = match[1]
      const values = match[2].split(',')
      
      if (values.length < 32) return
      
      const name = values[0]
      if (!name || name.length === 0) return
      
      const open = parseFloat(values[1]) || 0
      const prevClose = parseFloat(values[2]) || 0
      const current = parseFloat(values[3]) || 0
      const high = parseFloat(values[4]) || 0
      const low = parseFloat(values[5]) || 0
      const volume = parseInt(values[8]) || 0
      
      const change = prevClose > 0 ? parseFloat(((current - prevClose) / prevClose * 100).toFixed(2)) : 0
      
      if (current === 0) return
      
      stocks.push({
        code: code.replace(/^[a-z]{2}/, ''),
        name: name,
        price: current.toFixed(2),
        change: change,
        volume: this.formatVolume(volume),
        open: open.toFixed(2),
        high: high.toFixed(2),
        low: low.toFixed(2),
        prevClose: prevClose.toFixed(2)
      })
    })
    
    return stocks
  },

  formatVolume(volume) {
    if (volume >= 100000000) {
      return (volume / 100000000).toFixed(2) + '亿'
    } else if (volume >= 10000) {
      return (volume / 10000).toFixed(2) + '万'
    }
    return volume.toString()
  },

  async getStockDetail(code) {
    const cacheKey = `stock_${code}`
    const cached = this.getFromCache(cacheKey)
    if (cached) return cached
    
    try {
      const prefix = code.startsWith('6') ? 'sh' : 'sz'
      const response = await axios.get(`${SINA_API}${prefix}${code}`, {
        headers: {
          'Referer': 'http://finance.sina.com.cn',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000
      })
      
      const stock = this.parseSingleStock(response.data, code)
      if (stock) {
        apiErrorCount.sina = 0
        
        try {
          const basicInfo = await this.getStockBasicInfo(code)
          const result = { ...stock, ...basicInfo }
          this.setToCache(cacheKey, result)
          return result
        } catch (e) {
          console.error('获取基本面信息失败:', e.message)
          this.setToCache(cacheKey, stock)
          return stock
        }
      }
      
      throw new Error('解析股票数据失败')
    } catch (error) {
      console.error('获取股票详情失败:', error.message)
      
      try {
        const emData = await this.getStockDetailFromEastMoney(code)
        if (emData) {
          return emData
        }
      } catch (e) {
        console.error('东方财富详情也失败:', e.message)
      }
      
      return this.getFallbackStockDetail(code)
    }
  },

  async getStockDetailFromEastMoney(code) {
    const secid = code.startsWith('6') ? `1.${code}` : `0.${code}`
    
    const response = await axios.get(
      `${EAST_MONEY_API}/api/qt/stock/get?secid=${secid}&fields=f57,f58,f162,f167,f168,f169,f170,f171,f116,f117,f43,f44,f45,f46,f47,f48,f57,f58,f60`,
      {
        headers: {
          'Referer': 'http://quote.eastmoney.com/',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 10000
      }
    )
    
    if (response.data && response.data.data) {
      const d = response.data.data
      return {
        code: code,
        name: d.f58 || '未知',
        price: (d.f43 / 100).toFixed(2) || '0.00',
        change: parseFloat(d.f3) || 0,
        open: (d.f46 / 100).toFixed(2) || '0.00',
        high: (d.f44 / 100).toFixed(2) || '0.00',
        low: (d.f45 / 100).toFixed(2) || '0.00',
        volume: this.formatVolume(d.f47 / 100) || '0',
        turnover: this.formatVolume(d.f48 / 100) || '0',
        prevClose: (d[f60] / 100).toFixed(2) || '0.00',
        pe: d.f162 || '-',
        pb: d.f167 || '-',
        marketCap: d.f116 ? this.formatVolume(d.f116) : '-',
        totalValue: d.f117 ? this.formatVolume(d.f117) : '-'
      }
    }
    
    throw new Error('东方财富数据为空')
  },

  parseSingleStock(data, code) {
    if (!data || typeof data !== 'string') return null
    
    const match = data.match(/hq_str_\w+="(.+)"/)
    if (!match) return null
    
    const values = match[1].split(',')
    if (values.length < 32) return null
    
    const name = values[0]
    if (!name) return null
    
    const open = parseFloat(values[1]) || 0
    const prevClose = parseFloat(values[2]) || 0
    const current = parseFloat(values[3]) || 0
    const high = parseFloat(values[4]) || 0
    const low = parseFloat(values[5]) || 0
    const volume = parseInt(values[8]) || 0
    const amount = parseFloat(values[9]) || 0
    const change = prevClose > 0 ? parseFloat(((current - prevClose) / prevClose * 100).toFixed(2)) : 0
    
    if (current === 0) return null
    
    return {
      code: code,
      name: name,
      price: current.toFixed(2),
      change: change,
      open: open.toFixed(2),
      high: high.toFixed(2),
      low: low.toFixed(2),
      volume: this.formatVolume(volume),
      turnover: this.formatVolume(amount),
      prevClose: prevClose.toFixed(2)
    }
  },

  async getStockBasicInfo(code) {
    try {
      const secid = code.startsWith('6') ? `1.${code}` : `0.${code}`
      const response = await axios.get(
        `${EAST_MONEY_API}/api/qt/stock/get?secid=${secid}&fields=f57,f58,f162,f167,f168,f169,f170,f171,f116,f117`,
        {
          headers: {
            'Referer': 'http://quote.eastmoney.com/'
          },
          timeout: 10000
        }
      )
      
      if (response.data && response.data.data) {
        const d = response.data.data
        return {
          pe: d.f162 || '-',
          pb: d.f167 || '-',
          marketCap: d.f116 ? this.formatVolume(d.f116) : '-',
          totalValue: d.f117 ? this.formatVolume(d.f117) : '-'
        }
      }
    } catch (error) {
      console.error('获取基本面信息失败')
    }
    
    return {
      pe: '-',
      pb: '-',
      marketCap: '-',
      totalValue: '-'
    }
  },

  async getKLineData(code) {
    const cacheKey = `kline_${code}`
    const cached = this.getFromCache(cacheKey)
    if (cached) return cached
    
    try {
      const histData = await this.getHistoricalData(code)
      if (histData && histData.length > 0) {
        const result = {
          dates: histData.map(d => d.date),
          data: histData.map(d => ({
            date: d.date,
            open: d.open,
            close: d.close,
            high: d.high,
            low: d.low,
            volume: d.volume
          }))
        }
        this.setToCache(cacheKey, result, 60000)
        return result
      }
      
      throw new Error('K线数据为空')
    } catch (error) {
      console.error('获取K线数据失败:', error.message)
      apiErrorCount.eastmoney++
      return this.getFallbackKLineData()
    }
  },

  async getHistoricalData(code) {
    try {
      const begin = this.getDateBefore(90)
      const end = this.getToday()
      const secid = code.startsWith('6') ? `1.${code}` : `0.${code}`
      
      const url = `${EAST_MONEY_HIS_API}/api/qt/stock/kline/get?secid=${secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=${begin}&end=${end}&smplmt=460&lmt=1000000`
      
      const response = await axios.get(url, {
        headers: {
          'Referer': 'http://quote.eastmoney.com/',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 15000
      })
      
      if (response.data && response.data.data && response.data.data.klines) {
        apiErrorCount.eastmoney = 0
        const klines = response.data.data.klines
        return klines.map(line => {
          const parts = line.split(',')
          return {
            date: parts[0],
            open: parseFloat(parts[1]),
            close: parseFloat(parts[2]),
            high: parseFloat(parts[3]),
            low: parseFloat(parts[4]),
            volume: parseInt(parts[5])
          }
        })
      }
      
      throw new Error('K线数据格式错误')
    } catch (error) {
      console.error('获取历史数据失败:', error.message)
      throw error
    }
  },

  getToday() {
    const now = new Date()
    return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}`
  },

  getDateBefore(days) {
    const date = new Date()
    date.setDate(date.getDate() - days)
    return `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
  },

  getFromCache(key) {
    const cached = dataCache.get(key)
    if (cached && Date.now() - cached.timestamp < cached.duration) {
      return cached.data
    }
    dataCache.delete(key)
    return null
  },

  setToCache(key, data, duration = CACHE_DURATION) {
    dataCache.set(key, {
      data,
      timestamp: Date.now(),
      duration
    })
  },

  clearCache() {
    dataCache.clear()
  },

  getApiStatus() {
    return {
      sina: {
        errorCount: apiErrorCount.sina,
        status: apiErrorCount.sina < 3 ? '正常' : '异常'
      },
      eastmoney: {
        errorCount: apiErrorCount.eastmoney,
        status: apiErrorCount.eastmoney < 3 ? '正常' : '异常'
      }
    }
  },

  getFallbackStockList() {
    return [
      // 白酒行业
      { code: '600519', name: '贵州茅台', price: 1856.00, change: 3.56, volume: '15.8万', open: '1798.00', high: '1868.00', low: '1792.00', prevClose: '1792.00' },
      { code: '000858', name: '五粮液', price: 168.50, change: -1.23, volume: '89.2万', open: '170.50', high: '172.30', low: '167.80', prevClose: '170.50' },
      { code: '000568', name: '泸州老窖', price: 235.80, change: 2.15, volume: '32.5万', open: '231.00', high: '238.50', low: '230.50', prevClose: '231.00' },
      { code: '002304', name: '洋河股份', price: 145.60, change: 1.85, volume: '28.3万', open: '143.20', high: '147.80', low: '142.90', prevClose: '143.20' },
      // 银行
      { code: '600036', name: '招商银行', price: 35.80, change: 1.56, volume: '78.9万', open: '35.20', high: '36.10', low: '34.90', prevClose: '35.20' },
      { code: '601318', name: '中国平安', price: 48.25, change: -0.85, volume: '98.3万', open: '48.65', high: '49.10', low: '47.80', prevClose: '48.65' },
      { code: '601398', name: '工商银行', price: 5.12, change: 0.35, volume: '256.8万', open: '5.10', high: '5.15', low: '5.08', prevClose: '5.10' },
      { code: '601939', name: '建设银行', price: 6.85, change: 0.28, volume: '189.5万', open: '6.82', high: '6.90', low: '6.80', prevClose: '6.82' },
      { code: '000001', name: '平安银行', price: 12.35, change: 0.92, volume: '67.2万', open: '12.20', high: '12.50', low: '12.15', prevClose: '12.20' },
      { code: '601166', name: '兴业银行', price: 18.62, change: 1.15, volume: '85.6万', open: '18.40', high: '18.80', low: '18.35', prevClose: '18.40' },
      { code: '600000', name: '浦发银行', price: 8.45, change: 0.52, volume: '92.3万', open: '8.40', high: '8.55', low: '8.38', prevClose: '8.40' },
      { code: '601328', name: '交通银行', price: 4.89, change: 0.18, volume: '178.4万', open: '4.87', high: '4.92', low: '4.85', prevClose: '4.87' },
      // 保险
      { code: '601601', name: '中国太保', price: 28.65, change: -0.45, volume: '45.8万', open: '28.80', high: '29.10', low: '28.50', prevClose: '28.80' },
      { code: '601336', name: '新华保险', price: 32.50, change: -1.20, volume: '38.6万', open: '32.90', high: '33.20', low: '32.30', prevClose: '32.90' },
      { code: '000627', name: '天茂集团', price: 3.25, change: 0.85, volume: '52.3万', open: '3.22', high: '3.30', low: '3.20', prevClose: '3.22' },
      // 券商
      { code: '600030', name: '中信证券', price: 22.50, change: 1.85, volume: '112.5万', open: '22.10', high: '22.80', low: '22.00', prevClose: '22.10' },
      { code: '601211', name: '国泰君安', price: 15.62, change: 1.25, volume: '78.9万', open: '15.40', high: '15.80', low: '15.35', prevClose: '15.40' },
      { code: '601688', name: '华泰证券', price: 16.85, change: 1.68, volume: '95.2万', open: '16.55', high: '17.05', low: '16.50', prevClose: '16.55' },
      { code: '000776', name: '广发证券', price: 16.25, change: 2.05, volume: '68.7万', open: '15.90', high: '16.45', low: '15.85', prevClose: '15.90' },
      { code: '600837', name: '海通证券', price: 11.85, change: 1.35, volume: '102.4万', open: '11.65', high: '11.95', low: '11.60', prevClose: '11.65' },
      { code: '600958', name: '东方证券', price: 9.85, change: 0.95, volume: '56.8万', open: '9.75', high: '9.95', low: '9.72', prevClose: '9.75' },
      { code: '002736', name: '国信证券', price: 10.25, change: 1.15, volume: '48.6万', open: '10.10', high: '10.35', low: '10.05', prevClose: '10.10' },
      // 科技成长
      { code: '300750', name: '宁德时代', price: 218.60, change: 4.12, volume: '56.7万', open: '210.00', high: '221.50', low: '208.50', prevClose: '210.00' },
      { code: '002594', name: '比亚迪', price: 258.90, change: 5.21, volume: '67.5万', open: '246.50', high: '262.80', low: '245.20', prevClose: '246.50' },
      { code: '601012', name: '隆基绿能', price: 28.65, change: 3.25, volume: '125.8万', open: '27.75', high: '29.10', low: '27.60', prevClose: '27.75' },
      { code: '603986', name: '兆易创新', price: 128.50, change: 2.85, volume: '35.6万', open: '125.00', high: '130.20', low: '124.50', prevClose: '125.00' },
      { code: '002415', name: '海康威视', price: 35.80, change: 1.95, volume: '82.3万', open: '35.10', high: '36.25', low: '35.00', prevClose: '35.10' },
      { code: '600745', name: '闻泰科技', price: 58.25, change: 2.45, volume: '42.8万', open: '56.80', high: '59.10', low: '56.50', prevClose: '56.80' },
      { code: '300059', name: '东方财富', price: 18.65, change: 2.15, volume: '185.6万', open: '18.25', high: '18.95', low: '18.20', prevClose: '18.25' },
      { code: '688111', name: '金山办公', price: 358.60, change: 3.65, volume: '12.5万', open: '346.00', high: '362.80', low: '345.20', prevClose: '346.00' },
      // 医药
      { code: '600276', name: '恒瑞医药', price: 48.65, change: 1.85, volume: '58.9万', open: '47.75', high: '49.20', low: '47.60', prevClose: '47.75' },
      { code: '603259', name: '药明康德', price: 85.60, change: 2.25, volume: '32.5万', open: '83.70', high: '86.80', low: '83.50', prevClose: '83.70' },
      { code: '300015', name: '爱尔眼科', price: 32.50, change: 1.65, volume: '65.8万', open: '31.95', high: '33.00', low: '31.85', prevClose: '31.95' },
      { code: '000538', name: '云南白药', price: 58.25, change: 0.85, volume: '28.6万', open: '57.80', high: '58.80', low: '57.70', prevClose: '57.80' },
      { code: '600196', name: '复星医药', price: 32.85, change: 1.35, volume: '45.8万', open: '32.40', high: '33.20', low: '32.30', prevClose: '32.40' },
      { code: '002007', name: '华兰生物', price: 22.60, change: 1.15, volume: '35.2万', open: '22.35', high: '22.90', low: '22.30', prevClose: '22.35' },
      { code: '600329', name: '中新药业', price: 28.50, change: 0.95, volume: '22.5万', open: '28.25', high: '28.85', low: '28.20', prevClose: '28.25' },
      // 消费家电
      { code: '000333', name: '美的集团', price: 62.85, change: 1.75, volume: '68.5万', open: '61.75', high: '63.50', low: '61.60', prevClose: '61.75' },
      { code: '000651', name: '格力电器', price: 38.65, change: 1.25, volume: '75.8万', open: '38.15', high: '39.10', low: '38.05', prevClose: '38.15' },
      { code: '600690', name: '海尔智家', price: 26.85, change: 1.45, volume: '58.6万', open: '26.45', high: '27.15', low: '26.40', prevClose: '26.45' },
      { code: '000100', name: 'TCL科技', price: 4.25, change: 1.85, volume: '125.8万', open: '4.17', high: '4.32', low: '4.15', prevClose: '4.17' },
      { code: '600887', name: '伊利股份', price: 28.60, change: 0.85, volume: '52.3万', open: '28.35', high: '28.90', low: '28.30', prevClose: '28.35' },
      { code: '002032', name: '苏泊尔', price: 52.80, change: 1.15, volume: '18.5万', open: '52.20', high: '53.40', low: '52.10', prevClose: '52.20' },
      { code: '600618', name: '氯碱化工', price: 12.85, change: 2.25, volume: '38.6万', open: '12.55', high: '13.05', low: '12.50', prevClose: '12.55' },
      // 房地产
      { code: '000002', name: '万科A', price: 18.95, change: -2.15, volume: '134.2万', open: '19.35', high: '19.45', low: '18.75', prevClose: '19.35' },
      { code: '600048', name: '保利发展', price: 15.62, change: -1.25, volume: '95.6万', open: '15.82', high: '15.90', low: '15.45', prevClose: '15.82' },
      { code: '600383', name: '金地集团', price: 10.25, change: -0.85, volume: '68.5万', open: '10.35', high: '10.45', low: '10.15', prevClose: '10.35' },
      { code: '001979', name: '招商蛇口', price: 12.85, change: -1.05, volume: '45.8万', open: '12.98', high: '13.10', low: '12.70', prevClose: '12.98' },
      { code: '601155', name: '新城控股', price: 22.60, change: -1.85, volume: '52.3万', open: '23.05', high: '23.20', low: '22.40', prevClose: '23.05' },
      { code: '600606', name: '绿地控股', price: 3.85, change: -0.52, volume: '78.6万', open: '3.90', high: '3.95', low: '3.82', prevClose: '3.90' },
      { code: '000402', name: '金融街', price: 6.85, change: -0.65, volume: '35.8万', open: '6.92', high: '7.00', low: '6.80', prevClose: '6.92' },
      // 新能源
      { code: '600900', name: '长江电力', price: 22.85, change: 0.65, volume: '45.6万', open: '22.70', high: '23.10', low: '22.65', prevClose: '22.70' },
      { code: '600905', name: '三峡能源', price: 6.25, change: 1.45, volume: '125.8万', open: '6.15', high: '6.35', low: '6.12', prevClose: '6.15' },
      { code: '002459', name: '晶澳科技', price: 35.60, change: 2.85, volume: '58.3万', open: '34.60', high: '36.10', low: '34.50', prevClose: '34.60' },
      { code: '300014', name: '亿纬锂能', price: 68.50, change: 3.15, volume: '62.5万', open: '66.40', high: '69.50', low: '66.20', prevClose: '66.40' },
      { code: '601615', name: '明阳智能', price: 22.85, change: 2.25, volume: '48.6万', open: '22.35', high: '23.20', low: '22.25', prevClose: '22.35' },
      { code: '002129', name: '中环股份', price: 42.60, change: 2.65, volume: '72.8万', open: '41.50', high: '43.25', low: '41.40', prevClose: '41.50' },
      { code: '600438', name: '通威股份', price: 38.65, change: 3.25, volume: '95.6万', open: '37.45', high: '39.20', low: '37.30', prevClose: '37.45' },
      // 基建制造
      { code: '601668', name: '中国建筑', price: 5.85, change: 0.85, volume: '185.6万', open: '5.80', high: '5.92', low: '5.78', prevClose: '5.80' },
      { code: '601186', name: '中国铁建', price: 8.65, change: 0.95, volume: '98.5万', open: '8.55', high: '8.75', low: '8.52', prevClose: '8.55' },
      { code: '601390', name: '中国中铁', price: 6.85, change: 1.05, volume: '125.8万', open: '6.78', high: '6.95', low: '6.75', prevClose: '6.78' },
      { code: '002048', name: '宁波华翔', price: 15.60, change: 1.25, volume: '28.5万', open: '15.40', high: '15.80', low: '15.35', prevClose: '15.40' },
      { code: '600031', name: '三一重工', price: 18.25, change: 2.15, volume: '125.6万', open: '17.85', high: '18.55', low: '17.80', prevClose: '17.85' },
      { code: '000425', name: '徐工机械', price: 6.85, change: 1.45, volume: '158.6万', open: '6.75', high: '6.95', low: '6.72', prevClose: '6.75' },
      { code: '600170', name: '上海建工', price: 3.25, change: 0.68, volume: '92.5万', open: '3.22', high: '3.30', low: '3.20', prevClose: '3.22' },
      // 通信电子
      { code: '600941', name: '中国移动', price: 98.60, change: 1.25, volume: '35.8万', open: '97.40', high: '99.20', low: '97.25', prevClose: '97.40' },
      { code: '601728', name: '中国电信', price: 6.25, change: 0.85, volume: '125.6万', open: '6.20', high: '6.32', low: '6.18', prevClose: '6.20' },
      { code: '600050', name: '中国联通', price: 4.85, change: 1.25, volume: '185.6万', open: '4.79', high: '4.90', low: '4.77', prevClose: '4.79' },
      { code: '000063', name: '中兴通讯', price: 35.60, change: 2.45, volume: '72.5万', open: '34.75', high: '36.10', low: '34.65', prevClose: '34.75' },
      { code: '002241', name: '歌尔股份', price: 22.85, change: 1.85, volume: '85.6万', open: '22.40', high: '23.15', low: '22.35', prevClose: '22.40' },
      { code: '603160', name: '汇顶科技', price: 85.60, change: 2.65, volume: '25.8万', open: '83.40', high: '86.50', low: '83.25', prevClose: '83.40' },
      { code: '300033', name: '同花顺', price: 125.60, change: 3.25, volume: '32.5万', open: '121.60', high: '127.80', low: '121.30', prevClose: '121.60' },
      // 化工材料
      { code: '600309', name: '万华化学', price: 92.50, change: 1.85, volume: '42.8万', open: '90.80', high: '93.50', low: '90.65', prevClose: '90.80' },
      { code: '601216', name: '君正集团', price: 5.85, change: 0.95, volume: '78.6万', open: '5.78', high: '5.92', low: '5.75', prevClose: '5.78' },
      { code: '002601', name: '龙蟒佰利', price: 28.60, change: 1.35, volume: '45.6万', open: '28.20', high: '28.95', low: '28.15', prevClose: '28.20' },
      { code: '600989', name: '宝丰能源', price: 12.85, change: 1.15, volume: '62.5万', open: '12.70', high: '13.00', low: '12.68', prevClose: '12.70' },
      { code: '002092', name: '中泰化学', price: 8.65, change: 1.05, volume: '58.3万', open: '8.55', high: '8.75', low: '8.52', prevClose: '8.55' },
      { code: '600486', name: '扬农化工', price: 85.60, change: 1.65, volume: '18.5万', open: '84.20', high: '86.50', low: '84.10', prevClose: '84.20' },
      { code: '600596', name: '新安股份', price: 15.80, change: 1.25, volume: '42.6万', open: '15.60', high: '16.00', low: '15.55', prevClose: '15.60' },
      // 军工
      { code: '600893', name: '航发动力', price: 42.60, change: 2.85, volume: '52.5万', open: '41.40', high: '43.20', low: '41.30', prevClose: '41.40' },
      { code: '000733', name: '振华科技', price: 65.80, change: 2.15, volume: '28.6万', open: '64.40', high: '66.80', low: '64.25', prevClose: '64.40' },
      { code: '600760', name: '中航沈飞', price: 58.50, change: 3.25, volume: '38.5万', open: '56.65', high: '59.30', low: '56.50', prevClose: '56.65' },
      { code: '002013', name: '中航机电', price: 12.85, change: 1.85, volume: '68.6万', open: '12.60', high: '13.05', low: '12.55', prevClose: '12.60' },
      { code: '601989', name: '中国重工', price: 4.25, change: 1.25, volume: '125.8万', open: '4.20', high: '4.32', low: '4.18', prevClose: '4.20' },
      { code: '002025', name: '航天电器', price: 72.50, change: 1.95, volume: '22.5万', open: '71.10', high: '73.50', low: '71.00', prevClose: '71.10' },
      { code: '600862', name: '中航高科', price: 28.60, change: 2.15, volume: '35.8万', open: '28.00', high: '29.00', low: '27.95', prevClose: '28.00' },
      // 食品饮料
      { code: '600132', name: '重庆啤酒', price: 118.60, change: 1.45, volume: '12.5万', open: '116.80', high: '120.20', low: '116.65', prevClose: '116.80' },
      { code: '000895', name: '双汇发展', price: 28.65, change: 0.85, volume: '42.8万', open: '28.40', high: '28.90', low: '28.35', prevClose: '28.40' },
      { code: '600597', name: '光明乳业', price: 11.85, change: 0.95, volume: '35.6万', open: '11.75', high: '11.98', low: '11.72', prevClose: '11.75' },
      { code: '002714', name: '牧原股份', price: 52.80, change: 2.25, volume: '68.5万', open: '51.60', high: '53.50', low: '51.50', prevClose: '51.60' },
      { code: '600300', name: '维维股份', price: 3.85, change: 0.65, volume: '45.6万', open: '3.82', high: '3.90', low: '3.80', prevClose: '3.82' },
      { code: '002507', name: '涪陵榨菜', price: 28.50, change: 1.15, volume: '25.8万', open: '28.15', high: '28.85', low: '28.10', prevClose: '28.15' },
      { code: '603288', name: '海天味业', price: 68.60, change: 1.25, volume: '18.5万', open: '67.75', high: '69.30', low: '67.65', prevClose: '67.75' },
      // 汽车
      { code: '600104', name: '上汽集团', price: 15.85, change: 0.95, volume: '85.6万', open: '15.70', high: '16.05', low: '15.68', prevClose: '15.70' },
      { code: '000625', name: '长安汽车', price: 12.60, change: 2.15, volume: '125.6万', open: '12.35', high: '12.80', low: '12.30', prevClose: '12.35' },
      { code: '601127', name: '赛力斯', price: 72.50, change: 3.65, volume: '58.3万', open: '69.95', high: '73.50', low: '69.80', prevClose: '69.95' },
      { code: '002126', name: '银轮股份', price: 18.65, change: 1.85, volume: '35.6万', open: '18.30', high: '18.90', low: '18.25', prevClose: '18.30' },
      { code: '600742', name: '一汽富维', price: 8.85, change: 0.85, volume: '28.5万', open: '8.78', high: '8.95', low: '8.75', prevClose: '8.78' },
      // 半导体
      { code: '688981', name: '中芯国际', price: 52.60, change: 3.15, volume: '85.6万', open: '51.00', high: '53.40', low: '50.85', prevClose: '51.00' },
      { code: '002371', name: '北方华创', price: 328.50, change: 4.25, volume: '22.5万', open: '315.00', high: '333.50', low: '314.50', prevClose: '315.00' },
      { code: '603501', name: '韦尔股份', price: 92.80, change: 2.85, volume: '38.6万', open: '90.20', high: '94.10', low: '90.05', prevClose: '90.20' },
      { code: '688008', name: '澜起科技', price: 65.80, change: 2.45, volume: '25.8万', open: '64.20', high: '66.70', low: '64.10', prevClose: '64.20' },
      { code: '300782', name: '卓胜微', price: 128.60, change: 3.25, volume: '18.5万', open: '124.50', high: '130.50', low: '124.30', prevClose: '124.50' },
      { code: '600584', name: '长电科技', price: 28.65, change: 1.95, volume: '62.5万', open: '28.10', high: '29.05', low: '28.05', prevClose: '28.10' },
      { code: '002156', name: '通富微电', price: 22.80, change: 1.65, volume: '52.6万', open: '22.40', high: '23.10', low: '22.35', prevClose: '22.40' },
      // 互联网科技
      { code: '600570', name: '恒生电子', price: 58.60, change: 2.15, volume: '42.5万', open: '57.40', high: '59.40', low: '57.30', prevClose: '57.40' },
      { code: '600588', name: '用友网络', price: 22.85, change: 1.85, volume: '58.6万', open: '22.40', high: '23.15', low: '22.35', prevClose: '22.40' },
      { code: '002410', name: '广联达', price: 48.60, change: 2.25, volume: '32.5万', open: '47.50', high: '49.20', low: '47.45', prevClose: '47.50' },
      { code: '600184', name: '光电股份', price: 12.85, change: 1.45, volume: '25.8万', open: '12.65', high: '13.02', low: '12.62', prevClose: '12.65' },
      { code: '002230', name: '科大讯飞', price: 52.80, change: 2.85, volume: '65.8万', open: '51.30', high: '53.50', low: '51.20', prevClose: '51.30' },
      { code: '600718', name: '东软集团', price: 12.60, change: 1.35, volume: '35.6万', open: '12.42', high: '12.78', low: '12.40', prevClose: '12.42' }
    ]
  },

  getFallbackStockDetail(code) {
    const stocks = this.getFallbackStockList()
    const stock = stocks.find(s => s.code === code) || stocks[0]
    
    return {
      ...stock,
      turnover: '1578万',
      pe: Math.floor(Math.random() * 50 + 10),
      pb: (Math.random() * 5 + 1).toFixed(2),
      marketCap: '-',
      totalValue: '-'
    }
  },

  getFallbackKLineData() {
    const dates = []
    const data = []
    let basePrice = 10.0
    
    for (let i = 60; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      dates.push(`${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`)
      
      const open = basePrice + (Math.random() - 0.5) * 0.5
      const close = open + (Math.random() - 0.5) * 0.8
      const high = Math.max(open, close) + Math.random() * 0.3
      const low = Math.min(open, close) - Math.random() * 0.3
      
      data.push({
        date: dates[dates.length - 1],
        open: parseFloat(open.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        volume: Math.floor(Math.random() * 500000 + 100000)
      })
      
      basePrice = close
    }
    
    return { dates, data }
  }
}
