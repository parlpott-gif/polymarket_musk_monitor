import json
from collections import defaultdict

tweets_path = "/home/admin/polymarket_musk_monitor/data/all_tweets.json"
stats_path = "/home/admin/polymarket_musk_monitor/data/stats.json"

# 读取推文数据
with open(tweets_path) as f:
    tweets = json.load(f)

# 按日期统计
daily_counts = defaultdict(int)
for tweet in tweets:
    date = tweet.get("date")
    if date:
        daily_counts[date] += 1

print(f"按日期统计: {dict(daily_counts)}")

# 读取stats
with open(stats_path) as f:
    stats = json.load(f)

# 更新daily字段
stats["daily"] = {}
for date, count in daily_counts.items():
    stats["daily"][date] = {
        "count": count,
        "tweets": [],
        "hourly": {}
    }

# 更新总数
stats["total_tweets"] = sum(daily_counts.values())

# 保存
with open(stats_path, "w") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print(f"已更新: 总计 {stats['total_tweets']} 条推文, {len(daily_counts)} 天")
