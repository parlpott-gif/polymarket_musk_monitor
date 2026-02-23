#!/usr/bin/env python3
"""
私人数据看板 - 带认证 + Polymarket 完整数据
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from functools import wraps
import subprocess
import re

app = Flask(__name__, static_folder='react-app/public')

USERNAME = "admin"
PASSWORD = "cong123456"
DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"

# ============ Polymarket 数据获取 ============

def get_series_events():
    try:
        result = subprocess.run(
            ["curl", "-s", "https://gamma-api.polymarket.com/series?slug=elon-tweet-daily"],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        if data and len(data) > 0:
            events = data[0].get("events", [])
            return [e for e in events if e.get("active") and not e.get("closed")]
    except:
        pass
    return []

def fetch_market_full(slug):
    """获取完整市场信息包括YES价格"""
    try:
        url = f"https://polymarket.com/event/{slug}"
        result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
        html = result.stdout
        
        if len(html) < 1000:
            return None
        
        # 标题
        title_match = re.search(r'"title":"([^"]+)"', html)
        title = title_match.group(1)[:60] if title_match else slug
        
        # 交易量
        vol_match = re.search(r'"volume":([0-9.]+)', html)
        volume = float(vol_match.group(1)) if vol_match else 0
        
        # 结算日期
        end_match = re.search(r'"endDate":"([^"]+)"', html)
        end_date = end_match.group(1)[:10] if end_match else "N/A"
        
        # YES价格 - 从API获取更准确
        yes_price = 0.5
        no_price = 0.5
        
        # 尝试从网页提取YES/NO价格
        yes_match = re.search(r'"Yes":{"price":([0-9.]+)}', html)
        no_match = re.search(r'"No":{"price":([0-9.]+)}', html)
        
        if yes_match:
            yes_price = float(yes_match.group(1))
        if no_match:
            no_price = float(no_match.group(1))
        
        # 检查是否关闭
        is_closed = '"closed":true' in html[:20000]
        
        return {
            "title": title,
            "volume": volume,
            "volume_display": f"${volume/1000:.0f}K" if volume < 1000000 else f"${volume/1000000:.1f}M",
            "end_date": end_date,
            "url": url,
            "slug": slug,
            "yes_price": yes_price,
            "no_price": no_price,
            "yes_pct": int(yes_price * 100),
            "no_pct": int(no_price * 100),
            "active": not is_closed and volume > 0
        }
    except:
        return None

KNOWN_SLUGS = [
    "elon-musk-of-tweets-february-17-february-24",
    "elon-musk-of-tweets-february-21-february-23", 
    "elon-musk-of-tweets-february-20-february-27",
    "elon-musk-of-tweets-february-24-march-3",
    "elon-musk-of-tweets-february-23-february-25",
    "elon-musk-of-tweets-march-2026"
]

def get_polymarket_data():
    active_markets = []
    found_slugs = set()
    
    events = get_series_events()
    if events:
        for e in events:
            slug = e.get("slug", "")
            market = fetch_market_full(slug)
            if market and market["active"]:
                active_markets.append(market)
                found_slugs.add(slug)
    
    for slug in KNOWN_SLUGS:
        if slug in found_slugs:
            continue
        market = fetch_market_full(slug)
        if market and market["active"]:
            active_markets.append(market)
    
    active_markets.sort(key=lambda x: x["volume"], reverse=True)
    return active_markets

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
        return jsonify({"markets": markets, "updated": "now"})
    except Exception as e:
        return jsonify({"error": str(e), "markets": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
