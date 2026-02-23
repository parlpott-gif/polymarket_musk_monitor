import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Cell, AreaChart, Area, PieChart, Pie } from 'recharts';
import { Bird, TrendingUp, Activity, LayoutDashboard, Database, Wallet, Hash, RefreshCw } from 'lucide-react';

// 获取真实数据
const useRealData = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api')
      .then(res => res.json())
      .then(d => {
        // 转换每日数据
        const dailyData = Object.entries(d.daily || {})
          .sort(([a], [b]) => a.localeCompare(b))
          .slice(-14)
          .map(([date, info]) => ({
            name: date.slice(5), // MM-DD
            count: info.count
          }));
        
        // 转换每小时数据
        const hourlyData = Object.entries(d.daily[Object.keys(d.daily).pop()]?.hourly || {})
          .map(([h, c]) => ({ h, c }));
        
        setData({
          daily: dailyData,
          hourly: hourlyData,
          total: d.total_tweets || 0,
          today: d.daily[Object.keys(d.daily).pop()]?.count || 0,
          lastUpdate: d.last_updated
        });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  return { data, loading };
};

// 侧边导航
const Sidebar = ({ activePage, setActivePage }) => {
  const menuItems = [
    { id: 'dashboard', label: '实时概览', icon: LayoutDashboard },
    { id: 'backend', label: '后端数据台', icon: Database },
  ];

  return (
    <div className="w-full md:w-64 bg-slate-950 border-r border-slate-800 flex flex-col p-4">
      <div className="flex items-center gap-3 px-2 mb-10">
        <Bird className="text-blue-500 fill-blue-500" size={32} />
        <h1 className="text-xl font-bold text-white tracking-tight">MUSK MONITOR</h1>
      </div>
      <nav className="space-y-2 flex-1">
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActivePage(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
              activePage === item.id 
              ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20' 
              : 'text-slate-400 hover:bg-slate-900 hover:text-white'
            }`}
          >
            <item.icon size={20} />
            <span className="font-medium">{item.label}</span>
          </button>
        ))}
      </nav>
      <div className="p-4 bg-slate-900/50 rounded-2xl border border-slate-800">
        <div className="flex items-center gap-2 mb-2">
          <Activity size={14} className="text-emerald-500" />
          <span className="text-xs font-bold text-slate-300">系统状态: 运行中</span>
        </div>
      </div>
    </div>
  );
};

// Dashboard 页面
const DashboardPage = ({ data }) => (
  <div className="space-y-6 animate-in fade-in duration-500">
    <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <StatCard title="今日推文" value={data?.today || 0} sub="实时" icon={Bird} color="bg-blue-500" />
      <StatCard title="总推文数" value={data?.total || 0} sub="累计" icon={Database} color="bg-purple-500" />
      <StatCard title="数据天数" value={data?.daily?.length || 0} sub="记录中" icon={Activity} color="bg-orange-500" />
      <StatCard title="系统状态" value="正常" sub="在线" icon={TrendingUp} color="bg-emerald-500" />
    </section>
    
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h2 className="text-lg font-bold text-white mb-6">推文发布趋势 (近14天)</h2>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data?.daily || []}>
              <defs>
                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }} />
              <Area type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={3} fill="url(#colorCount)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h2 className="text-lg font-bold text-white mb-6">今日发布时段</h2>
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data?.hourly || []}>
              <Bar dataKey="c" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              <XAxis dataKey="h" axisLine={false} tickLine={false} tick={{fontSize: 10}} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  </div>
);

// Backend 页面
const BackendPage = ({ data }) => {
  const tweets = [];
  // 从数据中提取推文
  Object.entries(data?.daily || {}).forEach(([date, info]) => {
    (info.tweets || []).forEach(t => {
      tweets.push({
        time: t.time?.slice(11, 19) || '',
        date,
        content: t.content || ''
      });
    });
  });

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold text-white">原始推文数据</h2>
            <p className="text-slate-500 text-sm">共 {tweets.length} 条记录</p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-slate-800 text-slate-500 text-xs uppercase">
                <th className="px-4 py-3">日期</th>
                <th className="px-4 py-3">时间</th>
                <th className="px-4 py-3">内容</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {tweets.slice(0, 50).map((t, i) => (
                <tr key={i} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3 text-xs text-slate-400">{t.date}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-400">{t.time}</td>
                  <td className="px-4 py-3 text-sm text-white max-w-md truncate">{t.content}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, sub, icon: Icon, color }) => (
  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 flex flex-col">
    <div className={`p-2 rounded-lg ${color} w-fit mb-3`}>
      <Icon size={20} className="text-white" />
    </div>
    <h3 className="text-slate-400 text-sm font-medium">{title}</h3>
    <p className="text-3xl font-bold text-white mt-1">{value}</p>
    <span className="text-xs text-slate-500 mt-1">{sub}</span>
  </div>
);

const App = () => {
  const [activePage, setActivePage] = useState('dashboard');
  const { data, loading } = useRealData();

  if (loading) {
    return <div className="min-h-screen bg-black text-white flex items-center justify-center">加载中...</div>;
  }

  return (
    <div className="flex flex-col md:flex-row min-h-screen bg-black text-slate-200 font-sans">
      <Sidebar activePage={activePage} setActivePage={setActivePage} />
      <div className="flex-1 flex flex-col h-screen overflow-y-auto">
        <header className="sticky top-0 z-10 bg-black/80 backdrop-blur-md border-b border-slate-800 p-4 px-8 flex items-center justify-between">
          <h2 className="text-lg font-bold text-white">
            {activePage === 'dashboard' ? '实时概览' : '后端数据台'}
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            更新: {data?.lastUpdate?.slice(0, 19) || 'N/A'}
          </span>
        </header>
        <main className="p-4 md:p-8 max-w-7xl w-full mx-auto">
          {activePage === 'dashboard' && <DashboardPage data={data} />}
          {activePage === 'backend' && <BackendPage data={data} />}
        </main>
      </div>
    </div>
  );
};

export default App;
