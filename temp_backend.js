function renderBackend() {
      document.querySelectorAll('.menu-item').forEach(el => el.classList.remove('active'));
      document.getElementById('btn-backend').classList.add('active');
      
      const tweets = [];
      Object.entries(tweetData.daily||{}).forEach(([date,info])=>{
        (info.tweets||[]).forEach(t=>{
          tweets.push({date, time:t.time?.slice(11,19), hour:parseInt(t.time?.slice(11,13)||'0'), content:t.content});
        });
      });
      
      // 统计每小时发布数量
      const hourlyCounts = new Array(24).fill(0);
      tweets.forEach(t => {
        if (t.hour >= 0 && t.hour < 24) hourlyCounts[t.hour]++;
      });
      
      const maxHour = Math.max(...hourlyCounts, 1);
      
      // 统计每日数量
      const dailyCounts = {};
      tweets.forEach(t => { dailyCounts[t.date] = (dailyCounts[t.date]||0)+1; });
      const dailyArr = Object.entries(dailyCounts).sort((a,b)=>a[0].localeCompare(b[0])).slice(-14);
      const maxDaily = Math.max(...dailyArr.map(d=>d[1]),1);
      
      // 统计摘要
      const totalTweets = tweets.length;
      const avgDaily = (totalTweets / Math.max(Object.keys(dailyCounts).length,1)).toFixed(1);
      const peakHour = hourlyCounts.indexOf(Math.max(...hourlyCounts));
      const peakDay = dailyArr.sort((a,b)=>b[1]-a[1])[0];
      
      // 生成时段热力图 HTML
      let heatmapHTML = '<div style="display:grid;grid-template-columns:repeat(24,1fr);gap:2px;margin-top:16px;">';
      for (let h=0; h<24; h++) {
        const intensity = hourlyCounts[h] / maxHour;
        const color = `rgba(59,130,246,${0.1 + intensity * 0.9})`;
        heatmapHTML += `<div style="background:${color};height:40px;border-radius:4px;position:relative;" title="${h}:00 - ${hourlyCounts[h]}条">
          <span style="position:absolute;bottom:-20px;left:50%;transform:translateX(-50%);font-size:10px;color:#64748b">${h}</span>
        </div>`;
      }
      heatmapHTML += '</div>';
      
      document.getElementById('main').innerHTML = `
        <div class="header"><h1>📊 后端数据</h1></div>
        
        <!-- 统计摘要 -->
        <div class="stats-grid" style="grid-template-columns:repeat(5,1fr);">
          <div class="stat-card">
            <div class="stat-value">${totalTweets}</div><div class="stat-label">总推文</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${avgDaily}</div><div class="stat-label">日均</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${peakHour}:00</div><div class="stat-label">高峰时段</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${peakDay?.[1]||0}</div><div class="stat-label">最高单日</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${Object.keys(dailyCounts).length}</div><div class="stat-label">数据天数</div>
          </div>
        </div>
        
        <!-- 时段热力图 -->
        <div class="card">
          <div class="card-title">🕐 时段热力图 (24小时发布分布)</div>
          ${heatmapHTML}
          <div style="display:flex;justify-content:space-between;margin-top:30px;font-size:11px;color:#64748b;">
            <span>深蓝 = 高频率</span><span>浅蓝 = 低频率</span>
          </div>
        </div>
        
        <!-- 每日趋势图 -->
        <div class="card">
          <div class="card-title">📈 最近14天推文数量</div>
          <div style="display:flex;align-items:flex-end;gap:4px;height:150px;padding:10px 0;">
            ${dailyArr.map(d=>`
              <div style="flex:1;display:flex;flex-direction:column;align-items:center;">
                <div style="width:100%;background:linear-gradient(180deg,#3b82f6,#60a5fa);border-radius:4px 4px 0 0;height:${(d[1]/maxDaily)*120}px;" title="${d[0]}: ${d[1]}条"></div>
                <span style="font-size:9px;color:#64748b;margin-top:4px;">${d[0].slice(5)}</span>
              </div>
            `).join('')}
          </div>
        </div>
        
        <!-- 原始数据表格 -->
        <div class="card">
          <div class="card-title">📋 原始数据 (${tweets.length}条)</div>
          <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <tr style="border-bottom:2px solid var(--border);">
              <th style="text-align:left;padding:10px;color:#64748b;font-size:12px;">日期</th>
              <th style="text-align:left;padding:10px;color:#64748b;font-size:12px;">时间</th>
              <th style="text-align:left;padding:10px;color:#64748b;font-size:12px;">内容预览</th>
            </tr>
            ${tweets.slice(0,30).map(t=>`
              <tr style="border-bottom:1px solid var(--border);">
                <td style="padding:10px;">${t.date}</td>
                <td style="padding:10px;font-family:monospace;">${t.time}</td>
                <td style="padding:10px;max-width:400px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${t.content}">${t.content}</td>
              </tr>
            `).join('')}
          </table>
        </div>
      `;
    }