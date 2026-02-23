#!/usr/bin/env python3
"""
推文监控系统 - 每日快照模式
记录每天抓到的推文数量
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
SNAPSHOT_FILE = f"{PROJECT_DIR}/daily_snapshots.json"

def get_tweets_count():
    """抓取推文数量"""
    try:
        resp = requests.get(
            "https://xcancel.com/elonmusk",
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if resp.status_code != 200:
            return None
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tweet_divs = soup.find_all('div', class_='tweet-content')
        
        return len(tweet_divs)
        
    except:
        return None

def save_snapshot(count):
    """保存每日快照"""
    snapshots = {}
    
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, 'r') as f:
            snapshots = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 记录今天的快照（只记一次，后面不再覆盖）
    if today not in snapshots:
        snapshots[today] = {
            "count": count,
            "time": datetime.now().isoformat(),
            "note": "当天抓到的推文数量（非新增）"
        }
        print(f"📝 记录 {today}: {count} 条")
    else:
        # 如果今天已经记录过，检查数量是否变化
        if snapshots[today]["count"] != count:
            print(f"📝 {today} 更新: {snapshots[today]['count']} -> {count} 条")
            snapshots[today]["count"] = count
            snapshots[today]["updated"] = datetime.now().isoformat()
        else:
            print(f"✓ {today} 数量无变化: {count} 条")
    
    with open(SNAPSHOT_FILE, 'w') as f:
        json.dump(snapshots, f, indent=2, ensure_ascii=False)
    
    return snapshots

def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 每日快照...")
    
    count = get_tweets_count()
    
    if count is None:
        print("❌ 获取失败")
        return
    
    snapshots = save_snapshot(count)
    
    # 显示最近7天
    print("\n最近7天:")
    sorted_days = sorted(snapshots.keys(), reverse=True)[:7]
    for day in sorted_days:
        print(f"  {day}: {snapshots[day]['count']} 条")

if __name__ == "__main__":
    main()
