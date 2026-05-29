import * as readline from 'readline'
import * as fs from 'fs'
import * as path from 'path'

const CONFIG_PATH = path.join(__dirname, '../config.json')

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
})

function question(prompt: string): Promise<string> {
  return new Promise(resolve => {
    rl.question(prompt, resolve)
  })
}

async function setup() {
  console.log('=== Tushare 配置设置 ===\n')

  let currentToken = ''
  if (fs.existsSync(CONFIG_PATH)) {
    try {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'))
      currentToken = config.tushare?.token || ''
    } catch {}
  }
  
  console.log(`当前Token: ${currentToken ? '已设置' : '未设置'}\n`)

  const newToken = await question('请输入你的Tushare Token: ')

  if (newToken.trim()) {
    const config = {
      tushare: {
        token: newToken.trim(),
        enabled: true
      },
      data: {
        cacheDir: "./data/cache",
        useTushare: true
      }
    }
    
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2))
    console.log('\n✅ Token已保存！')
    console.log(`\n配置文件位置: ${CONFIG_PATH}`)
    console.log('\n🎉 现在你可以运行 `npm run t1` 来使用真实数据进行回测！')
  } else {
    console.log('\n未输入Token，保持当前配置。')
  }

  rl.close()
}

setup().catch(console.error)
