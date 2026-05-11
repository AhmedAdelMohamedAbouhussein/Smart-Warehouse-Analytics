import React from 'react';
import { useSimulationStore } from '../store/simulationStore';
import WarehouseCanvas from '../components/Warehouse/WarehouseCanvas';
import KPICard from '../components/Analytics/KPICard';
import { 
  Package, 
  Truck, 
  Users, 
  Move, 
  History, 
  AlertTriangle,
  Activity
} from 'lucide-react';

const DashboardPage: React.FC = () => {
  const { metrics, events, pickers } = useSimulationStore();

  return (
    <div className="grid grid-cols-12 gap-6 animate-in fade-in duration-700">
      {/* KPI Section */}
      <div className="col-span-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          label="Total Distance" 
          value={`${metrics.total_distance.toLocaleString()} m`}
          icon={Move}
          color="bg-cyan-500"
          trend="+12%"
        />
        <KPICard 
          label="Active Orders" 
          value={metrics.active_orders}
          icon={Package}
          color="bg-emerald-500"
        />
        <KPICard 
          label="Completed Orders" 
          value={metrics.completed_orders}
          icon={Truck}
          color="bg-blue-500"
          trend="+4.2%"
        />
        <KPICard 
          label="Avg. Utilization" 
          value={`${metrics.avg_utilization}%`}
          icon={Users}
          color="bg-violet-500"
        />
      </div>

      {/* Main Content Area */}
      <div className="col-span-12 lg:col-span-8 h-[650px] space-y-6">
        <div className="h-full glass-card overflow-hidden relative group">
          <div className="absolute top-4 left-4 z-10">
            <h3 className="text-sm font-bold text-slate-400 bg-slate-900/80 backdrop-blur px-3 py-1 rounded-full border border-slate-700/50">
              Live Floor View
            </h3>
          </div>
          <WarehouseCanvas />
        </div>
      </div>

      {/* Sidebar Content Area */}
      <div className="col-span-12 lg:col-span-4 h-[650px] flex flex-col gap-6">
        {/* Picker Status */}
        <div className="glass-card flex-1 p-6 flex flex-col gap-4 overflow-hidden">
          <div className="flex items-center justify-between">
            <h3 className="font-bold text-slate-200">Picker Fleet</h3>
            <span className="text-xs font-medium text-slate-500 uppercase tracking-widest">
              {Object.keys(pickers).length} Active
            </span>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin space-y-3">
            {Object.values(pickers).map(picker => (
              <div key={picker.id} className="p-3 bg-slate-800/30 rounded-xl border border-slate-700/30 flex items-center justify-between group hover:border-slate-600 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: picker.color }} />
                  <div>
                    <p className="text-sm font-bold text-slate-200">{picker.name}</p>
                    <p className="text-[10px] text-slate-500 font-medium uppercase tracking-tighter">
                      {picker.status}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs font-mono text-slate-400">{Math.round(picker.total_distance_traveled)}m</p>
                  <p className="text-[10px] text-emerald-500 font-bold">{picker.orders_completed} orders</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live Event Log */}
        <div className="glass-card flex-1 p-6 flex flex-col gap-4 overflow-hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-slate-500" />
              <h3 className="font-bold text-slate-200">Event Log</h3>
            </div>
            <div className="flex gap-1">
              <div className="w-1 h-1 bg-slate-700 rounded-full" />
              <div className="w-1 h-1 bg-slate-700 rounded-full" />
              <div className="w-1 h-1 bg-slate-700 rounded-full" />
            </div>
          </div>
          <div className="flex-1 overflow-y-auto pr-2 scrollbar-thin space-y-3">
            {events.slice().reverse().map((event, idx) => (
              <div key={idx} className="flex gap-3 animate-in slide-in-from-right duration-300">
                <div className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${
                  event.type === 'error' ? 'bg-red-500' :
                  event.type === 'warning' ? 'bg-amber-500' :
                  'bg-cyan-500'
                }`} />
                <div className="space-y-0.5">
                  <p className="text-[11px] font-medium text-slate-300 leading-tight">
                    {event.message}
                  </p>
                  <span className="text-[9px] font-mono text-slate-600 uppercase">
                    Tick {event.tick}
                  </span>
                </div>
              </div>
            ))}
            {events.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-2 opacity-50">
                <Activity className="w-8 h-8" />
                <p className="text-xs font-medium">Monitoring system traffic...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
