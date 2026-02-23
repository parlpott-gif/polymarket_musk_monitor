#!/usr/bin/env python3
"""
马斯克推文 RSS 监控脚本
使用 Nitter/XCancel RSS 订阅获取最新推文
"""

import feedparser
import json
import time
from datetime import datetime

# Config
OUTPUT_FILE = "/home/admin/polymarket_musk_monitor/tweets.json"
CHECK_INTERVAL = 300  # 5 minutes

# 多个 RSS 源，依次尝试
RSS_SOURCES = [
    "https://xcancel.com/elonmusk/rss",
    "https://nitter.privacydev.net/elonmusk/rss",
    "https://nitter.poast.org/elonmusk/rss",
]

# 记录上次推文 ID
LAST_TWEET_LINK = None

def get_tweets_from_rss():
    """从 RSS 源获取推文"""
    tweets = []
    
    for rss_url in RSS_SOURCES:
        try:
            print(f"尝试: {rss_url}")
            feed = feedparser.parse(rss_url, timeout=30)
            
            if feed.entries:
                print(f"✓ 成功获取 {len(feed.entries)} 条推文")
                for entry in feed.entries[:10]:
                    # 提取推文内容
                    title = entry.get('title', '')
                    # 清理标题，去掉用户名前缀
                    if 'Elon Musk (@elonmusk): ' in title:
                        content = title.replace('Elon Musk (@elonmusk): ', '')
                    else:
                        content = title
                    
                    # 检查是否是回复
                    is_reply = title.startswith('R to @')
                    
                    tweets.append({
                        'id': len(tweets) + 1,
                        'content': content.strip(),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', ''),
                        'username': 'Elon Musk',
                        'handle': '@elonmusk',
                        'is_reply': is_reply,
                        'source': rss_url
                    })
                return tweets, rss_url
            else:
                print(f"✗ 无数据: {rss_url}")
        except Exception as e:
            print(f"✗ 失败: {rss_url} - {e}")
            continue
    
    return None, None

def check_updates():
    """检查是否有新推文"""
    global LAST_TWEET_LINK
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查推文...")
    
    tweets, source = get_tweets_from_rss()
    
    if tweets is None:
        print("所有 RSS 源都失败，保存空数据")
        tweets = []
        source = "none"
    
    # 过滤回复（如果 polymarket 不计回复）
    original_tweets = [t for t in tweets if not t['is_reply']]
    reply_count = len(tweets) - len(original_tweets)
    
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
        LAST_TWEET_LINK = tweets[0]['link']
    
    # 保存数据
    data = {
        'last_updated': datetime.now().isoformat(),
        'count': len(tweets),
        'original_count': len(original_tweets),
        'reply_count': reply_count,
        'source': source,
        'new_tweets': len(new_tweets),
        'tweets': tweets
    }
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已保存: {len(tweets)} 条推文 ({len(original_tweets)} 条原创, {reply_count} 条回复)")
    return len(new_tweets)

def main():
    """主循环"""
    global LAST_TWEET_LINK
    
    # 读取上次保存的推文 ID
    try:
        with open(OUTPUT_FILE, 'r') as f:
            old_data = json.load(f)
            if old_data.get('tweets'):
                LAST_TWEET_LINK = old_data['tweets'][0].get('link')
                print(f"从缓存恢复，上次最新推文: {LAST_TWEET_LINK[:50]}...")
    except:
        pass
    
    # 立即检查一次
    check_updates()
    
    print(f"\n等待 {CHECK_INTERVAL} 秒后再次检查...")

if __name__ == "__main__":
    main()
