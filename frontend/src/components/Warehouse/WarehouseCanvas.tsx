import React, { useRef, useEffect, useState, useCallback } from 'react';
import { useSimulationStore } from '../../store/simulationStore';
import { CellType, WarehouseCell, Picker } from '../../types';

export interface WarehouseCanvasProps {
  highlightPath?: [number, number][];
  highlightPoints?: { pos: [number, number], color: string, label?: string }[];
  highlightEdges?: [[number, number], [number, number]][];
  highlightExplored?: [number, number][];
}

const WarehouseCanvas: React.FC<WarehouseCanvasProps> = ({ 
  highlightPath, 
  highlightPoints, 
  highlightEdges,
  highlightExplored 
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const { layout, pickers, replenishment, heatmap } = useSimulationStore();
  
  // View state
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Constants
  const CELL_SIZE = 40;

  const [userMovedMap, setUserMovedMap] = useState(false);

  // Auto-center on layout load and container resize (if user hasn't moved it)
  useEffect(() => {
    if (layout && containerRef.current && !userMovedMap) {
      const { clientWidth, clientHeight } = containerRef.current;
      if (clientWidth < 100 || clientHeight < 100) return; // Wait for stable layout

      const mapWidth = layout.cols * CELL_SIZE;
      const mapHeight = layout.rows * CELL_SIZE;
      
      setOffset({
        x: (clientWidth - mapWidth * zoom) / 2,
        y: (clientHeight - mapHeight * zoom) / 2
      });

      // Initial zoom to fit if first time
      if (zoom === 1) {
        const zoomX = clientWidth / (mapWidth + 80);
        const zoomY = clientHeight / (mapHeight + 80);
        const fitZoom = Math.min(1, zoomX, zoomY);
        setZoom(fitZoom);
        
        // Recalculate offset with new zoom
        setOffset({
          x: (clientWidth - mapWidth * fitZoom) / 2,
          y: (clientHeight - mapHeight * fitZoom) / 2
        });
      }
    }
  }, [layout, userMovedMap]);

  // Render loop
  const draw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas || !layout) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.save();
    ctx.translate(offset.x, offset.y);
    ctx.scale(zoom, zoom);

    // 1. Draw Grid / Aisle background
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(-1000, -1000, (layout.cols * CELL_SIZE) + 2000, (layout.rows * CELL_SIZE) + 2000);

    // Subtle grid pattern
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 0.5;
    for (let i = -1000; i < (layout.cols * CELL_SIZE) + 1000; i += CELL_SIZE) {
      ctx.beginPath(); ctx.moveTo(i, -1000); ctx.lineTo(i, (layout.rows * CELL_SIZE) + 1000); ctx.stroke();
    }
    for (let j = -1000; j < (layout.rows * CELL_SIZE) + 1000; j += CELL_SIZE) {
      ctx.beginPath(); ctx.moveTo(-1000, j); ctx.lineTo((layout.cols * CELL_SIZE) + 1000, j); ctx.stroke();
    }

    // 2. Draw Cells
    layout.grid.forEach((row, r) => {
      row.forEach((cell, c) => {
        const x = c * CELL_SIZE;
        const y = r * CELL_SIZE;

        // Base cell styles
        switch (cell.cell_type) {
          case 'shelf':
            // High-contrast shelf colors
            ctx.fillStyle = '#1e293b'; // Slate-800
            if (cell.zone === 'A') ctx.fillStyle = '#450a0a'; // Deep red
            else if (cell.zone === 'B') ctx.fillStyle = '#451a03'; // Deep orange
            else if (cell.zone === 'C') ctx.fillStyle = '#061a40'; // Deep blue
            
            ctx.fillRect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            ctx.strokeStyle = cell.zone === 'A' ? '#ef4444' : (cell.zone === 'B' ? '#f59e0b' : '#3b82f6');
            ctx.lineWidth = 1.5;
            ctx.strokeRect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4);
            
            // Fill level indicator
            if (cell.shelf_capacity > 0) {
              const fillPct = cell.shelf_used / cell.shelf_capacity;
              ctx.fillStyle = '#475569';
              ctx.fillRect(x + 6, y + CELL_SIZE - 10, (CELL_SIZE - 12) * fillPct, 4);
            }
            break;

          case 'pick_station':
            ctx.fillStyle = '#fbbf2411';
            ctx.fillRect(x, y, CELL_SIZE, CELL_SIZE);
            ctx.strokeStyle = '#fbbf24';
            ctx.lineWidth = 2;
            ctx.strokeRect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8);
            // Draw a small icon-like shape for station
            ctx.fillStyle = '#fbbf24';
            ctx.fillRect(x + 10, y + 15, 20, 10);
            break;

          case 'receiving':
            ctx.fillStyle = '#10b98111';
            ctx.fillRect(x, y, CELL_SIZE, CELL_SIZE);
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 2;
            ctx.strokeRect(x + 4, y + 4, CELL_SIZE - 8, CELL_SIZE - 8);
            // Draw a small icon-like shape for dock
            ctx.fillStyle = '#10b981';
            ctx.fillRect(x + 15, y + 10, 10, 20);
            break;

          default:
            // Path
            break;
        }

        // Visit count (Heatmap overlay)
        if (cell.visit_count > 0) {
          const alpha = Math.min(cell.visit_count / 100, 0.4);
          ctx.fillStyle = `rgba(236, 72, 153, ${alpha})`;
          ctx.fillRect(x, y, CELL_SIZE, CELL_SIZE);
        }
      });
    });

    // 3. Draw Explored Nodes (Algorithm Visualization)
    if (highlightExplored) {
      ctx.fillStyle = '#06b6d433'; // Cyan-500 with low opacity
      highlightExplored.forEach(node => {
        ctx.fillRect(node[1] * CELL_SIZE, node[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE);
      });
    }

    // 4. Draw Explored Edges (Algorithm Visualization)
    if (highlightEdges) {
      ctx.beginPath();
      ctx.strokeStyle = '#06b6d444';
      ctx.lineWidth = 1;
      highlightEdges.forEach(edge => {
        const [p1, p2] = edge;
        ctx.moveTo(p1[1] * CELL_SIZE + CELL_SIZE/2, p1[0] * CELL_SIZE + CELL_SIZE/2);
        ctx.lineTo(p2[1] * CELL_SIZE + CELL_SIZE/2, p2[0] * CELL_SIZE + CELL_SIZE/2);
      });
      ctx.stroke();
    }

    // 5. Draw Highlight Path (Algorithm Visualization)
    if (highlightPath && highlightPath.length > 0) {
      ctx.beginPath();
      ctx.strokeStyle = '#06b6d4';
      ctx.lineWidth = 4;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.moveTo(highlightPath[0][1] * CELL_SIZE + CELL_SIZE/2, highlightPath[0][0] * CELL_SIZE + CELL_SIZE/2);
      for (let i = 1; i < highlightPath.length; i++) {
        ctx.lineTo(highlightPath[i][1] * CELL_SIZE + CELL_SIZE/2, highlightPath[i][0] * CELL_SIZE + CELL_SIZE/2);
      }
      ctx.stroke();
      
      // Animate path flow
      const time = Date.now() / 1000;
      ctx.setLineDash([10, 10]);
      ctx.lineDashOffset = -time * 30;
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 6. Draw Highlight Points
    if (highlightPoints) {
      highlightPoints.forEach(pt => {
        const x = pt.pos[1] * CELL_SIZE + CELL_SIZE/2;
        const y = pt.pos[0] * CELL_SIZE + CELL_SIZE/2;
        
        ctx.fillStyle = pt.color;
        ctx.beginPath();
        ctx.arc(x, y, 6, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (pt.label) {
          ctx.fillStyle = '#fff';
          ctx.font = 'bold 10px Inter';
          ctx.textAlign = 'center';
          ctx.shadowBlur = 4;
          ctx.shadowColor = 'rgba(0,0,0,0.5)';
          ctx.fillText(pt.label, x, y - 10);
          ctx.shadowBlur = 0;
        }
      });
    }

    // 7. Draw Active Picker Routes
    Object.values(pickers).forEach(picker => {
      if (picker.route.length > 0 && picker.status !== 'idle' && !highlightPath) {
        ctx.beginPath();
        ctx.strokeStyle = picker.color;
        ctx.lineWidth = 2;
        ctx.setLineDash([5, 5]);
        
        const start = picker.route[picker.route_index] || picker.current_position;
        ctx.moveTo(start[1] * CELL_SIZE + CELL_SIZE/2, start[0] * CELL_SIZE + CELL_SIZE/2);
        
        for (let i = picker.route_index + 1; i < picker.route.length; i++) {
          const p = picker.route[i];
          ctx.lineTo(p[1] * CELL_SIZE + CELL_SIZE/2, p[0] * CELL_SIZE + CELL_SIZE/2);
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // 8. Draw Pickers
    Object.values(pickers).forEach(picker => {
      const x = picker.current_position[1] * CELL_SIZE + CELL_SIZE/2;
      const y = picker.current_position[0] * CELL_SIZE + CELL_SIZE/2;

      // Glow
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, 15);
      gradient.addColorStop(0, `${picker.color}66`);
      gradient.addColorStop(1, 'transparent');
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(x, y, 15, 0, Math.PI * 2);
      ctx.fill();

      // Body
      ctx.fillStyle = picker.color;
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Label
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 9px Inter';
      ctx.textAlign = 'center';
      ctx.fillText(picker.name.split(' ')[1], x, y + 3.5);
    });

    // 9. Draw Replenishment tasks
    replenishment.active_tasks.forEach(task => {
      const pos = task.route[task.route_index];
      if (!pos) return;
      const x = pos[1] * CELL_SIZE + CELL_SIZE/2;
      const y = pos[0] * CELL_SIZE + CELL_SIZE/2;

      ctx.fillStyle = '#a855f7';
      ctx.beginPath();
      ctx.rect(x - 5, y - 5, 10, 10);
      ctx.fill();
      ctx.strokeStyle = '#fff';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    ctx.restore();
  }, [layout, pickers, replenishment, offset, zoom, highlightPath, highlightPoints, highlightEdges, highlightExplored]);

  // Handle resizing
  useEffect(() => {
    const updateSize = () => {
      if (containerRef.current && canvasRef.current) {
        canvasRef.current.width = containerRef.current.clientWidth;
        canvasRef.current.height = containerRef.current.clientHeight;
        draw();
      }
    };
    window.addEventListener('resize', updateSize);
    updateSize();
    return () => window.removeEventListener('resize', updateSize);
  }, [draw]);

  // Animation frame
  useEffect(() => {
    let frameId: number;
    const render = () => {
      draw();
      frameId = requestAnimationFrame(render);
    };
    render();
    return () => cancelAnimationFrame(frameId);
  }, [draw]);

  // Interaction handlers
  const handleWheel = (e: React.WheelEvent) => {
    setUserMovedMap(true);
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoom(z => Math.max(0.05, Math.min(10, z * delta)));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setUserMovedMap(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  if (!layout) {
    return (
      <div className="w-full h-full bg-slate-950 flex flex-col items-center justify-center gap-4">
        <div className="w-12 h-12 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
        <p className="text-slate-500 font-medium animate-pulse">Initializing Warehouse Map...</p>
      </div>
    );
  }

  return (
    <div 
      ref={containerRef} 
      className="w-full h-full cursor-grab active:cursor-grabbing bg-slate-950 relative"
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
    >
      <canvas ref={canvasRef} className="block" />
      
      {/* HUD overlays */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        <button 
          onClick={() => {
            setUserMovedMap(false);
            setZoom(1);
          }}
          className="glass-card px-3 py-1.5 flex items-center gap-2 hover:bg-slate-800 transition-colors pointer-events-auto"
        >
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Recenter</span>
        </button>
        <div className="glass-card px-3 py-1.5 flex items-center gap-3 backdrop-blur-md pointer-events-none">
          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Zoom</span>
          <span className="text-xs font-mono text-cyan-400">{Math.round(zoom * 100)}%</span>
        </div>
      </div>
    </div>
  );
};

export default WarehouseCanvas;

