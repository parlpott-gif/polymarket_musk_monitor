#!/usr/bin/env python3
"""
推文数据抓取与分析系统
使用 ntscraper 抓取 Twitter/Nitter 数据
"""

import pandas as pd
from ntscraper import Nitter
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time
import os
import json
from datetime import datetime, timedelta

# Config
PROJECT_DIR = "/home/admin/polymarket_musk_monitor"
USER = "elonmusk"
START_DATE = "2025-01-01"
END_DATE = "2026-02-23"
DATA_FILE = f"{PROJECT_DIR}/tweet_data.csv"
STATS_FILE = f"{PROJECT_DIR}/stats.json"
HTML_FILE = f"{PROJECT_DIR}/analytics.html"

def fetch_tweets():
    """抓取推文数据"""
    print(f"🚀 开始抓取 {USER} 从 {START_DATE} 到 {END_DATE} 的数据...")
    
    scraper = Nitter()
    tweets_data = []
    
    # 尝试抓取
    try:
        # mode='user' 获取用户推文
        # number=-1 尽量多抓
        tweets = scraper.get_tweets(USER, mode='user', number=-1, since=START_DATE, until=END_DATE)
        
        if tweets and tweets.get('tweets'):
            print(f"✓ 获取到 {len(tweets['tweets'])} 条推文")
            
            for t in tweets['tweets']:
                tweets_data.append({
                    'timestamp': t.get('date', ''),
                    'text': t.get('text', ''),
                    'is_reply': t.get('is-reply', False),
                    'is_retweet': t.get('is-retweet', False),
                    'link': t.get('link', ''),
                    'likes': t.get('likes', 0),
                    'retweets': t.get('retweets', 0)
                })
        else:
            print("⚠ 未获取到推文数据，尝试备用方法...")
            # 备用：尝试获取最近的推文
            tweets = scraper.get_tweets(USER, mode='user', number=100)
            if tweets and tweets.get('tweets'):
                for t in tweets['tweets']:
                    tweets_data.append({
                        'timestamp': t.get('date', ''),
                        'text': t.get('text', ''),
                        'is_reply': t.get('is-reply', False),
                        'is_retweet': t.get('is-retweet', False),
                        'link': t.get('link', ''),
                        'likes': t.get('likes', 0),
                        'retweets': t.get('retweets', 0)
                    })
                print(f"✓ 备用模式获取到 {len(tweets_data)} 条推文")
                
    except Exception as e:
        print(f"❌ 抓取失败: {e}")
        return None
    
    if not tweets_data:
        print("❌ 没有获取到任何数据")
        return None
    
    # 转换为 DataFrame
    df = pd.DataFrame(tweets_data)
    
    # 解析时间
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df['date'] = df['timestamp'].dt.date
    except:
        pass
    
    # 保存原始数据
    df.to_csv(DATA_FILE, index=False, encoding='utf-8')
    print(f"✓ 数据已保存至 {DATA_FILE}")
    
    return df

def analyze_data(df):
    """分析数据并生成统计"""
    if df is None or df.empty:
        return None
    
    print("\n📊 开始分析...")
    
    # 统计每日条数
    # 全部推文
    if 'date' in df.columns and not df['date'].isna().all():
        daily_total = df.groupby('date').size().reset_index(name='total')
        
        # 纯原创（非回复非转发）
        daily_original = df[(df['is_reply'] == False) & (df['is_retweet'] == False)].groupby('date').size().reset_index(name='original')
        
        # 合并
        stats = pd.merge(daily_total, daily_original, on='date', how='left').fillna(0)
        stats.to_csv(STATS_FILE, index=False)
        
        # 计算统计信息
        analysis = {
            "total_tweets": int(len(df)),
            "original_tweets": int(len(df[(df['is_reply'] == False) & (df['is_retweet'] == False)])),
            "replies": int(len(df[df['is_reply'] == True])),
            "retweets": int(len(df[df['is_retweet'] == True])),
            "avg_daily": round(stats['total'].mean(), 2),
            "avg_original_daily": round(stats['original'].mean(), 2),
            "max_daily": int(stats['total'].max()),
            "min_daily": int(stats['total'].min()),
            "data_days": len(stats),
            "last_updated": datetime.now().isoformat()
        }
        
        with open(STATS_FILE.replace('.csv', '_summary.json'), 'w') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 分析完成: {analysis['total_tweets']} 条推文")
        return stats, analysis
    
    return None, None

