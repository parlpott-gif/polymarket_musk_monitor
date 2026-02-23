#!/usr/bin/env python3
"""
推文数据收集系统 - 完整版
长期存储每条推文的详细信息
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from collections import defaultdict

PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
DATA_DIR = f"{PROJECT_DIR}/data"
TWEETS_FILE = f"{DATA_DIR}/all_tweets.json"
STATS_FILE = f"{DATA_DIR}/stats.json"

TWITTER_EPOCH = 1288834974657

def snowflake_to_time(tweet_id):
    try:
        tweet_id = int(tweet_id)
        timestamp_ms = ((tweet_id >> 22) + TWITTER_EPOCH)
        return datetime.fromtimestamp(timestamp_ms / 1000)
    except:
        return None

def load_tweets():
    """加载已有推文"""
    if os.path.exists(TWEETS_FILE):
        with open(TWEETS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tweets(tweets):
    """保存推文"""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(TWEETS_FILE, 'w') as f:
        json.dump(tweets, f, indent=2, ensure_ascii=False)

def load_stats():
    """加载统计"""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'r') as f:
            return json.load(f)
    return {
        "daily": {},      # "2026-02-23": {"count": 21, "tweets": [...], "hourly": {}}
        "weekly": {},     # "2026-W08": {"count": 150}
        "monthly": {},   # "2026-02": {"count": 600}
        "last_updated": None
    }

def save_stats(stats):
    """保存统计"""
    with open(STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

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
        tweet_divs = soup.find_all('div', class_=lambda x: x and 'tweet-content' in x)
        links = soup.find_all('a', class_='tweet-link')
        
        tweets = []
        for i, div in enumerate(tweet_divs):
            content = div.get_text().strip()
            
            link = links[i].get('href', '') if i < len(links) else ""
            full_link = f"https://xcancel.com{link}" if link.startswith('/') else link
            
            tweet_id = ""
            if '/status/' in link:
                tweet_id = link.split('/status/')[1].split('#')[0].split('?')[0]
            
            dt = snowflake_to_time(tweet_id) if tweet_id else None
            
            tweets.append({
                'tweet_id': tweet_id,
                'content': content,
                'link': full_link,
                'full_time': dt.isoformat() if dt else None,
                'date': dt.strftime('%Y-%m-%d') if dt else None,
                'hour': dt.hour if dt else None,
                'week': dt.strftime('%Y-W%W') if dt else None,
                'month': dt.strftime('%Y-%m') if dt else None,
                'fetched_at': datetime.now().isoformat()
            })
        
        return tweets
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def update_database(new_tweets):
    """更新数据库"""
    all_tweets = load_tweets()
    stats = load_stats()
    
    # 获取已有ID
    existing_ids = set(t.get('tweet_id', '') for t in all_tweets)
    
    # 只添加新推文
    added = 0
    for t in new_tweets:
        if t['tweet_id'] and t['tweet_id'] not in existing_ids:
            all_tweets.append(t)
            added += 1
    
    # 更新统计
    today = datetime.now().strftime("%Y-%m-%d")
    now_week = datetime.now().strftime('%Y-W%W')
    now_month = datetime.now().strftime('%Y-%m')
    
    # 每日统计
    if today not in stats["daily"]:
        stats["daily"][today] = {"count": 0, "tweets": [], "hourly": {}}
    
    # 每周统计
    if now_week not in stats["weekly"]:
        stats["weekly"][now_week] = {"count": 0, "tweets": []}
    
    # 每月统计
    if now_month not in stats["monthly"]:
        stats["monthly"][now_month] = {"count": 0, "tweets": []}
    
    # 更新今日统计（根据所有推文计算）
    today_tweets = [t for t in all_tweets if t.get('date') == today]
    stats["daily"][today] = {
        "count": len(today_tweets),
        "tweets": [{"time": t.get('full_time'), "content": t['content'][:50]} for t in today_tweets],
        "hourly": {str(h): len([t for t in today_tweets if t.get('hour') == h]) for h in range(24)}
    }
    
    # 本周统计
    week_tweets = [t for t in all_tweets if t.get('week') == now_week]
    week_dates = list(set([t.get('date') for t in week_tweets if t.get('date')]))
    stats["weekly"][now_week] = {
        "count": len(week_tweets),
        "daily_breakdown": {d: len([x for x in week_tweets if x.get('date') == d]) for d in week_dates}
    }
    
    # 本月统计
    month_tweets = [t for t in all_tweets if t.get('month') == now_month]
    stats["monthly"][now_month] = {
        "count": len(month_tweets)
    }
    
    stats["last_updated"] = datetime.now().isoformat()
    stats["total_tweets"] = len(all_tweets)
    stats["new_today"] = added
    
    # 保存
    save_tweets(all_tweets)
    save_stats(stats)
    
    return len(all_tweets), added

def show_summary():
    """显示摘要"""
    stats = load_stats()
    all_tweets = load_tweets()
    
    print("\n" + "="*50)
    print("📊 数据收集摘要")
    print("="*50)
    print(f"总推文数: {len(all_tweets)}")
    print(f"今日新增: {stats.get('new_today', 0)}")
    print()
    
    print("📅 最近7天每日条数:")
    for i in range(7):
        d = datetime.now().replace(hour=0, minute=0, second=0)
        d = d.replace(day=d.day - i)
        date_key = d.strftime("%Y-%m-%d")
        if date_key in stats.get("daily", {}):
            cnt = stats["daily"][date_key]["count"]
            print(f"  {date_key}: {cnt} 条")
    
    print()
    print("📆 最近4周每周条数:")
    for i in range(4):
        d = datetime.now()
        week = d.isocalendar()[1] - i
        year = d.year
        if week < 1:
            year -= 1
            week += 52
        week_key = f"{year}-W{week:02d}"
        if week_key in stats.get("weekly", {}):
            cnt = stats["weekly"][week_key]["count"]
            print(f"  {week_key}: {cnt} 条")
    
    print()
    print("🗓️ 每月条数:")
    for m in sorted(stats.get("monthly", {}).keys())[-6:]:
        cnt = stats["monthly"][m]["count"]
        print(f"  {m}: {cnt} 条")
    
    print("="*50)

def main():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 抓取推文...")
    
    new_tweets = get_tweets()
    
    if not new_tweets:
        print("获取失败")
        return
    
    print(f"获取 {len(new_tweets)} 条")
    
    # 更新数据库
    total, added = update_database(new_tweets)
    print(f"数据库更新: 共 {total} 条, 新增 {added} 条")
    
    # 显示摘要
    show_summary()

if __name__ == "__main__":
    main()
