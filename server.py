#!/usr/bin/env python3
"""
私人数据看板 - 带认证 + React 前端 + Polymarket
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from functools import wraps
import subprocess

app = Flask(__name__, static_folder='react-app/public')

# 配置
USERNAME = "admin"
PASSWORD = "cong123456"

DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"

# ============ Polymarket 数据获取 ============

def get_polymarket_data():
    """获取 Polymarket 数据"""
    import re
    
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
    
    def fetch_market(slug):
        try:
            url = f"https://polymarket.com/event/{slug}"
            result = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
            html = result.stdout
            
            if len(html) < 1000:
                return None
            
            title_match = re.search(r'"title":"([^"]+)"', html)
            title = title_match.group(1)[:55] if title_match else slug
            
            vol_match = re.search(r'"volume":([0-9.]+)', html)
            volume = float(vol_match.group(1)) if vol_match else 0
            
            end_match = re.search(r'"endDate":"([^"]+)"', html)
            end_date = end_match.group(1)[:10] if end_match else "N/A"
            
            is_closed = '"closed":true' in html[:20000]
            
            return {
                "title": title,
                "volume": volume,
                "end_date": end_date,
                "url": url,
                "slug": slug,
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
    
    active_markets = []
    found_slugs = set()
    
    events = get_series_events()
    if events:
        for e in events:
            slug = e.get("slug", "")
            market = fetch_market(slug)
            if market and market["active"]:
                active_markets.append(market)
                found_slugs.add(slug)
    
    for slug in KNOWN_SLUGS:
        if slug in found_slugs:
            continue
        market = fetch_market(slug)
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
    """推文数据 API"""
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    return jsonify(data)

@app.route('/api/polymarket')
@check_auth
def polymarket_api():
    """Polymarket 数据 API"""
    try:
        markets = get_polymarket_data()
        return jsonify({"markets": markets, "updated": "now"})
    except Exception as e:
        return jsonify({"error": str(e), "markets": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
