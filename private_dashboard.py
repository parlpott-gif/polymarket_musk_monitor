#!/usr/bin/env python3
"""
私人数据看板 - 带认证
"""

from flask import Flask, request, jsonify, render_template_string
import json
import os
from functools import wraps

app = Flask(__name__)

# 配置（请修改密码）
USERNAME = "admin"
PASSWORD = "cong123456"  # 你可以改成自己的密码

DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"
TWEETS_FILE = "/home/admin/polymarket_musk_monitor/data/all_tweets.json"

def check_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return ('需要认证', 401, {'WWW-Authenticate': 'Basic realm="Private"'})
        return f(*args, **kwargs)
    return decorated

HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Private Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f0f23;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { text-align: center; margin: 30px 0; color: #00d4ff; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-value { font-size: 2rem; color: #00d4ff; font-weight: bold; }
        .stat-label { color: #888; margin-top: 5px; }
        
        .section { margin: 30px 0; }
        .section h2 { color: #00d4ff; margin-bottom: 15px; }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #888; }
        
        .footer { text-align: center; color: #666; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Private Dashboard</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ stats.total_tweets }}</div>
                <div class="stat-label">总推文数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ stats.new_today }}</div>
                <div class="stat-label">今日新增</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📅 每日统计</h2>
            <table>
                <tr><th>日期</th><th>条数</th></tr>
                {% for date, data in stats.daily.items()|reverse %}
                <tr><td>{{ date }}</td><td>{{ data.count }}</td></tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="section">
            <h2>🗓️ 每月统计</h2>
            <table>
                <tr><th>月份</th><th>条数</th></tr>
                {% for month, data in stats.monthly.items()|reverse %}
                <tr><td>{{ month }}</td><td>{{ data.count }}</td></tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="footer">
            <p>最后更新: {{ stats.last_updated }}</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
@check_auth
def index():
    # 读取数据
    stats = {"daily": {}, "monthly": {}, "total_tweets": 0, "new_today": 0, "last_updated": "N/A"}
    
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            stats = json.load(f)
    
    return render_template_string(HTML, stats=stats)

@app.route('/api')
@check_auth
def api():
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    # 监听所有接口，端口 5000
    app.run(host='0.0.0.0', port=5000, debug=False)
