#!/usr/bin/env python3
"""
私人数据看板 - 带认证 + React 前端
"""

from flask import Flask, request, jsonify, send_from_directory
import json
import os
from functools import wraps

app = Flask(__name__, static_folder='react-app/public')

# 配置
USERNAME = "admin"
PASSWORD = "cong123456"

DATA_FILE = "/home/admin/polymarket_musk_monitor/data/stats.json"
TWEETS_FILE = "/home/admin/polymarket_musk_monitor/data/all_tweets.json"

def check_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != USERNAME or auth.password != PASSWORD:
            return ('需要认证', 401, {'WWW-Authenticate': 'Basic realm="Private"'})
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@check_auth
def index():
    return send_from_directory('react-app/public', 'index.html')

@app.route('/<path:filename>')
@check_auth
def static_files(filename):
    return send_from_directory('react-app/public', filename)

@app.route('/api')
@check_auth
def api():
    data = {}
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
