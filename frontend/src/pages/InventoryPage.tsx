import React, { useMemo, useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { Search, Filter, AlertCircle, Box, ArrowUpRight } from 'lucide-react';

const InventoryPage: React.FC = () => {
  const { products } = useSimulationStore();
  const [searchTerm, setSearchTerm] = useState('');

  const productList = useMemo(() => Object.values(products), [products]);
  
  const filteredProducts = productList.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.sku.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white">Inventory Management</h2>
          <p className="text-slate-400">Monitor stock levels and warehouse slotting across all zones.</p>
        </div>
        
        <div className="flex gap-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search SKUs or products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 bg-slate-900 border border-slate-800 rounded-xl focus:outline-none focus:border-cyan-600 transition-colors text-sm w-64"
            />
          </div>
          <button className="btn-secondary flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Filter
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-cyan-600/10 rounded-xl flex items-center justify-center">
            <Box className="text-cyan-500 w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{productList.length}</p>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-widest">Total SKUs</p>
          </div>
        </div>
        
        <div className="glass-card p-6 flex items-center gap-4">
          <div className="w-12 h-12 bg-emerald-600/10 rounded-xl flex items-center justify-center">
            <ArrowUpRight className="text-emerald-500 w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {productList.filter(p => p.velocity_class === 'A').length}
            </p>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-widest">High Velocity (Class A)</p>
          </div>
        </div>

        <div className="glass-card p-6 border-red-900/30 bg-red-900/5 flex items-center gap-4">
          <div className="w-12 h-12 bg-red-600/10 rounded-xl flex items-center justify-center">
            <AlertCircle className="text-red-500 w-6 h-6" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {productList.filter(p => p.current_stock <= p.reorder_threshold).length}
            </p>
            <p className="text-xs font-medium text-slate-500 uppercase tracking-widest text-red-500/70">Low Stock Alerts</p>
          </div>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-800/50 text-slate-400 text-[10px] font-bold uppercase tracking-widest border-b border-slate-800">
            <tr>
              <th className="px-6 py-4">Product / SKU</th>
              <th className="px-6 py-4">Velocity</th>
              <th className="px-6 py-4">Current Stock</th>
              <th className="px-6 py-4">Shelf Location</th>
              <th className="px-6 py-4">Demand Freq</th>
              <th className="px-6 py-4">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredProducts.map((p) => (
              <tr key={p.id} className="hover:bg-slate-800/20 transition-colors group">
                <td className="px-6 py-4">
                  <div className="flex flex-col">
                    <span className="text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition-colors">{p.name}</span>
                    <span className="text-[10px] font-mono text-slate-500">{p.sku}</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    p.velocity_class === 'A' ? 'bg-red-500/10 text-red-500' :
                    p.velocity_class === 'B' ? 'bg-amber-500/10 text-amber-500' :
                    'bg-blue-500/10 text-blue-500'
                  }`}>
                    CLASS {p.velocity_class}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-1.5 bg-slate-800 rounded-full w-24 overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${p.current_stock <= p.reorder_threshold ? 'bg-red-500' : 'bg-emerald-500'}`}
                        style={{ width: `${Math.min(100, (p.current_stock / 30) * 100)}%` }}
                      />
                    </div>
                    <span className={`text-sm font-bold ${p.current_stock <= p.reorder_threshold ? 'text-red-400' : 'text-slate-300'}`}>
                      {p.current_stock}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="text-sm font-mono text-slate-400">
                    {p.shelf_location ? `[${p.shelf_location[0]}, ${p.shelf_location[1]}]` : 'Unassigned'}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-400">
                  {p.demand_frequency.toFixed(2)}/hr
                </td>
                <td className="px-6 py-4">
                  <span className={`flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-tighter ${
                    p.current_stock <= p.reorder_threshold ? 'text-red-500' : 'text-emerald-500'
                  }`}>
                    <div className={`w-1.5 h-1.5 rounded-full ${
                      p.current_stock <= p.reorder_threshold ? 'bg-red-500 animate-pulse' : 'bg-emerald-500'
                    }`} />
                    {p.current_stock <= p.reorder_threshold ? 'Critical' : 'Healthy'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryPage;
