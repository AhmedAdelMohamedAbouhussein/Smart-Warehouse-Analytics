import React from 'react';
import { useSimulationStore } from '../../store/simulationStore';
import { Play, Pause, RotateCcw, Clock, Zap } from 'lucide-react';

const Header: React.FC = () => {
  const { 
    running, 
    paused, 
    tick, 
    speed, 
    setSpeed,
    setRunning,
    setPaused,
    setInitialState
  } = useSimulationStore();

  const handleStart = async () => {
    // Optimistic UI update
    setRunning(true);
    setPaused(false);
    try {
      const res = await fetch('/api/simulation/start', { method: 'POST' });
      const data = await res.json();
      // Sync with server response
      setRunning(data.status === 'running');
    } catch (err) {
      setRunning(false);
      console.error('Failed to start simulation:', err);
    }
  };

  const handlePause = async () => {
    setPaused(true);
    await fetch('/api/simulation/pause', { method: 'POST' });
  };

  const handleReset = async () => {
    if (window.confirm('Reset simulation? All current progress will be lost.')) {
      setRunning(false);
      setPaused(false);
      const res = await fetch('/api/simulation/reset', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'reset') {
        // The store reset will happen automatically via WS, 
        // but we can clear local metrics here if needed.
      }
    }
  };

  const handleSpeedChange = async (newSpeed: number) => {
    setSpeed(newSpeed);
    await fetch('/api/simulation/speed', { 
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ speed: newSpeed })
    });
  };

  return (
    <header className="h-16 glass-card mx-6 mt-6 px-6 flex items-center justify-between z-40 relative">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2 text-slate-400">
          <Clock className="w-4 h-4" />
          <span className="text-sm font-mono tracking-wider">TICK: {tick.toString().padStart(6, '0')}</span>
        </div>
        
        <div className="h-4 w-[1px] bg-slate-700" />

        <div className="flex items-center gap-2">
          <button 
            onClick={running && !paused ? handlePause : handleStart}
            className={`p-2 rounded-lg transition-all duration-200 ${
              running && !paused 
                ? 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20' 
                : 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20'
            }`}
          >
            {running && !paused ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
          </button>
          
          <button 
            onClick={handleReset}
            className="p-2 bg-slate-800 text-slate-400 rounded-lg hover:bg-slate-700 hover:text-slate-200 transition-all"
          >
            <RotateCcw className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4 bg-slate-800/50 px-4 py-2 rounded-xl border border-slate-700/50">
          <Zap className="w-4 h-4 text-cyan-400" />
          <input 
            type="range" 
            min="0.25" 
            max="5" 
            step="0.25" 
            value={speed}
            onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
            className="w-32 accent-cyan-500 bg-slate-700 h-1 rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-xs font-bold text-slate-400 min-w-[2.5rem]">{speed}x</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex flex-col items-end">
            <span className="text-sm font-bold text-slate-200">Admin Panel</span>
            <span className="text-[10px] text-emerald-500 font-medium uppercase tracking-tighter">Simulation Live</span>
          </div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg border-2 border-slate-800">
            A
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
