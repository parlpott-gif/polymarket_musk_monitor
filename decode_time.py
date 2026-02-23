#!/usr/bin/env python3
"""
从推文ID解析发布时间
Twitter Snowflake ID 包含时间信息
"""

def snowflake_to_time(tweet_id):
    """从推文ID解析时间"""
    try:
        # Twitter epoch: 1288834974657 ms (Nov 4, 2010)
        twitter_epoch = 1288834974657
        
        # 提取时间戳（ID的前41位）
        tweet_id = int(tweet_id)
        timestamp_ms = ((tweet_id >> 22) + twitter_epoch)
        
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp_ms / 1000)
        return dt
    except:
        return None

# 测试
test_ids = [
    "2024727442427171118",
    "2024723187251236967",
    "2023880206721970544",
]

print("从 ID 解析时间:")
for id in test_ids:
    dt = snowflake_to_time(id)
    print(f"  {id[:10]}... -> {dt}")
