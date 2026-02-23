#!/usr/bin/env python3
"""
Twitter/Fetch Twitter data and save to JSON
Run: python3 fetcher.py
"""

import json
import os
from datetime import datetime

# Config
OUTPUT_FILE = "/home/admin/polymarket_musk_monitor/tweets.json"
TWEETS_TO_FETCH = 10

def fetch_tweets():
    """Fetch tweets - using multiple fallback methods"""
    tweets = []
    
    # Method 1: Try using subprocess with curl to nitter
    try:
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "https://nitter.net/elonmusk/rss"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout:
            # Parse RSS XML
            import re
            items = re.findall(r'<item>(.*?)</item>', result.stdout, re.DOTALL)
            for item in items[:TWEETS_TO_FETCH]:
                title = re.search(r'<title>(.*?)</title>', item)
                pubDate = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if title:
                    content = title.group(1).replace('Elon Musk (@elonmusk): ', '')
                    tweets.append({
                        "id": len(tweets) + 1,
                        "content": content.strip(),
                        "time": pubDate.group(1) if pubDate else datetime.now().isoformat(),
                        "username": "Elon Musk",
                        "handle": "@elonmusk",
                        "fetched_at": datetime.now().isoformat()
                    })
            if tweets:
                print(f"Method 1 (Nitter RSS): Got {len(tweets)} tweets")
                return tweets
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    # Method 2: Use vxtwitter.com (more reliable)
    try:
        import urllib.request
        url = "https://api.vxtwitter.com/elonmusk"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            tweets.append({
                "id": 1,
                "content": data.get('text', ''),
                "time": data.get('created_at', ''),
                "username": "Elon Musk",
                "handle": "@elonmusk",
                "fetched_at": datetime.now().isoformat()
            })
            if tweets:
                print(f"Method 2 (vxtwitter): Got {len(tweets)} tweets")
                return tweets
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    # Method 3: Use fxtwitter.com
    try:
        import urllib.request
        url = "https://api.fxtwitter.com/elonmusk"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
            if 'tweet' in data:
                tweets.append({
                    "id": 1,
                    "content": data['tweet'].get('text', ''),
                    "time": data['tweet'].get('created_at', ''),
                    "username": "Elon Musk",
                    "handle": "@elonmusk",
                    "fetched_at": datetime.now().isoformat()
                })
                if tweets:
                    print(f"Method 3 (fxtwitter): Got {len(tweets)} tweets")
                    return tweets
    except Exception as e:
        print(f"Method 3 failed: {e}")
    
    # If all methods fail, return mock data
    print("All methods failed, using fallback data")
    return [{
        "id": 1,
        "content": "Unable to fetch tweets. Please check API.",
        "time": datetime.now().isoformat(),
        "username": "Elon Musk",
        "handle": "@elonmusk",
        "fetched_at": datetime.now().isoformat(),
        "error": True
    }]

def main():
    print(f"[{datetime.now()}] Fetching tweets...")
    tweets = fetch_tweets()
    
    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "last_updated": datetime.now().isoformat(),
            "count": len(tweets),
            "tweets": tweets
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {OUTPUT_FILE}")
    print(f"Total tweets: {len(tweets)}")

if __name__ == "__main__":
    main()
