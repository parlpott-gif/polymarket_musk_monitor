#!/usr/bin/env python3
"""
推文监控系统 - 完整版（带时间）
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
OUTPUT_FILE = f"{PROJECT_DIR}/tweets.json"
SNAPSHOT_FILE = f"{PROJECT_DIR}/daily_snapshots.json"
STATS_FILE = f"{PROJECT_DIR}/stats.json"

TWITTER_EPOCH = 1288834974657

def snowflake_to_time(tweet_id):
    """从推文ID解析时间"""
    try:
        tweet_id = int(tweet_id)
        timestamp_ms = ((tweet_id >> 22) + TWITTER_EPOCH)
        return datetime.fromtimestamp(timestamp_ms / 1000)
    except:
        return None

def get_tweets():
    """抓取推文"""
    try:
        resp = requests.get(
            "https://xcancel.com/elonmusk",
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tweet_divs = soup.find_all('div', class_='tweet-content')
        links = soup.find_all('a', class_='tweet-link')
        
        tweets = []
        for i, div in enumerate(tweet_divs):
            content = div.get_text().strip()
            
            # 获取推文链接和ID
            link = links[i].get('href', '') if i < len(links) else ""
            full_link = f"https://xcancel.com{link}" if link.startswith('/') else link
            
            # 从链接提取ID
            tweet_id = ""
            if '/status/' in link:
                tweet_id = link.split('/status/')[1].split('#')[0].split('?')[0]
            
            # 解析时间
            dt = snowflake_to_time(tweet_id) if tweet_id else None
            
            tweets.append({
                'id': i + 1,
                'tweet_id': tweet_id,
                'content': content,
                'link': full_link,
                'time': dt.strftime('%Y-%m-%d %H:%M:%S') if dt else None,
                'date': dt.strftime('%Y-%m-%d') if dt else None,
                'fetched': datetime.now().isoformat()
            })
        
        return tweets
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def update_stats(tweets):
    """更新统计数据"""
    # 统计每日
    daily = {}
    for t in tweets:
        if t.get('date'):
            daily[t.get('date', 'unknown')] = daily.get(t.get('date', 'unknown'), 0) + 1
    
    # 加载历史
    stats = {"daily": {}, "monthly": {}}
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            stats = json.load(f)
    
    # 更新今天
    today = datetime.now().strftime("%Y-%m-%d")
    stats["daily"][today] = daily.get(today, len(tweets))
    
    # 每月
    month = datetime.now().strftime("%Y-%m")
    stats["monthly"][month] = stats["monthly"].get(month, 0) + len(tweets)
    
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)
    
    return stats

def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 抓取推文...")
    
    tweets = get_tweets()
    
    if not tweets:
        print("获取失败")
        return
    
    # 显示前几条的时间和内容
    print(f"获取 {len(tweets)} 条:")
    for t in tweets[:5]:
        print(f"  {t.get('time', 'N/A')} | {t['content'][:35]}...")
    
    # 统计
    stats = update_stats(tweets)
    
    # 保存
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "count": len(tweets),
            "last_updated": datetime.now().isoformat(),
            "tweets": tweets
        }, f, ensure_ascii=False, indent=2)
    
    # 快照
    today = datetime.now().strftime("%Y-%m-%d")
    snapshots = {}
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, 'r') as f:
            snapshots = json.load(f)
    snapshots[today] = {
        "count": len(tweets),
        "time": datetime.now().isoformat(),
        "sample": [{"time": t.get('time'), "content": t['content'][:30]} for t in tweets[:3]]
    }
    with open(SNAPSHOT_FILE, 'w') as f:
        json.dump(snapshots, f, indent=2, ensure_ascii=False)
    
    print("✓ 完成")

if __name__ == "__main__":
    main()
