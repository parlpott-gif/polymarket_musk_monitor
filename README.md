# 🎯 Musk Tweet Monitor - 马斯克推文监控系统

## 项目结构

```
polymarket_musk_monitor/
├── src/
│   ├── collectors/       # 数据采集模块
│   │   └── collector.py  # 推文数据采集
│   ├── api/             # API 服务
│   │   └── server.py    # Flask Web 服务
│   └── web/             # 前端页面
│       └── index.html   # 可视化界面
├── data/                # 数据存储
│   ├── all_tweets.json  # 全部推文
│   └── stats.json       # 统计数据
├── logs/                # 日志目录
├── auto_collect.sh      # 自动采集脚本
└── README.md
```

## 功能模块

### 1. 数据采集 (collectors/)
- `collector.py` - 从 xcancel.com 抓取马斯克推文
- 每小时自动执行
- 数据存储到 data/

### 2. API 服务 (api/)
- `server.py` - Flask 服务器
- 提供数据 API
- 端口: 8080

### 3. 前端界面 (web/)
- `index.html` - 可视化仪表盘
- 页面：
  - 📊 实时概览 - 推文统计、趋势图
  - 📊 后端数据 - 时段热力图、原始数据
  - 🎯 预测市场 - Polymarket 盘口

## 启动方式

```bash
# 启动 API 服务
python3 src/api/server.py

# 手动采集数据
python3 src/collectors/collector.py
```

## 自动任务

通过 cron 设置：
```bash
0 * * * * /home/admin/polymarket_musk_monitor/auto_collect.sh
```

## 外部依赖

- xcancel.com - 推文数据源
- Polymarket API - 预测市场数据
- GitHub - 数据备份

## TODO

- [ ] 预测功能 - 基于历史数据的推文数量预测
- [ ] 情绪分析 - 推文内容情感分析
- [ ] 盘口关联 - 推文频率与市场价格相关性
