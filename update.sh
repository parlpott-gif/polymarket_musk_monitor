#!/bin/bash
# 马斯克推文监控自动更新脚本

cd ~/polymarket_musk_monitor

# 设置Git配置
git config user.email "admin@example.com"
git config user.name "OpenClaw"

# 添加所有更改
git add .

# 检查是否有更改
if git diff --staged --quiet; then
    echo "没有新内容需要推送"
    exit 0
fi

# 提交更改
git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"

# 推送到GitHub
git push origin main

echo "推送完成: $(date)"
