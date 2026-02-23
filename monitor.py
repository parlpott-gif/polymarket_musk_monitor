#!/usr/bin/env python3
"""
马斯克推文监控系统 - 完整版
功能：
1. 抓取最新推文
2. 统计每日/每周/每月发推数量
3. 生成可视化图表
4. 自动推送到 GitHub
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Config
PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
DATA_FILE = f"{PROJECT_DIR}/data.json"
HTML_FILE = f"{PROJECT_DIR}/index.html"
COUNT_FILE = f"{PROJECT_DIR}/counts.json"

LAST_TWEET_LINK = None

def get_tweets():
    """抓取推文"""
    url = "https://xcancel.com/elonmusk"
    
    try:
        resp = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        
        if resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tweet_divs = soup.find_all('div', class_='tweet-content')
        
        if not tweet_divs:
            return []
        
        links = soup.find_all('a', class_='tweet-link')
        
        tweets = []
        for i, div in enumerate(tweet_divs):
            content = div.get_text().strip()
            link = links[i].get('href', '') if i < len(links) else ''
            full_link = f"https://xcancel.com{link}" if link.startswith('/') else link
            
            tweets.append({
                'id': i + 1,
                'content': content,
                'link': full_link,
                'fetched_at': datetime.now().isoformat()
            })
        
        return tweets
        
    except Exception as e:
        print(f"抓取失败: {e}")
        return []

def load_data():
    """加载历史数据"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"records": []}

def save_data(data):
    """保存数据"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_counts():
    """加载计数"""
    if os.path.exists(COUNT_FILE):
        with open(COUNT_FILE, 'r') as f:
            return json.load(f)
    return {"daily": {}, "weekly": {}, "monthly": {}}

def save_counts(counts):
    """保存计数"""
    with open(COUNT_FILE, 'w') as f:
        json.dump(counts, f, indent=2)

def analyze_and_record(tweets):
    """分析并记录"""
    data = load_data()
    counts = load_counts()
    
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%U")
    month = datetime.now().strftime("%Y-%m")
    
    # 记录这次抓到的数量
    current_count = len(tweets)
    
    # 每日计数
    if today not in counts["daily"]:
        counts["daily"][today] = current_count
    else:
        counts["daily"][today] = max(counts["daily"][today], current_count)
    
    # 每周计数
    if week not in counts["weekly"]:
        counts["weekly"][week] = current_count
    else:
        counts["weekly"][week] = max(counts["weekly"][week], current_count)
    
    # 每月计数
    if month not in counts["monthly"]:
        counts["monthly"][month] = current_count
    else:
        counts["monthly"][month] = max(counts["monthly"][month], current_count)
    
    # 记录详情
    record = {
        "date": today,
        "time": datetime.now().isoformat(),
        "count": current_count,
        "tweets": tweets[:10]  # 保存前10条
    }
    
    # 检查是否已记录今天
    existing_today = [i for i, r in enumerate(data["records"]) if r.get("date") == today]
    if existing_today:
        data["records"][existing_today[0]] = record
    else:
        data["records"].append(record)
    
    save_data(data)
    save_counts(counts)
    
    return counts

def generate_charts(counts):
    """生成可视化图表"""
    # 每日趋势图
    daily = counts.get("daily", {})
    if daily:
        dates = sorted(daily.keys())[-14:]  # 最近14天
        values = [daily.get(d, 0) for d in dates]
        
        plt.figure(figsize=(12, 6))
        plt.bar(dates, values, color='#00d4ff')
        plt.title('Elon Musk Daily Tweets (Recent 14 Days)', fontsize=14)
        plt.xlabel('Date')
        plt.ylabel('Tweet Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{PROJECT_DIR}/chart-daily.png", dpi=100)
        plt.close()
        print("✓ 生成日趋势图")
    
    # 每周趋势图
    weekly = counts.get("weekly", {})
    if weekly:
        weeks = sorted(weekly.keys())[-12:]  # 最近12周
        values = [weekly.get(w, 0) for w in weeks]
        
        plt.figure(figsize=(12, 6))
        plt.bar(weeks, values, color='#7b2ff7')
        plt.title('Elon Musk Weekly Tweets (Recent 12 Weeks)', fontsize=14)
        plt.xlabel('Week')
        plt.ylabel('Tweet Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{PROJECT_DIR}/chart-weekly.png", dpi=100)
        plt.close()
        print("✓ 生成周趋势图")
    
    # 每月趋势图
    monthly = counts.get("monthly", {})
    if monthly:
        months = sorted(monthly.keys())[-6:]  # 最近6个月
        values = [monthly.get(m, 0) for m in months]
        
        plt.figure(figsize=(10, 6))
        plt.bar(months, values, color='#00ff88')
        plt.title('Elon Musk Monthly Tweets (Recent 6 Months)', fontsize=14)
        plt.xlabel('Month')
        plt.ylabel('Tweet Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"{PROJECT_DIR}/chart-monthly.png", dpi=100)
        plt.close()
        print("✓ 生成月趋势图")

def update_html(tweets, counts):
    """更新HTML"""
    # 推文列表
    tweets_html = ""
    for tweet in tweets[:15]:
        content = tweet['content'][:150]
        if len(tweet['content']) > 150:
            content += "..."
        tweets_html += f'''
        <div class="tweet">
            <div class="tweet-content">{content}</div>
            <div class="tweet-link"><a href="{tweet['link']}" target="_blank">查看 →</a></div>
        </div>'''
    
    # 统计数据
    daily = counts.get("daily", {})
    weekly = counts.get("weekly", {})
    monthly = counts.get("monthly", {})
    
    today = datetime.now().strftime("%Y-%m-%d")
    week = datetime.now().strftime("%Y-W%U")
    month = datetime.now().strftime("%Y-%m")
    
    today_count = daily.get(today, 0)
    week_count = weekly.get(week, 0)
    month_count = monthly.get(month, 0)
    total_count = sum(daily.values())
    
    stats_html = f'''
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{today_count}</div>
            <div class="stat-label">今日</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{week_count}</div>
            <div class="stat-label">本周</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{month_count}</div>
            <div class="stat-label">本月</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_count}</div>
            <div class="stat-label">总计</div>
        </div>
    </div>'''
    
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 替换内容
    html = html.replace('<!-- STATS_PLACEHOLDER -->', stats_html)
    html = html.replace('<!-- TWEETS_PLACEHOLDER -->', tweets_html)
    html = html.replace('id="updateTime">--', f'id="updateTime">{datetime.now().strftime("%H:%M")}')
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✓ HTML已更新")

def main():
    global LAST_TWEET_LINK
    
    print(f"\n[{datetime.now()}] === 抓取推文 ===")
    
    tweets = get_tweets()
    
    if not tweets:
        print("抓取失败")
        return
    
    print(f"获取到 {len(tweets)} 条推文")
    
    # 分析并记录
    counts = analyze_and_record(tweets)
    
    # 生成图表
    generate_charts(counts)
    
    # 更新HTML
    update_html(tweets, counts)
    
    print("=== 完成 ===\n")

if __name__ == "__main__":
    main()
