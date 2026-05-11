import React, { useMemo, useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { 
  ShoppingBag, 
  Clock, 
  CheckCircle2, 
  MoreVertical, 
  ExternalLink,
  ChevronRight,
  User,
  MapPin
} from 'lucide-react';

const OrdersPage: React.FC = () => {
  const { orders, completed_orders_count } = useSimulationStore();
  const [activeTab, setActiveTab] = useState<'active' | 'completed'>('active');

  const activeOrders = useMemo(() => Object.values(orders), [orders]);

  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Fulfillment Hub</h2>
          <p className="text-slate-400">Manage incoming customer orders and track picker assignments in real-time.</p>
        </div>
        
        <div className="flex p-1 bg-slate-900 border border-slate-800 rounded-xl">
          <button 
            onClick={() => setActiveTab('active')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'active' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            Active ({activeOrders.length})
          </button>
          <button 
            onClick={() => setActiveTab('completed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'completed' ? 'bg-cyan-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'
            }`}
          >
            History ({completed_orders_count})
          </button>
        </div>
      </div>

      {activeTab === 'active' ? (
        <div className="grid grid-cols-1 gap-4">
          {activeOrders.length > 0 ? (
            activeOrders.map((order) => (
              <div key={order.id} className="glass-card p-6 flex items-center justify-between group hover:border-slate-600 transition-all">
                <div className="flex items-center gap-6">
                  <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                    order.status === 'pending' ? 'bg-amber-500/10 text-amber-500' : 'bg-cyan-500/10 text-cyan-500'
                  }`}>
                    <ShoppingBag className="w-6 h-6" />
                  </div>
                  
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <h4 className="text-lg font-bold text-white">Order #{order.id}</h4>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                        order.status === 'pending' ? 'bg-amber-500/10 text-amber-500' : 'bg-cyan-500/10 text-cyan-500'
                      }`}>
                        {order.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-slate-500">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(order.created_at * 1000).toLocaleTimeString()}</span>
                      <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3" /> {order.items.length} Items</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-12">
                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Assignment</span>
                    {order.assigned_picker_id !== null ? (
                      <div className="flex items-center gap-2">
                        <User className="w-3 h-3 text-cyan-400" />
                        <span className="text-sm font-bold text-slate-300">Picker {order.assigned_picker_id}</span>
                      </div>
                    ) : (
                      <span className="text-sm font-medium text-slate-600">Waiting for picker...</span>
                    )}
                  </div>

                  <div className="flex flex-col items-end gap-1">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Priority Route</span>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-3 h-3 text-slate-500" />
                      <span className="text-sm font-mono text-slate-400">{order.total_distance.toFixed(1)}m total</span>
                    </div>
                  </div>

                  <button className="p-2 text-slate-500 hover:text-white hover:bg-slate-800 rounded-lg transition-all">
                    <ChevronRight className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="glass-card p-12 flex flex-col items-center justify-center gap-4 opacity-50">
              <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center text-slate-600">
                <ShoppingBag className="w-8 h-8" />
              </div>
              <p className="text-slate-400 font-medium">No active orders in the queue</p>
            </div>
          )}
        </div>
      ) : (
        <div className="glass-card p-12 text-center text-slate-500">
           Order history view is currently being optimized for high-volume data.
        </div>
      )}
    </div>
  );
};

export default OrdersPage;
