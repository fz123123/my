# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime
import json
import sys
import os
from pathlib import Path
from io import BytesIO

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ReportGenerator:
    def __init__(self):
        self.report_dir = Path(__file__).parent.parent / 'data' / 'reports'
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_html_report(self, backtest_result, df, signals, symbol, strategy_name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{symbol}_{strategy_name}_{timestamp}.html"
        filepath = self.report_dir / filename
        
        html_content = self._create_html_template(backtest_result, df, signals, symbol, strategy_name)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _create_html_template(self, backtest_result, df, signals, symbol, strategy_name):
        equity_df = backtest_result.get('equity_curve')
        
        returns_json = self._prepare_chart_data(equity_df, df)
        trades_json = self._prepare_trades_data(backtest_result.get('trades', []))
        
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>閲忓寲鍥炴祴鎶ュ憡 - {symbol} {strategy_name}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .metric-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #2c3e50;
        }}
        .trades-table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .trades-table th {{
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
        }}
        .trades-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .trades-table tr:hover {{
            background: #f8f9fa;
        }}
        .buy {{ color: #27ae60; font-weight: bold; }}
        .sell {{ color: #e74c3c; font-weight: bold; }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>馃搳 閲忓寲鍥炴祴鎶ュ憡</h1>
        <p><strong>鏍囩殑:</strong> {symbol} | <strong>绛栫暐:</strong> {strategy_name}</p>
        <p><strong>鐢熸垚鏃堕棿:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value {'positive' if backtest_result['total_return_pct'] > 0 else 'negative'}">
                {backtest_result['total_return_pct']:+.2f}%
            </div>
            <div class="metric-label">鎬绘敹鐩婄巼</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">
                {backtest_result['sharpe_ratio']:.2f}
            </div>
            <div class="metric-label">澶忔櫘姣旂巼</div>
        </div>
        <div class="metric-card">
            <div class="metric-value negative">
                {backtest_result['max_drawdown_pct']:.2f}%
            </div>
            <div class="metric-label">鏈€澶у洖鎾?/div>
        </div>
        <div class="metric-card">
            <div class="metric-value">
                {backtest_result['win_rate_pct']:.2f}%
            </div>
            <div class="metric-label">鑳滅巼</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">
                {backtest_result['total_trades']}
            </div>
            <div class="metric-label">浜ゆ槗娆℃暟</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">
                {backtest_result.get('final_equity', 0):,.2f}
            </div>
            <div class="metric-label">鏈€缁堣祫閲?/div>
        </div>
    </div>

    <div class="chart-container">
        <h2 class="section-title">馃搱 鏉冪泭鏇茬嚎</h2>
        <div id="equity-chart"></div>
    </div>

    <div class="chart-container">
        <h2 class="section-title">馃搲 鍥炴挙鍒嗘瀽</h2>
        <div id="drawdown-chart"></div>
    </div>

    <div class="chart-container">
        <h2 class="section-title">馃捁 浠锋牸璧板娍涓庝氦鏄撲俊鍙?/h2>
        <div id="price-chart"></div>
    </div>

    <div class="chart-container">
        <h2 class="section-title">馃搵 浜ゆ槗璁板綍</h2>
        <table class="trades-table">
            <thead>
                <tr>
                    <th>鏃ユ湡</th>
                    <th>绫诲瀷</th>
                    <th>浠锋牸</th>
                    <th>鏁伴噺</th>
                    <th>閲戦</th>
                </tr>
            </thead>
            <tbody>
                {self._generate_trades_table(backtest_result.get('trades', []))}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>閲忓瓙閲忓寲骞冲彴 Pro | QuantumQuant Pro</p>
        <p>Generated by Quantum Trading System</p>
    </div>

    <script>
        var returnsData = {returns_json};
        var tradesData = {trades_json};
        
        Plotly.newPlot('equity-chart', [{
            x: returnsData.dates,
            y: returnsData.equity,
            type: 'scatter',
            mode: 'lines',
            name: '鏉冪泭',
            line: {{color: '#3498db', width: 2}}
        }}], {{
            title: '鏉冪泭鏇茬嚎',
            xaxis: {{title: '鏃ユ湡'}},
            yaxis: {{title: '閲戦'}},
            responsive: true
        }});

        Plotly.newPlot('drawdown-chart', [{
            x: returnsData.dates,
            y: returnsData.drawdown,
            type: 'scatter',
            mode: 'lines',
            name: '鍥炴挙',
            fill: 'tozeroy',
            fillcolor: 'rgba(231, 76, 60, 0.3)',
            line: {{color: '#e74c3c', width: 1}}
        }}], {{
            title: '鍥炴挙鏇茬嚎',
            xaxis: {{title: '鏃ユ湡'}},
            yaxis: {{title: '鍥炴挙 (%)'}},
            responsive: true
        }});
    </script>
</body>
</html>
"""
        return html
    
    def _prepare_chart_data(self, equity_df, price_df):
        if equity_df is None or len(equity_df) == 0:
            return {'dates': [], 'equity': [], 'drawdown': []}
        
        dates = equity_df.index.strftime('%Y-%m-%d').tolist()
        equity = equity_df['equity'].tolist()
        
        running_max = pd.Series(equity).expanding().max()
        drawdown = [(e - m) / m * 100 for e, m in zip(equity, running_max)]
        
        return {
            'dates': dates,
            'equity': equity,
            'drawdown': drawdown
        }
    
    def _prepare_trades_data(self, trades):
        if not trades:
            return []
        
        return [
            {
                'date': str(t['date']),
                'type': t['type'],
                'price': t['price'],
                'shares': t['shares'],
                'value': t['value']
            }
            for t in trades
        ]
    
    def _generate_trades_table(self, trades):
        if not trades:
            return '<tr><td colspan="5">鏆傛棤浜ゆ槗璁板綍</td></tr>'
        
        rows = []
        for trade in trades:
            trade_type_class = 'buy' if trade['type'] == 'buy' else 'sell'
            trade_type_text = '涔板叆' if trade['type'] == 'buy' else '鍗栧嚭'
            
            rows.append(f"""
                <tr>
                    <td>{pd.to_datetime(trade['date']).strftime('%Y-%m-%d')}</td>
                    <td class="{trade_type_class}">{trade_type_text}</td>
                    <td>{trade['price']:.2f}</td>
                    <td>{trade['shares']}</td>
                    <td>{trade['value']:,.2f}</td>
                </tr>
            """)
        
        return '\n'.join(rows)
    
    def generate_json_report(self, backtest_result, symbol, strategy_name):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{symbol}_{strategy_name}_{timestamp}.json"
        filepath = self.report_dir / filename
        
        report = {
            'metadata': {
                'symbol': symbol,
                'strategy': strategy_name,
                'generated_at': datetime.now().isoformat(),
                'report_version': '1.0'
            },
            'summary': {
                'total_return_pct': backtest_result['total_return_pct'],
                'sharpe_ratio': backtest_result['sharpe_ratio'],
                'max_drawdown_pct': backtest_result['max_drawdown_pct'],
                'win_rate_pct': backtest_result['win_rate_pct'],
                'total_trades': backtest_result['total_trades'],
                'final_equity': backtest_result.get('final_equity', 0)
            },
            'trades': backtest_result.get('trades', []),
            'equity_curve': backtest_result.get('equity_curve', pd.DataFrame()).to_dict()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        return str(filepath)
    
    def generate_text_summary(self, backtest_result, symbol, strategy_name):
        lines = []
        lines.append("=" * 80)
        lines.append(f"閲忓寲鍥炴祴鎶ュ憡 - {symbol} {strategy_name}")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"鐢熸垚鏃堕棿: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("銆愭€ц兘鎸囨爣銆?)
        lines.append("-" * 80)
        lines.append(f"鎬绘敹鐩婄巼:    {backtest_result['total_return_pct']:+.2f}%")
        lines.append(f"澶忔櫘姣旂巼:    {backtest_result['sharpe_ratio']:.2f}")
        lines.append(f"鏈€澶у洖鎾?    {backtest_result['max_drawdown_pct']:.2f}%")
        lines.append(f"鑳滅巼:        {backtest_result['win_rate_pct']:.2f}%")
        lines.append(f"浜ゆ槗娆℃暟:    {backtest_result['total_trades']}")
        lines.append(f"鏈€缁堣祫閲?    {backtest_result.get('final_equity', 0):,.2f}")
        lines.append("")
        
        trades = backtest_result.get('trades', [])
        if trades:
            lines.append("銆愪氦鏄撹褰曘€?)
            lines.append("-" * 80)
            for trade in trades:
                date = pd.to_datetime(trade['date']).strftime('%Y-%m-%d')
                trade_type = '涔板叆' if trade['type'] == 'buy' else '鍗栧嚭'
                lines.append(f"{date} | {trade_type:4s} | 浠锋牸: {trade['price']:8.2f} | "
                           f"鏁伴噺: {trade['shares']:6d} | 閲戦: {trade['value']:12,.2f}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return '\n'.join(lines)
    
    def list_reports(self):
        reports = []
        
        for report_file in self.report_dir.glob('*.html'):
            stat = report_file.stat()
            reports.append({
                'name': report_file.name,
                'path': str(report_file),
                'size': stat.st_size,
                'time': datetime.fromtimestamp(stat.st_mtime)
            })
        
        for report_file in self.report_dir.glob('*.json'):
            stat = report_file.stat()
            reports.append({
                'name': report_file.name,
                'path': str(report_file),
                'size': stat.st_size,
                'time': datetime.fromtimestamp(stat.st_mtime)
            })
        
        return sorted(reports, key=lambda x: x['time'], reverse=True)
    
    def delete_report(self, filename):
        filepath = self.report_dir / filename
        if filepath.exists():
            filepath.unlink()
            return True
        return False
