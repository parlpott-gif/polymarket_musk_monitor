#!/usr/bin/env python3
"""
用 Selenium 抓取 Twitter/X 数据
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re
from datetime import datetime

TWITTER_EPOCH = 1288834974657

def snowflake_to_time(tweet_id):
    try:
        tweet_id = int(tweet_id)
        ts = ((tweet_id >> 22) + TWITTER_EPOCH) / 1000
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    except:
        return None

def get_tweets():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    tweets = []
    
    for _ in range(3):  # 重试3次
        try:
            driver.get('https://xcancel.com/elonmusk')
            break
        except:
            continue
    
    # 找推文
    tweet_divs = driver.find_elements("css selector", "div[class*='tweet-content']")
    links = driver.find_elements("css selector", "a[class*='tweet-link']")
    
    for i, div in enumerate(tweet_divs):
        content = div.text.strip()
        
        link = ""
        if i < len(links):
            link = links[i].get_attribute('href') or ""
        
        # 从链接提取ID
        tweet_id = ""
        if '/status/' in link:
            tweet_id = link.split('/status/')[1].split('#')[0].split('?')[0]
        
        time_str = snowflake_to_time(tweet_id)
        date = time_str[:10] if time_str else None
        
        tweets.append({
            'tweet_id': tweet_id,
            'content': content,
            'link': link,
            'time': time_str,
            'date': date,
            'fetched': datetime.now().isoformat()
        })
    
    driver.quit()
    return tweets

if __name__ == "__main__":
    print("抓取中...")
    tweets = get_tweets()
    print(f"获取 {len(tweets)} 条推文")
    for t in tweets[:3]:
        print(f"  {t['time']} | {t['content'][:40]}...")
