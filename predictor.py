#!/usr/bin/env python3
"""
推文预测模块
基于移动平均进行简单预测
"""

import json
import os
from datetime import datetime, timedelta

DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"
HISTORY_FILE = "/home/admin/polymarket_musk_monitor/data/history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def load_history():
    """加载历史每日快照"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def update_history():
    """更新历史记录"""
    data = load_data()
    daily = data.get('daily', {})
    history = load_history()
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 保存今天的计数
    if today in daily:
        count = daily[today].get('count', 0)
        if today not in history:
            history[today] = count
            save_history(history)
    
    return history

def calculate_predictions():
    """计算预测数据"""
    history = load_history()
    data = load_data()
    
    # 确保历史是最新的
    update_history()
    history = load_history()
    
    if len(history) < 1:
        return None
    
    # 获取所有日期的数据
    dates = sorted(history.keys())
    counts = [history[d] for d in dates]
    
    # 至少需要2天数据才能做趋势分析
    if len(counts) < 2:
        # 只有1天数据，返回简单估算
        return {
            "sma_3": counts[0] if counts else 0,
            "sma_7": counts[0] if counts else 0,
            "recent_avg": counts[0] if counts else 0,
            "trend": "➡️ 初始数据",
            "trend_pct": 0,
            "tomorrow_pred": counts[0] if counts else 10,
            "week_pred": (counts[0] * 7) if counts else 70,
            "data_days": len(counts),
            "note": "需要更多数据才能做准确预测",
            "last_updated": data.get('last_updated', '')
        }
    
    # 简单移动平均
    sma_3 = sum(counts[-3:]) / min(3, len(counts))
    sma_7 = sum(counts) / len(counts)
    
    # 趋势判断
    if len(counts) >= 3:
        recent_avg = sum(counts[-3:]) / 3
        older_avg = sum(counts[:-3]) / max(1, len(counts)-3)
    else:
        recent_avg = counts[-1]
        older_avg = counts[0] if len(counts) > 1 else counts[0]
    
    trend = "📈 上升" if recent_avg > older_avg else "📉 下降" if recent_avg < older_avg else "➡️ 平稳"
    trend_pct = ((recent_avg - older_avg) / max(older_avg, 1)) * 100
    
    # 预测
    tomorrow_pred = int(sma_3 * 1.05)  # 轻微上调
    week_pred = int(sma_7 * 7)
    
    return {
        "sma_3": round(sma_3, 1),
        "sma_7": round(sma_7, 1),
        "recent_avg": round(recent_avg, 1),
        "trend": trend,
        "trend_pct": round(trend_pct, 1),
        "tomorrow_pred": tomorrow_pred,
        "week_pred": week_pred,
        "data_days": len(counts),
        "history": {k:v for k,v in history.items()},
        "last_updated": data.get('last_updated', '')
    }

if __name__ == "__main__":
    result = calculate_predictions()
    if result:
        print("=== 🎯 推文预测 ===")
        print(f"历史数据: {result['data_days']} 天")
        print(f"3日均值: {result['sma_3']} 条/天")
        print(f"7日均值: {result['sma_7']} 条/天")
        print(f"当前趋势: {result['trend']} ({result['trend_pct']:+.1f}%)")
        print(f"")
        print(f"📊 预测:")
        print(f"  明日预测: {result['tomorrow_pred']} 条")
        print(f"  本周预测: {result['week_pred']} 条")
        if 'note' in result:
            print(f"  ⚠️ {result['note']}")
    else:
        print("数据不足，无法预测")
