import React, { useEffect, useMemo, useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from 'recharts';
import { BarChart3, TrendingUp, Zap, Clock, PackageCheck } from 'lucide-react';
import KPICard from '../components/Analytics/KPICard';

const AnalyticsPage: React.FC = () => {
  const { metrics, pickers, layout, history, products, replenishment, events } = useSimulationStore();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const pickerData = useMemo(() =>
    Object.values(pickers || {}).map(p => ({
      name: p.name,
      orders: p.orders_completed,
      distance: Math.round(p.total_distance_traveled),
      utilization: Math.round((p.total_active_time / (p.total_active_time + p.total_idle_time || 1)) * 100)
    })), [pickers]);

  const zoneData = useMemo(() => {
    if (!layout) return [];
    const counts = { A: 0, B: 0, C: 0, S: 0 };
    layout.grid.forEach(row => row.forEach(cell => {
      const z = cell.zone;
      const visits = cell.visit_count || 0;
      if (visits > 0) {
        if (cell.cell_type === 'pick_station') counts.S += visits;
        else if (z === 'A') counts.A += visits;
        else if (z === 'B') counts.B += visits;
        else if (z === 'C') counts.C += visits;
      }
    }));
    const total = counts.A + counts.B + counts.C + counts.S || 1;
    return [
      { name: 'Zone A', value: Math.round((counts.A / total) * 100), color: '#ef4444' },
      { name: 'Zone B', value: Math.round((counts.B / total) * 100), color: '#f59e0b' },
      { name: 'Zone C', value: Math.round((counts.C / total) * 100), color: '#3b82f6' },
      { name: 'Station', value: Math.round((counts.S / total) * 100), color: '#fbbf24' },
    ];
  }, [layout]);

  const throughputData = useMemo(() => {
    if (!history || !history.ticks) return [];
    return history.ticks.map((t, i) => ({
      tick: t,
      throughput: history.throughput[i] || 0,
      utilization: history.utilization[i] || 0
    }));
  }, [history]);

  const stockMetrics = useMemo(() => {
    const productsList = Object.values(products || {});
    const lowStock = productsList.filter(p => p.current_stock <= p.reorder_threshold).length;
    const outOfStock = productsList.filter(p => p.current_stock === 0).length;
    return {
      availability: productsList.length > 0
        ? Math.round(((productsList.length - outOfStock) / productsList.length) * 100)
        : 0,
      lowStock
    };
  }, [products]);

  return (
    <div className="space-y-8 animate-in fade-in duration-700 pb-12">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-white">Picker Efficiency Dashboard</h2>
        <p className="text-slate-400">Comparing real-time greedy assignment against DP-optimized pick routes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <KPICard
          label="Orders / Min"
          value={metrics.orders_per_minute}
          icon={TrendingUp}
          color="bg-emerald-500"
        />
        <KPICard
          label="Picker Status"
          value={`${metrics.active_pickers}/${Object.keys(pickers).length}`}
          icon={Zap}
          color="bg-violet-500"
        />
        <KPICard
          label="Avg Cycle Time"
          value={`${metrics.avg_cycle_time.toFixed(1)}s`}
          icon={Clock}
          color="bg-cyan-500"
        />
        <KPICard
          label="Shift Distance"
          value={`${metrics.total_distance.toFixed(0)}m`}
          icon={BarChart3}
          color="bg-blue-500"
        />
        <KPICard
          label="Stock Health"
          value={`${stockMetrics.availability}%`}
          icon={PackageCheck}
          color="bg-amber-500"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card p-8 space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Fulfillment Velocity Trend</h3>
            <div className="flex gap-4">
              <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500" /> <span className="text-[10px] text-slate-500 uppercase">Throughput</span></div>
              <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-violet-500" /> <span className="text-[10px] text-slate-500 uppercase">Utilization</span></div>
            </div>
          </div>
          <div className="w-full relative min-h-[300px]">
            {isMounted && (
              <ResponsiveContainer width="100%" aspect={2.5} minWidth={0} debounce={100}>
                <LineChart data={throughputData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="tick" hide />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }}
                  />
                  <Line type="monotone" dataKey="throughput" stroke="#10b981" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="utilization" stroke="#8b5cf6" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="glass-card p-8 space-y-6">
          <h3 className="text-lg font-bold text-white">Traffic Analysis</h3>
          <div className="w-full flex flex-col items-center justify-center relative min-h-[300px]">
            {isMounted && (
              <ResponsiveContainer width="100%" aspect={1} minWidth={0} debounce={100}>
                <PieChart>
                  <Pie data={zoneData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value">
                    {zoneData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.6} stroke={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4 w-full mt-4">
            {zoneData.map((item) => (
              <div key={item.name} className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-[10px] text-slate-400 font-medium">{item.name} ({item.value}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Picker Performance Chart */}
        <div className="glass-card p-8 space-y-6">
          <h3 className="text-lg font-bold text-white">Individual Picker Efficiency</h3>
          <div className="w-full relative min-h-[350px]">
            {isMounted && (
              <ResponsiveContainer width="100%" aspect={2} minWidth={0} debounce={100}>
                <BarChart data={pickerData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                  <Tooltip cursor={{ fill: '#1e293b' }} contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px' }} />
                  <Bar dataKey="utilization" radius={[6, 6, 0, 0]}>
                    {pickerData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={Object.values(pickers || {})[index]?.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Replenishment Log */}
        <div className="glass-card flex flex-col">
          <div className="p-6 border-b border-slate-800 flex justify-between items-center">
            <h3 className="text-lg font-bold text-white">Replenishment Log</h3>
            <span className="text-[10px] font-bold text-amber-500 bg-amber-500/10 px-2 py-1 rounded">Threshold Trigger: {replenishment.completed_count} Events</span>
          </div>
          <div className="flex-1 overflow-y-auto max-h-[350px] scrollbar-thin">
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-slate-900 text-slate-500 font-bold uppercase tracking-widest text-[10px]">
                <tr>
                  <th className="px-6 py-3">Product</th>
                  <th className="px-6 py-3">Qty</th>
                  <th className="px-6 py-3">Destination</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {events.filter(e => e.type === 'replenishment').reverse().slice(0, 10).map((event, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="px-6 py-4 text-slate-300 font-medium">{event.message.split(' ')[1]}</td>
                    <td className="px-6 py-4 text-slate-400">{event.message.split('qty: ')[1]?.split(')')[0] || '--'}</td>
                    <td className="px-6 py-4 text-slate-500 font-mono">Shelf Cell</td>
                    <td className="px-6 py-4">
                      <span className="text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded text-[9px] font-bold">COMPLETED</span>
                    </td>
                  </tr>
                ))}
                {events.filter(e => e.type === 'replenishment').length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-slate-600 italic">No replenishment events recorded yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
