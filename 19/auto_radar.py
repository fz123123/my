from datetime import datetime
from stock_data import fetch_all_stocks
from radar import LimitUpRadar
import os

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, f'radar_{datetime.now().strftime("%Y%m%d")}.log')

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry.strip())
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def run_auto_scan():
    log_message("=" * 60)
    log_message("涨停雷达自动扫描任务启动")
    log_message("=" * 60)
    
    try:
        radar = LimitUpRadar()
        log_message("正在获取股票数据...")
        
        stocks = fetch_all_stocks()
        
        if stocks.empty:
            log_message("获取股票数据失败")
            return False
        
        log_message(f"成功获取 {len(stocks)} 只股票数据")
        
        limit_up = radar.detect_limit_up(stocks)
        analysis = radar.analyze_limit_up_stocks(limit_up)
        
        log_message(f"\n检测到 {len(analysis)} 只涨停股票")
        
        if analysis:
            log_message("\n涨停股票列表:")
            for i, stock in enumerate(analysis[:20], 1):
                log_message(f"{i:2d}. [{stock['code']}] {stock['name']:<8s} "
                          f"{stock['price']:>8.2f}元 涨幅:{stock['change_pct']:>6.2f}%  "
                          f"换手率:{stock['turnover_rate']:>6.2f}% 风险:{stock['risk_level']}")
            
            if len(analysis) > 20:
                log_message(f"... 还有 {len(analysis) - 20} 只涨停股票")
        
        radar.save_history(analysis, datetime.now())
        
        risk_summary = {'高风险': 0, '中风险': 0, '低风险': 0}
        for stock in analysis:
            risk_summary[stock['risk_level']] += 1
        
        log_message(f"\n风险分布: 高风险:{risk_summary['高风险']}只 "
                   f"中风险:{risk_summary['中风险']}只 低风险:{risk_summary['低风险']}只")
        
        log_message("\n" + "=" * 60)
        log_message("涨停雷达自动扫描任务完成")
        log_message("=" * 60)
        
        return True
        
    except Exception as e:
        log_message(f"扫描过程中出错: {e}")
        return False

if __name__ == '__main__':
    success = run_auto_scan()
    exit(0 if success else 1)
