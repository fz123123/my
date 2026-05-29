import sys
sys.dont_write_bytecode = True
import sqlite3

conn = sqlite3.connect('data/market_data.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM stock_daily')
total = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(DISTINCT symbol) FROM stock_daily')
stocks = cursor.fetchone()[0]

print("="*60)
print("数据库统计")
print("="*60)
print(f"总记录数: {total:,}")
print(f"股票数量: {stocks}")
print()

if total > 0:
    cursor.execute('SELECT symbol, COUNT(*) as cnt FROM stock_daily GROUP BY symbol ORDER BY cnt DESC LIMIT 5')
    top5 = cursor.fetchall()
    print("前5只股票数据量:")
    for s, c in top5:
        print(f"  {s}: {c} 条记录")

    cursor.execute('SELECT symbol FROM stock_daily GROUP BY symbol LIMIT 10')
    sample = cursor.fetchall()
    print("\n样本股票代码:")
    for s, in sample:
        print(f"  {s}")
else:
    print("⚠️ 数据库中没有数据！")

conn.close()
