#!/usr/bin/env python3
"""
马斯克推文监控脚本 v3 - 最终版
抓取推文 -> 更新 tweets.json -> 更新 HTML
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os

# Config
PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
OUTPUT_FILE = f"{PROJECT_DIR}/tweets.json"
HTML_FILE = f"{PROJECT_DIR}/index.html"

SCRAPE_SOURCES = [
    ("xcancel", "https://xcancel.com/elonmusk"),
]

LAST_TWEET_LINK = None

def get_tweets_from_scrape():
    """从网页抓取推文"""
    tweets = []
    
    for name, url in SCRAPE_SOURCES:
        try:
            print(f"抓取: {name}")
            resp = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if resp.status_code != 200:
                print(f"✗ HTTP {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            tweet_divs = soup.find_all('div', class_='tweet-content')
            
            if tweet_divs:
                print(f"✓ 获取 {len(tweet_divs)} 条推文")
                links = soup.find_all('a', class_='tweet-link')
                
                for i, div in enumerate(tweet_divs):
                    content = div.get_text().strip()
                    link = links[i].get('href', '') if i < len(links) else f"tweet_{i}"
                    
                    tweets.append({
                        'id': i + 1,
                        'content': content,
                        'link': f"https://xcancel.com{link}" if link.startswith('/') else link,
                        'username': 'Elon Musk',
                        'handle': '@elonmusk',
                        'source': name
                    })
                break
                    
        except Exception as e:
            print(f"✗ 失败: {str(e)[:50]}")
            continue
    
    return tweets

def update_html(tweets):
    """更新 HTML 文件，嵌入推文数据"""
    
    # 生成推文 HTML
    tweets_html = ""
    for tweet in tweets[:10]:  # 只显示前10条
        # 截断太长的内容
        content = tweet['content'][:200]
        if len(tweet['content']) > 200:
            content += "..."
            
        tweets_html += f'''
        <div class="tweet">
            <div class="tweet-header">
                <div class="avatar"></div>
                <div class="user-info">
                    <div class="username">{tweet['username']} <span class="badge">🐦</span></div>
                    <div class="handle">{tweet['handle']}</div>
                </div>
            </div>
            <div class="tweet-content">{content}</div>
            <div class="tweet-link"><a href="{tweet['link']}" target="_blank">查看原文 →</a></div>
        </div>'''
    
    # 读取模板
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 替换推文容器内容
    html = html.replace(
        '<!-- Tweets will be embedded here -->',
        tweets_html
    )
    
    # 更新统计
    html = html.replace(
        'id="tweetCount">0',
        f'id="tweetCount">{len(tweets)}'
    )
    html = html.replace(
        'id="lastUpdate">--',
        f'id="lastUpdate">{datetime.now().strftime("%H:%M")}'
    )
    
    # 写回
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML 已更新")

def check_updates():
    """检查并更新"""
    global LAST_TWEET_LINK
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] === 检查推文 ===")
    
    tweets = get_tweets_from_scrape()
    
    if not tweets:
        print("抓取失败")
        return
    
    # 检查新推文
    new_count = 0
    if LAST_TWEET_LINK:
        for tweet in tweets:
            if tweet['link'] != LAST_TWEET_LINK:
                new_count += 1
    else:
        new_count = len(tweets)
    
    if new_count > 0:
        print(f"🎉 {new_count} 条新推文!")
        LAST_TWEET_LINK = tweets[0]['link']
    else:
        print("无新推文")
    
    # 保存 JSON
    data = {
        'last_updated': datetime.now().isoformat(),
        'count': len(tweets),
        'source': tweets[0]['source'] if tweets else 'none',
        'new_tweets': new_count,
        'tweets': tweets
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON 已保存: {len(tweets)} 条")
    
    # 更新 HTML
    update_html(tweets)
    
    print("=== 完成 ===\n")

def main():
    global LAST_TWEET_LINK
    
    # 读取缓存
    try:
        with open(OUTPUT_FILE, 'r') as f:
            old = json.load(f)
            if old.get('tweets'):
                LAST_TWEET_LINK = old['tweets'][0].get('link')
    except:
        pass
    
    check_updates()

if __name__ == "__main__":
    main()