def generate_charts(stats, analysis):
    """生成可视化图表"""
    if stats is None or stats.empty:
        print("⚠ 无数据可绘图")
        return
    
    print("📈 生成图表...")
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 图1: 每日推文趋势
    fig, ax = plt.subplots(figsize=(14, 6))
    
    dates = pd.to_datetime(stats['date'])
    ax.plot(dates, stats['total'], label='All Tweets', alpha=0.6, linewidth=1)
    ax.plot(dates, stats['original'], label='Original Only', color='red', linewidth=1.5)
    
    # 平均线
    avg = stats['original'].mean()
    ax.axhline(y=avg, color='green', linestyle='--', alpha=0.7, label=f'Avg: {avg:.1f}')
    
    ax.set_title(f'Activity Analysis', fontsize=14, fontweight='bold')
    ax.set_xlabel('Date')
    ax.set_ylabel('Tweet Count')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{PROJECT_DIR}/chart-trend.png", dpi=120)
    plt.close()
    print("✓ 趋势图已生成")
    
    # 图2: 每周统计
    stats['week'] = pd.to_datetime(stats['date']).dt.isocalendar().week
    stats['year'] = pd.to_datetime(stats['date']).dt.isocalendar().year
    weekly = stats.groupby(['year', 'week'])['original'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(len(weekly)), weekly['original'], color='#00d4ff', alpha=0.8)
    ax.set_title('Weekly Volume', fontsize=14, fontweight='bold')
    ax.set_xlabel('Week')
    ax.set_ylabel('Tweet Count')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{PROJECT_DIR}/chart-weekly.png", dpi=120)
    plt.close()
    print("✓ 周统计图已生成")
    
    # 图3: 分布直方图
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(stats['original'], bins=20, color='#7b2ff7', alpha=0.7, edgecolor='white')
    ax.axvline(x=avg, color='red', linestyle='--', label=f'Mean: {avg:.1f}')
    ax.set_title('Daily Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Tweets per Day')
    ax.set_ylabel('Frequency')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{PROJECT_DIR}/chart-dist.png", dpi=120)
    plt.close()
    print("✓ 分布图已生成")

def generate_html(stats, analysis):
    """生成数据分析页面"""
    if analysis is None:
        return
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Activity Analytics</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        h1 {{ font-size: 2rem; margin-bottom: 8px; }}
        .subtitle {{ color: #888; font-size: 0.9rem; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
        }}
        .stat-value {{ font-size: 2rem; font-weight: bold; color: #00d4ff; }}
        .stat-label {{ color: #888; font-size: 0.8rem; margin-top: 5px; }}
        
        .chart-section {{
            margin-bottom: 30px;
        }}
        .chart-title {{
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #00d4ff;
        }}
        .chart-container {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
        }}
        .chart-container img {{
            width: 100%;
            border-radius: 8px;
        }}
        
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.8rem;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Activity Analytics</h1>
            <p class="subtitle">Data Analysis Dashboard | Updated: {analysis.get('last_updated', '')[:19]}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{analysis.get('total_tweets', 0)}</div>
                <div class="stat-label">Total Tweets</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analysis.get('original_tweets', 0)}</div>
                <div class="stat-label">Original</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analysis.get('replies', 0)}</div>
                <div class="stat-label">Replies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analysis.get('avg_daily', 0)}</div>
                <div class="stat-label">Avg/Day</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analysis.get('max_daily', 0)}</div>
                <div class="stat-label">Max Day</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analysis.get('data_days', 0)}</div>
                <div class="stat-label">Days Tracked</div>
            </div>
        </div>
        
        <div class="chart-section">
            <h3 class="chart-title">📈 Daily Trend</h3>
            <div class="chart-container">
                <img src="chart-trend.png" alt="Daily Trend">
            </div>
        </div>
        
        <div class="chart-section">
            <h3 class="chart-title">📆 Weekly Volume</h3>
            <div class="chart-container">
                <img src="chart-weekly.png" alt="Weekly Volume">
            </div>
        </div>
        
        <div class="chart-section">
            <h3 class="chart-title">📊 Distribution</h3>
            <div class="chart-container">
                <img src="chart-dist.png" alt="Distribution">
            </div>
        </div>
        
        <div class="footer">
            <p>Automated Analytics System | Data collected from public sources</p>
        </div>
    </div>
</body>
</html>'''
    
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML页面已生成: {HTML_FILE}")

def main():
    print(f"\n{'='*50}")
    print("  Tweet Analytics System")
    print(f"{'='*50}\n")
    
    # 1. 抓取数据
    df = fetch_tweets()
    
    if df is not None:
        # 2. 分析数据
        stats, analysis = analyze_data(df)
        
        if stats is not None:
            # 3. 生成图表
            generate_charts(stats, analysis)
            
            # 4. 生成HTML
            generate_html(stats, analysis)
    
    print("\n✅ 完成!")

if __name__ == "__main__":
    main()
