import * as fs from 'fs'
import * as path from 'path'
import { Config } from './types'

const CONFIG_PATH = path.join(__dirname, '../config.json')

const DEFAULT_CONFIG: Config = {
  tushare: {
    token: '',
    enabled: true
  },
  data: {
    cacheDir: path.join(__dirname, '../data/cache'),
    useTushare: true
  }
}

export class ConfigManager {
  private config: Config

  constructor() {
    this.config = this.loadConfig()
  }

  private loadConfig(): Config {
    if (fs.existsSync(CONFIG_PATH)) {
      try {
        const content = fs.readFileSync(CONFIG_PATH, 'utf-8')
        const loaded = JSON.parse(content)
        return { ...DEFAULT_CONFIG, ...loaded }
      } catch (error) {
        console.error('加载配置文件失败，使用默认配置:', error)
        return DEFAULT_CONFIG
      }
    }
    return DEFAULT_CONFIG
  }

  saveConfig(): void {
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(this.config, null, 2))
  }

  getConfig(): Config {
    return this.config
  }

  getTushareToken(): string {
    return this.config.tushare.token
  }

  setTushareToken(token: string): void {
    this.config.tushare.token = token
    this.saveConfig()
  }

  isTushareEnabled(): boolean {
    return this.config.tushare.enabled
  }

  useTushare(): boolean {
    return this.config.data.useTushare
  }
}

export const configManager = new ConfigManager()
