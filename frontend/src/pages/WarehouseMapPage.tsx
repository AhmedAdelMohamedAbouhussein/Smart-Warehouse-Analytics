import React from 'react';
import WarehouseCanvas from '../components/Warehouse/WarehouseCanvas';
import { useSimulationStore } from '../store/simulationStore';
import { Info, Maximize2 } from 'lucide-react';

const MapPage: React.FC = () => {
  const { layout } = useSimulationStore();

  return (
    <div className="h-full flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-col gap-1">
          <h2 className="text-3xl font-bold text-white tracking-tight">Warehouse Floor Plan</h2>
          <p className="text-slate-400">Real-time spatial visualization of the picking environment and robot fleet.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="glass-card px-4 py-2 flex items-center gap-3">
            <Info className="w-4 h-4 text-cyan-400" />
            <span className="text-xs text-slate-300">Use <kbd className="bg-slate-800 px-1 rounded text-cyan-400 font-mono">Scroll</kbd> to Zoom and <kbd className="bg-slate-800 px-1 rounded text-cyan-400 font-mono">Drag</kbd> to Pan</span>
          </div>
          {layout && (
            <div className="glass-card px-4 py-2 border-emerald-500/20">
              <span className="text-xs font-bold text-emerald-500 uppercase tracking-widest">{layout.rows} x {layout.cols} Grid</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 glass-card overflow-hidden relative border-slate-700/50 min-h-[600px]">
        <div className="absolute top-4 left-4 z-10">
          <div className="bg-slate-900/80 backdrop-blur-md border border-slate-700/50 p-3 rounded-xl shadow-2xl flex items-center gap-4">
            <div className="flex items-center gap-2 pr-4 border-r border-slate-800">
              <div className="w-2.5 h-2.5 bg-slate-700 border border-slate-600 rounded-sm" />
              <span className="text-[10px] font-bold text-slate-400 uppercase">Shelf</span>
            </div>
            <div className="flex items-center gap-2 pr-4 border-r border-slate-800">
              <div className="w-2.5 h-2.5 bg-emerald-500/20 border border-emerald-500 rounded-sm" />
              <span className="text-[10px] font-bold text-slate-400 uppercase">Dock</span>
            </div>
            <div className="flex items-center gap-2 pr-4 border-r border-slate-800">
              <div className="w-2.5 h-2.5 bg-amber-500/20 border border-amber-500 rounded-sm" />
              <span className="text-[10px] font-bold text-slate-400 uppercase">Station</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2.5 h-2.5 rounded-full border border-white bg-cyan-500" />
              <span className="text-[10px] font-bold text-slate-400 uppercase">Robot</span>
            </div>
          </div>
        </div>
        
        <div className="absolute bottom-6 left-6 z-10">
           <button className="bg-slate-900/90 hover:bg-slate-800 backdrop-blur-md border border-slate-700/50 p-2 rounded-lg transition-all">
             <Maximize2 className="w-4 h-4 text-slate-400" />
           </button>
        </div>

        <WarehouseCanvas />
      </div>
    </div>
  );
};

export default MapPage;

