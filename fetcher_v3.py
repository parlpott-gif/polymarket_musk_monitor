#!/usr/bin/env python3
"""
马斯克推文监控脚本 v3
使用 BeautifulSoup 从 xcancel.com 抓取推文
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# Config
OUTPUT_FILE = "/home/admin/polymarket_musk_monitor/tweets.json"
CHECK_INTERVAL = 300  # 5 minutes

# 抓取源
SCRAPE_SOURCES = [
    ("xcancel", "https://xcancel.com/elonmusk"),
]

# 记录上次推文 ID
LAST_TWEET_LINK = None

def get_tweets_from_scrape():
    """从网页抓取推文"""
    tweets = []
    
    for name, url in SCRAPE_SOURCES:
        try:
            print(f"抓取: {name} - {url}")
            resp = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            if resp.status_code != 200:
                print(f"✗ HTTP {resp.status_code}")
                continue
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 找推文容器
            tweet_divs = soup.find_all('div', class_='tweet-content')
            
            if tweet_divs:
                print(f"✓ 成功获取 {len(tweet_divs)} 条推文")
                
                # 获取链接（用于去重）
                links = soup.find_all('a', class_='tweet-link')
                
                for i, div in enumerate(tweet_divs):
                    content = div.get_text().strip()
                    link = links[i].get('href', '') if i < len(links) else f"tweet_{i}"
                    
                    tweets.append({
                        'id': i + 1,
                        'content': content,
                        'link': link,
                        'username': 'Elon Musk',
                        'handle': '@elonmusk',
                        'source': name
                    })
                break
            else:
                # 尝试其他 class
                tweet_divs = soup.find_all('a', class_='post')
                if tweet_divs:
                    print(f"✓ 找到 {len(tweet_divs)} 条 (用 post class)")
                    for i, a in enumerate(tweet_divs[:10]):
                        content = a.get_text().strip()
                        tweets.append({
                            'id': i + 1,
                            'content': content,
                            'link': a.get('href', ''),
                            'username': 'Elon Musk',
                            'handle': '@elonmusk',
                            'source': name
                        })
                    break
                    
        except Exception as e:
            print(f"✗ 失败: {str(e)[:50]}")
            continue
    
    return tweets

def check_updates():
    """检查是否有新推文"""
    global LAST_TWEET_LINK
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查推文...")
    
    tweets = get_tweets_from_scrape()
    
    if not tweets:
        print("抓取失败，使用空数据")
    
    # 检查新推文
    new_tweets = []
    if tweets and LAST_TWEET_LINK:
        for tweet in tweets:
            if tweet['link'] != LAST_TWEET_LINK:
                new_tweets.append(tweet)
    elif tweets:
        new_tweets = [tweets[0]]
    
    if new_tweets:
        print(f"🎉 检测到 {len(new_tweets)} 条新推文!")
        for t in new_tweets:
            print(f"  - {t['content'][:60]}...")
        if tweets:
            LAST_TWEET_LINK = tweets[0]['link']
    else:
        print("未检测到新推文")
    
    # 保存数据
    data = {
        'last_updated': datetime.now().isoformat(),
        'count': len(tweets),
        'source': tweets[0]['source'] if tweets else 'none',
        'new_tweets': len(new_tweets),
        'tweets': tweets
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存: {len(tweets)} 条推文")

def main():
    """主函数"""
    global LAST_TWEET_LINK
    
    # 读取上次保存的推文 ID
    try:
        with open(OUTPUT_FILE, 'r') as f:
            old_data = json.load(f)
            if old_data.get('tweets'):
                LAST_TWEET_LINK = old_data['tweets'][0].get('link')
                print(f"从缓存恢复，上次最新: {str(LAST_TWEET_LINK)[:50]}...")
    except:
        pass
    
    check_updates()

if __name__ == "__main__":
    main()
