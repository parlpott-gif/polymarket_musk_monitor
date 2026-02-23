#!/usr/bin/env python3
"""
马斯克推文计数器 - 统计历史推文数量
"""

import json
import os
from datetime import datetime, timedelta

# Config
PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
COUNT_FILE = f"{PROJECT_DIR}/tweet_counts.json"
TWEETS_FILE = f"{PROJECT_DIR}/tweets.json"

def load_counts():
    """加载历史计数"""
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, 'r') as f:
            return json.load(f)
    return {
        "total": 0,
        "last_count": 0,
        "last_check": None,
        "daily": {},
        "weekly": {},
    }

def save_counts(data):
    """保存计数"""
    with open(COUNT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_date_key(date_str=None):
    """获取日期key"""
    if date_str:
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            dt = datetime.now()
    else:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d")

def analyze_counts():
    """分析推文数量"""
    counts = load_counts()
    
    # 读取当前推文
    if not os.path.exists(TWEETS_FILE):
        print("没有推文数据")
        return
    
    with open(TWEETS_FILE, 'r') as f:
        data = json.load(f)
    
    current_count = data.get('count', 0)
    today = get_date_key()
    
    # 更新每日计数
    if today not in counts['daily']:
        # 首次记录今天
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 如果昨天没记录，记录昨天的数量
        if counts.get('last_check') and counts['last_check'] != today:
            yesterday_count = counts.get('last_count', 0)
            counts['daily'][counts['last_check']] = yesterday_count
        
        counts['daily'][today] = current_count
    
    counts['last_count'] = current_count
    counts['last_check'] = today
    
    save_counts(counts)
    
    # 输出统计
    print(f"\n=== 推文统计 ===")
    print(f"今日 ({today}): {counts['daily'].get(today, 0)} 条")
    
    print(f"\n最近7天:")
    total_week = 0
    for i in range(7):
        d = datetime.now() - timedelta(days=i)
        date_key = d.strftime("%Y-%m-%d")
        count = counts['daily'].get(date_key, 0)
        total_week += count
        if count > 0 or i == 0:
            print(f"  {date_key}: {count} 条")
    
    print(f"\n本周总计: {total_week} 条")
    print(f"历史总计: {sum(counts['daily'].values())} 条")

if __name__ == "__main__":
    analyze_counts()
