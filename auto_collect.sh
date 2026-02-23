#!/bin/bash
cd /home/admin/polymarket_musk_monitor

# 1. 收集数据
python3 collector.py >> collector.log 2>&1

# 2. 推送到GitHub
/home/admin/.openclaw/workspace/skills/github-deploy/push.sh /home/admin/polymarket_musk_monitor "Data update: $(date '+%m-%d %H:%M')"
