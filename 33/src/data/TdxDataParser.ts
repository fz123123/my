import * as fs from 'fs'
import * as path from 'path'
import { BarData } from '../types'

export class TdxDataParser {
  static parseCSV(filePath: string): BarData[] {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n').filter(line => line.trim())
    
    const data: BarData[] = []
    let headerSkipped = false
    
    for (const line of lines) {
      if (!headerSkipped) {
        if (line.includes('日期') || line.includes('DATE') || line.includes('timestamp')) {
          headerSkipped = true
          continue
        }
      }
      
      const parts = line.split(/[,;\s\t]+/).filter(p => p.trim())
      
      if (parts.length >= 6) {
        try {
          let dateStr = parts[0].trim()
          let timestamp: number
          
          if (dateStr.includes('/')) {
            const [month, day, year] = dateStr.split('/').map(Number)
            timestamp = new Date(year + 2000, month - 1, day).getTime()
          } else if (dateStr.includes('-')) {
            timestamp = new Date(dateStr).getTime()
          } else if (/^\d{8}$/.test(dateStr)) {
            const year = parseInt(dateStr.substring(0, 4))
            const month = parseInt(dateStr.substring(4, 6)) - 1
            const day = parseInt(dateStr.substring(6, 8))
            timestamp = new Date(year, month, day).getTime()
          } else {
            timestamp = new Date(dateStr).getTime()
          }
          
          const bar: BarData = {
            timestamp,
            open: parseFloat(parts[1].trim()),
            high: parseFloat(parts[2].trim()),
            low: parseFloat(parts[3].trim()),
            close: parseFloat(parts[4].trim()),
            volume: parseInt(parts[5].trim()) || 0
          }
          
          data.push(bar)
        } catch (error) {
          console.warn(`解析行失败: ${line}`, error)
        }
      }
    }
    
    return data.sort((a, b) => a.timestamp - b.timestamp)
  }

  static parseTXT(filePath: string): BarData[] {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n').filter(line => line.trim())
    
    const data: BarData[] = []
    
    for (const line of lines) {
      const parts = line.split(/\s+/).filter(p => p.trim())
      
      if (parts.length >= 7) {
        try {
          const dateStr = parts[0].trim()
          let timestamp: number
          
          if (/^\d{8}$/.test(dateStr)) {
            const year = parseInt(dateStr.substring(0, 4))
            const month = parseInt(dateStr.substring(4, 6)) - 1
            const day = parseInt(dateStr.substring(6, 8))
            timestamp = new Date(year, month, day).getTime()
          } else {
            timestamp = new Date(dateStr).getTime()
          }
          
          const bar: BarData = {
            timestamp,
            open: parseFloat(parts[1].trim()),
            high: parseFloat(parts[2].trim()),
            low: parseFloat(parts[3].trim()),
            close: parseFloat(parts[4].trim()),
            volume: parseInt(parts[5].trim()) || parseInt(parts[6].trim()) || 0
          }
          
          data.push(bar)
        } catch (error) {
          console.warn(`解析行失败: ${line}`, error)
        }
      }
    }
    
    return data.sort((a, b) => a.timestamp - b.timestamp)
  }

  static parseDirectory(directory: string): Record<string, BarData[]> {
    const result: Record<string, BarData[]> = {}
    const files = fs.readdirSync(directory)
    
    for (const file of files) {
      const filePath = path.join(directory, file)
      const ext = path.extname(file).toLowerCase()
      const symbol = path.basename(file, ext).toUpperCase()
      
      if (ext === '.csv') {
        result[symbol] = this.parseCSV(filePath)
      } else if (ext === '.txt') {
        result[symbol] = this.parseTXT(filePath)
      }
    }
    
    return result
  }

  static exportToBarDataFormat(data: BarData[], outputPath: string): void {
    const lines = []
    lines.push('date,open,high,low,close,volume')
    
    for (const bar of data) {
      const date = new Date(bar.timestamp).toISOString().split('T')[0]
      lines.push(`${date},${bar.open},${bar.high},${bar.low},${bar.close},${bar.volume}`)
    }
    
    fs.writeFileSync(outputPath, lines.join('\n'))
  }
}
