#!/usr/bin/env python3
"""
获取 Polymarket Elon Musk 市场数据
"""

import subprocess
import json
import re

def get_series_events():
    """从 API 获取系列事件"""
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
    """获取单个市场信息"""
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

def get_markets():
    """获取所有活跃市场"""
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

if __name__ == "__main__":
    markets = get_markets()
    print(json.dumps(markets, indent=2))
