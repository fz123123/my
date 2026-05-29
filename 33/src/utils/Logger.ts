export class Logger {
  static info(message: string, data?: any): void {
    const timestamp = new Date().toISOString()
    let logMessage = `[INFO] ${timestamp} - ${message}`
    if (data) {
      logMessage += '\n' + JSON.stringify(data, null, 2)
    }
    console.log(logMessage)
  }

  static warn(message: string, data?: any): void {
    const timestamp = new Date().toISOString()
    let logMessage = `[WARN] ${timestamp} - ${message}`
    if (data) {
      logMessage += '\n' + JSON.stringify(data, null, 2)
    }
    console.warn(logMessage)
  }

  static error(message: string, error?: Error): void {
    const timestamp = new Date().toISOString()
    let logMessage = `[ERROR] ${timestamp} - ${message}`
    if (error) {
      logMessage += '\n' + error.stack
    }
    console.error(logMessage)
  }

  static success(message: string, data?: any): void {
    const timestamp = new Date().toISOString()
    let logMessage = `[SUCCESS] ${timestamp} - ${message}`
    if (data) {
      logMessage += '\n' + JSON.stringify(data, null, 2)
    }
    console.log('\x1b[32m' + logMessage + '\x1b[0m')
  }
}
