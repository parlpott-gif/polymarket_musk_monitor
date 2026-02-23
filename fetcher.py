#!/usr/bin/env python3
"""
推文监控系统 - 使用 curl + BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
OUTPUT_FILE = f"{PROJECT_DIR}/tweets.json"
HTML_FILE = f"{PROJECT_DIR}/index.html"
COUNT_FILE = f"{PROJECT_DIR}/counts.json"

LAST_LINK = None

def get_tweets():
    """抓取推文"""
    try:
        resp = requests.get(
            "https://xcancel.com/elonmusk",
            timeout=30,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        if resp.status_code != 200:
            print(f"HTTP {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tweet_divs = soup.find_all('div', class_='tweet-content')
        
        if not tweet_divs:
            # 尝试其他class
            tweet_divs = soup.find_all('div', class_=lambda x: x and 'tweet-content' in x)
        
        tweets = []
        # 获取推文链接
        links = soup.find_all('a', class_='tweet-link')
        
        for i, div in enumerate(tweet_divs):
            content = div.get_text().strip()
            link = links[i].get('href', '') if i < len(links) else f"/elonmusk/status/{i}"
            full_link = f"https://xcancel.com{link}" if link.startswith('/') else link
            
            tweets.append({
                'id': i + 1,
                'content': content,
                'link': full_link,
                'fetched': datetime.now().isoformat()
            })
        
        return tweets
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def update_counts(tweets):
    """更新计数"""
    counts = {"daily": {}, "weekly": {}, "monthly": {}}
    
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, 'r') as f:
            counts = json.load(f)
    
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%W")
    month = datetime.now().strftime("%Y-%m")
    
    counts["daily"][today] = len(tweets)
    counts["weekly"][week] = counts["weekly"].get(week, 0) + len(tweets)
    counts["monthly"][month] = counts["monthly"].get(month, 0) + len(tweets)
    
    with open(COUNT_FILE, 'w') as f:
        json.dump(counts, f, indent=2)
    
    return counts

def update_html(tweets, counts):
    """更新HTML"""
    # 推文HTML
    tweets_html = ""
    for t in tweets[:15]:
        content = t['content'][:120]
        if len(t['content']) > 120:
            content += "..."
        tweets_html += f'''
        <div class="tweet">
            <div class="tweet-content">{content}</div>
            <div class="tweet-link"><a href="{t['link']}" target="_blank">查看 →</a></div>
        </div>'''
    
    # 统计
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%W")
    month = datetime.now().strftime("%Y-%m")
    
    stats = f'''
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(tweets)}</div>
            <div class="stat-label">今日</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{counts["weekly"].get(week, len(tweets))}</div>
            <div class="stat-label">本周</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{counts["monthly"].get(month, len(tweets))}</div>
            <div class="stat-label">本月</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(counts["daily"].values())}</div>
            <div class="stat-label">总计</div>
        </div>
    </div>'''
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    html = html.replace('<!-- STATS_PLACEHOLDER -->', stats)
    html = html.replace('<!-- TWEETS_PLACEHOLDER -->', tweets_html)
    html = html.replace('id="updateTime">--', f'id="updateTime">{datetime.now().strftime("%H:%M")}')
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    global LAST_LINK
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 检查推文...")
    
    tweets = get_tweets()
    
    if not tweets:
        print("获取失败")
        return
    
    print(f"获取 {len(tweets)} 条推文")
    
    # 更新计数
    counts = update_counts(tweets)
    
    # 更新HTML
    update_html(tweets, counts)
    
    # 保存JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "count": len(tweets),
            "last_updated": datetime.now().isoformat(),
            "tweets": tweets
        }, f, ensure_ascii=False, indent=2)
    
    print("✓ 完成")

if __name__ == "__main__":
    main()
