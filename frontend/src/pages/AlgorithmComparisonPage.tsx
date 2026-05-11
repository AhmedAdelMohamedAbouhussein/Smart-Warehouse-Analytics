import React, { useState, useMemo, useEffect } from 'react';
import { 
  Zap, 
  Route as RouteIcon, 
  PackageCheck, 
  ArrowRightLeft, 
  ChevronRight,
  Play,
  RotateCcw,
  BarChart as BarChartIcon,
  MousePointer2
} from 'lucide-react';
import { useSimulationStore } from '../store/simulationStore';
import WarehouseCanvas, { WarehouseCanvasProps } from '../components/Warehouse/WarehouseCanvas';

type AlgorithmTab = 'dijkstra' | 'bin_packing' | 'tsp' | 'assignment';

const AlgorithmComparisonPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<AlgorithmTab>('dijkstra');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  // Dynamic Inputs
  const [inputs, setInputs] = useState({
    dijkstra: { sR: 28, sC: 2, tR: 2, tC: 40 },
    tsp: { sR: 28, sC: 2, count: 8 },
    binPacking: { numProducts: 50 },
    assignment: { tR: 7, tC: 48 }
  });

  // Clear results on tab change
  useEffect(() => {
    setResults(null);
  }, [activeTab]);

  const updateInput = (tab: keyof typeof inputs, field: string, val: number) => {
    setInputs(prev => ({
      ...prev,
      [tab]: { ...prev[tab], [field]: val }
    }));
  };

  const runDijkstra = async () => {
    setLoading(true);
    try {
      const { sR, sC, tR, tC } = inputs.dijkstra;
      const res = await fetch('/api/algorithms/dijkstra', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ source: [sR, sC], target: [tR, tC] })
      });
      const data = await res.json();
      setResults(data.result);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const runBinPacking = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/algorithms/bin-packing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          num_products: inputs.binPacking.numProducts,
          rerun: true 
        })
      });
      const data = await res.json();
      setResults(data.result);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const runTSP = async () => {
    setLoading(true);
    try {
      const { sR, sC, count } = inputs.tsp;
      const res = await fetch('/api/algorithms/held-karp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          start: [sR, sC], 
          num_random: count,
          locations: [] 
        })
      });
      const data = await res.json();
      setResults(data.result);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const runAssignment = async () => {
    setLoading(true);
    try {
      const { tR, tC } = inputs.assignment;
      const res = await fetch('/api/algorithms/greedy-assignment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          custom_location: [tR, tC] 
        })
      });
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  // Memoize highlight props for the canvas
  const canvasProps = useMemo<WarehouseCanvasProps>(() => {
    if (!results) return {};

    if (activeTab === 'dijkstra') {
      return {
        highlightPath: results.path,
        highlightExplored: results.explored,
        highlightEdges: results.explored_edges,
        highlightPoints: [
          { pos: [inputs.dijkstra.sR, inputs.dijkstra.sC], color: '#10b981', label: 'Start' },
          { pos: [inputs.dijkstra.tR, inputs.dijkstra.tC], color: '#ef4444', label: 'End' }
        ]
      };
    }

    if (activeTab === 'tsp' && results.coordinates) {
      const points = results.coordinates.map((pos: any, i: number) => ({
        pos: pos as [number, number],
        color: i === 0 ? '#10b981' : '#3b82f6',
        label: i === 0 ? 'Start' : `Pick ${i}`
      }));
      return { highlightPoints: points };
    }

    if (activeTab === 'bin_packing' && results.steps) {
      // Group placements by bin to avoid text overlap
      const binGroups: Record<string, { pos: [number, number], zone: string, count: number, names: string[] }> = {};
      
      results.steps.forEach((s: any) => {
        if (s.action === 'place') {
          const key = `${s.bin_location[0]},${s.bin_location[1]}`;
          if (!binGroups[key]) {
            binGroups[key] = { pos: s.bin_location, zone: s.zone, count: 0, names: [] };
          }
          binGroups[key].count++;
          if (binGroups[key].names.length < 2) binGroups[key].names.push(s.item_name || `P${s.item_id}`);
        }
      });

      const highlights = Object.values(binGroups).map(group => ({
        pos: group.pos,
        color: group.zone === 'A' ? '#ef4444' : group.zone === 'B' ? '#f59e0b' : '#3b82f6',
        label: group.count > 1 ? `${group.count} Items` : group.names[0]
      }));

      return { highlightPoints: highlights };
    }

    if (activeTab === 'assignment' && results.assignment && results.assignment.picker) {
      const picker = results.assignment.picker;
      const target = results.assignment.order?.shelf_location || [inputs.assignment.tR, inputs.assignment.tC];
      return {
        highlightPoints: [
          { pos: picker.current_position as [number, number], color: '#a855f7', label: 'Assigned Picker' },
          { pos: target as [number, number], color: '#10b981', label: 'Target Order' }
        ],
        highlightPath: [picker.current_position, target] 
      };
    }

    return {};
  }, [results, activeTab, inputs]);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold text-white tracking-tight">Algorithm Lab</h2>
        <p className="text-slate-400 max-w-2xl">
          Visual demonstration and performance benchmarking of the core optimization engines used in the warehouse system.
        </p>
      </div>

      <div className="flex flex-wrap gap-4 p-1 bg-slate-900/50 rounded-2xl border border-slate-800 w-fit">
        {[
          { id: 'dijkstra', icon: RouteIcon, label: 'Dijkstra' },
          { id: 'bin_packing', icon: PackageCheck, label: 'Bin Packing' },
          { id: 'tsp', icon: ArrowRightLeft, label: 'TSP (Held-Karp)' },
          { id: 'assignment', icon: Zap, label: 'Order Assignment' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id as AlgorithmTab); setResults(null); }}
            className={`
              flex items-center gap-3 px-6 py-3 rounded-xl font-medium transition-all duration-200
              ${activeTab === tab.id 
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-900/40' 
                : 'text-slate-500 hover:text-slate-300 hover:bg-slate-800/50'}
            `}
          >
            <tab.icon className="w-5 h-5" />
            {tab.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-12 gap-8">
        {/* Controls Panel */}
        <div className="col-span-12 lg:col-span-4 space-y-6">
          <div className="glass-card p-8 space-y-6">
            <div className="space-y-2">
              <h3 className="text-xl font-bold text-white">Configuration</h3>
              <p className="text-sm text-slate-400">Modify inputs to test algorithm robustness.</p>
            </div>

            <div className="space-y-6">
              {activeTab === 'dijkstra' && (
                <div className="space-y-4">
                   <div className="grid grid-cols-2 gap-4">
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Start Row</label>
                        <input type="number" value={inputs.dijkstra.sR} onChange={e => updateInput('dijkstra', 'sR', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Start Col</label>
                        <input type="number" value={inputs.dijkstra.sC} onChange={e => updateInput('dijkstra', 'sC', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                   </div>
                   <div className="grid grid-cols-2 gap-4">
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">End Row</label>
                        <input type="number" value={inputs.dijkstra.tR} onChange={e => updateInput('dijkstra', 'tR', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">End Col</label>
                        <input type="number" value={inputs.dijkstra.tC} onChange={e => updateInput('dijkstra', 'tC', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                   </div>
                </div>
              )}
              {activeTab === 'tsp' && (
                <div className="space-y-4">
                   <div className="grid grid-cols-2 gap-4">
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Start Row</label>
                        <input type="number" value={inputs.tsp.sR} onChange={e => updateInput('tsp', 'sR', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Start Col</label>
                        <input type="number" value={inputs.tsp.sC} onChange={e => updateInput('tsp', 'sC', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                   </div>
                   <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-500 uppercase">Random Stops</label>
                      <input type="range" min="3" max="15" value={inputs.tsp.count} onChange={e => updateInput('tsp', 'count', +e.target.value)} className="w-full accent-cyan-500" />
                      <div className="flex justify-between text-[10px] font-mono text-slate-500"><span>3</span><span>{inputs.tsp.count} Stops</span><span>15</span></div>
                   </div>
                </div>
              )}
              {activeTab === 'bin_packing' && (
                <div className="space-y-4">
                   <div className="space-y-2">
                      <label className="text-[10px] font-bold text-slate-500 uppercase">Number of Products</label>
                      <input type="number" value={inputs.binPacking.numProducts} onChange={e => updateInput('binPacking', 'numProducts', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                   </div>
                   <p className="text-[10px] text-slate-500 italic">Optimizes slotting using FFD + ABC Classification based on velocity.</p>
                </div>
              )}
              {activeTab === 'assignment' && (
                <div className="space-y-4">
                   <div className="grid grid-cols-2 gap-4">
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Target Row</label>
                        <input type="number" value={inputs.assignment.tR} onChange={e => updateInput('assignment', 'tR', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                     <div className="space-y-2">
                        <label className="text-[10px] font-bold text-slate-500 uppercase">Target Col</label>
                        <input type="number" value={inputs.assignment.tC} onChange={e => updateInput('assignment', 'tC', +e.target.value)} className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-white font-mono text-sm" />
                     </div>
                   </div>
                </div>
              )}
            </div>

            <div className="flex flex-col gap-3 pt-4">
              <button 
                onClick={() => {
                  if (activeTab === 'dijkstra') runDijkstra();
                  else if (activeTab === 'bin_packing') runBinPacking();
                  else if (activeTab === 'tsp') runTSP();
                  else if (activeTab === 'assignment') runAssignment();
                }}
                disabled={loading}
                className="w-full btn-primary flex items-center justify-center gap-2 h-12"
              >
                {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Play className="w-5 h-5 fill-current" />}
                Run Optimization
              </button>
            </div>
          </div>

          {results && (
            <div className="glass-card p-8 space-y-6 animate-in slide-in-from-top-4 duration-500">
              <div className="flex items-center gap-2">
                <BarChartIcon className="w-5 h-5 text-cyan-400" />
                <h3 className="text-lg font-bold text-white">Metrics</h3>
              </div>
              
              <div className="space-y-4">
                {activeTab === 'dijkstra' && (
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-3 bg-slate-800/30 rounded-lg text-center">
                      <p className="text-[10px] text-slate-500 uppercase">Distance</p>
                      <p className="text-lg font-bold text-white font-mono">
                        {results.distance === Infinity || results.distance === null || results.distance > 999999 
                          ? 'No Path' 
                          : `${Math.round(results.distance)}m`}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-800/30 rounded-lg text-center">
                      <p className="text-[10px] text-slate-500 uppercase">Nodes</p>
                      <p className="text-lg font-bold text-white font-mono">{results.path?.length || 0}</p>
                    </div>
                  </div>
                )}
                {activeTab === 'bin_packing' && (
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Products Placed</span><span className="text-white font-bold">{results.total_products_placed}</span></div>
                    <div className="flex justify-between text-sm"><span className="text-slate-400">Avg Utilization</span><span className="text-emerald-400 font-bold">{results.zone_metrics.A?.avg_utilization || 0}%</span></div>
                  </div>
                )}
                {activeTab === 'assignment' && results.assignment && (
                  <div className="space-y-3">
                    {results.assignment.assigned_picker_id !== null ? (
                      <>
                        <div className="flex justify-between text-sm"><span className="text-slate-400">Best Picker</span><span className="text-white font-bold">{results.assignment.picker?.name}</span></div>
                        <div className="flex justify-between text-sm"><span className="text-slate-400">Estimated Dist</span><span className="text-cyan-400 font-bold">{Math.round(results.assignment.distance_to_first_item)}m</span></div>
                      </>
                    ) : (
                      <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-xs font-bold text-center">
                        {results.assignment.assignment_reason}
                      </div>
                    )}
                  </div>
                )}
                {activeTab === 'tsp' && results && (
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-3 bg-slate-800/30 rounded-lg text-center">
                      <p className="text-[10px] text-slate-500 uppercase">Optimal Dist</p>
                      <p className="text-lg font-bold text-cyan-400 font-mono">{Math.round(results.optimal?.distance || 0)}m</p>
                    </div>
                    <div className="p-3 bg-slate-800/30 rounded-lg text-center">
                      <p className="text-[10px] text-slate-500 uppercase">Greedy Dist</p>
                      <p className="text-lg font-bold text-amber-400 font-mono">{Math.round(results.greedy?.distance || 0)}m</p>
                    </div>
                    {results.improvement_pct > 0 && (
                      <div className="col-span-2 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-center">
                        <p className="text-[10px] text-emerald-500 uppercase">Saving</p>
                        <p className="text-sm font-bold text-emerald-400">{results.improvement_pct}% shorter route</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Visualization Panel */}
        <div className="col-span-12 lg:col-span-8 h-[750px]">
          <div className="glass-card h-full flex flex-col relative overflow-hidden">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between z-10 bg-slate-900/50 backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" />
                <span className="text-xs font-bold text-slate-300 uppercase tracking-widest">Interactive Visualizer</span>
              </div>
              <div className="flex items-center gap-3">
                 <MousePointer2 className="w-3 h-3 text-slate-500" />
                 <span className="text-[10px] text-slate-500 uppercase text-right">Scroll to zoom<br/>Drag to pan</span>
              </div>
            </div>

            <div className="flex-1 relative bg-slate-950">
              <WarehouseCanvas {...canvasProps} />
              
              {!results && !loading && (
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-20">
                  <div className="flex flex-col items-center gap-6 animate-pulse opacity-20">
                    <Zap className="w-16 h-16 text-slate-600" />
                    <p className="text-lg font-bold text-slate-600">Engine Ready</p>
                  </div>
                </div>
              )}

              {loading && (
                <div className="absolute inset-0 bg-slate-950/50 backdrop-blur-sm flex items-center justify-center z-30">
                   <div className="flex flex-col items-center gap-4">
                     <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
                     <p className="text-cyan-500 font-bold animate-pulse uppercase tracking-widest text-xs">Computing Solution...</p>
                   </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AlgorithmComparisonPage;
