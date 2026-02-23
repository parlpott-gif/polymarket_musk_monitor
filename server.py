#!/usr/bin/env python3
"""
私人数据看板 - 集成 polymarket-elon-tweets
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from functools import wraps
import subprocess

app = Flask(__name__, static_folder='react-app/public')

USERNAME = "admin"
PASSWORD = "cong123456"
DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"

# ============ Polymarket 数据获取 ============

def get_polymarket_data():
    """运行脚本获取 Polymarket 数据"""
    try:
        result = subprocess.run(
            ["python3", "/home/admin/.openclaw/workspace/skills/polymarket-elon-tweets/get_elon_tweets.py"],
            capture_output=True, text=True, timeout=120
        )
        
        markets = []
        lines = result.stdout.split('\n')
        
        current_market = None
        outcomes = []
        
        for line in lines:
            line = line.strip()
            
            # 检测新市场
            if line.startswith('📌'):
                if current_market:
                    current_market['outcomes'] = outcomes
                    markets.append(current_market)
                
                # 解析标题和URL
                title_match = line.replace('📌', '').strip()
                current_market = {
                    'title': title_match,
                    'outcomes': [],
                    'url': ''
                }
                outcomes = []
            
            # 结算日期和交易量
            elif '结算:' in line and '交易量:' in line:
                结算 = line.split('|')[0].replace('结算:', '').strip()
                交易量 = line.split('|')[1].replace('交易量:', '').strip()
                if current_market:
                    current_market['end_date'] = 结算
                    current_market['volume_display'] = 交易量
                    current_market['volume'] = int(交易量.replace('$','').replace(',',''))
            
            # URL
            elif line.startswith('http'):
                if current_market:
                    current_market['url'] = line
            
            # 结果选项
            elif '•' in line and 'Yes' in line:
                parts = line.replace('•', '').strip().split(':')
                if len(parts) == 2:
                    outcome = parts[0].strip()
                    pct = parts[1].replace('Yes', '').strip()
                    outcomes.append({'outcome': outcome, 'pct': pct})
        
        # 添加最后一个
        if current_market:
            current_market['outcomes'] = outcomes
            markets.append(current_market)
        
        # 按交易量排序
        markets.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        return markets
        
    except Exception as e:
        print(f"Error: {e}")
        return []

# ============ Flask 路由 ============

def check_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return ('需要认证', 401, {'WWW-Authenticate': 'Basic realm="Private"'})
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@check_auth
def index():
    return send_from_directory('react-app/public', 'index.html')

@app.route('/<path:filename>')
@check_auth
def static_files(filename):
    return send_from_directory('react-app/public', filename)

@app.route('/api')
@check_auth
def api():
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    return jsonify(data)

@app.route('/api/polymarket')
@check_auth
def polymarket_api():
    try:
        markets = get_polymarket_data()
        return jsonify({"markets": markets})
    except Exception as e:
        return jsonify({"error": str(e), "markets": []})

@app.route('/api/prediction')
@check_auth
def prediction_api():
    """推文预测 API"""
    import sys
    sys.path.insert(0, '/home/admin/polymarket_musk_monitor')
    from predictor import calculate_predictions
    try:
        pred = calculate_predictions()
        return jsonify(pred)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
