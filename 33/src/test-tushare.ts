import { TushareClient } from './data/TushareClient'
import { configManager } from './config'

async function testTushare() {
  console.log('=== Tushare 接口测试 ===\n')

  const token = configManager.getTushareToken()
  const useTushare = configManager.useTushare()
  
  if (!token || !useTushare) {
    console.log('⚠️  当前配置为模拟数据模式')
    console.log('📝 若要使用真实数据，请：')
    console.log('   1. 访问 https://tushare.pro/ 获取Token')
    console.log('   2. 运行 `npm run setup` 配置Token')
    console.log('   3. 或手动编辑 config.json')
    console.log('\n✅ 系统将使用模拟数据运行')
    return
  }

  console.log('✅ Token已配置\n')

  try {
    const client = new TushareClient(token)
    
    console.log('📊 测试获取股票列表...')
    const stocks = await client.getStockList()
    console.log(`✅ 获取成功，共 ${stocks.length} 只股票\n`)
    
    console.log('📈 测试获取日线数据（000001.SZ）...')
    const data = await client.getDailyData('000001.SZ', '20240101', '20240331')
    
    if (data.length > 0) {
      console.log(`✅ 获取成功，共 ${data.length} 个交易日`)
      console.log('📅 前3条数据:')
      data.slice(0, 3).forEach((bar, i) => {
        const date = new Date(bar.timestamp).toLocaleDateString('zh-CN')
        console.log(`   ${i + 1}. ${date} - 开盘:${bar.open} 最高:${bar.high} 最低:${bar.low} 收盘:${bar.close} 成交量:${bar.volume}`)
      })
    } else {
      console.log('⚠️ 没有获取到数据')
    }

    console.log('\n🎉 测试完成！Tushare接口正常工作！')

  } catch (error: any) {
    console.error('\n❌ Tushare接口测试失败:', error.message || error)
    console.log('\n💡 请检查：')
    console.log('  1. Token是否正确')
    console.log('  2. 网络连接是否正常')
    console.log('  3. Tushare账号是否有足够积分')
    console.log('\n📝 如需使用模拟数据，请将 config.json 中的 useTushare 设置为 false')
  }
}

testTushare().catch(console.error)
