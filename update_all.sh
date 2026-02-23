#!/bin/bash
cd /home/admin/polymarket_musk_monitor

# 1. 获取新推文
python3 fetcher_final.py

# 2. 推送到 GitHub
/home/admin/.openclaw/workspace/skills/github-deploy/push.sh /home/admin/polymarket_musk_monitor "Update tweets: $(date '+%Y-%m-%d %H:%M')"

echo "=== 更新完成 ==="
