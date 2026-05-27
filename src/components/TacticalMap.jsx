import React, { useState, useEffect, useCallback, useMemo } from 'react';

export default function TacticalMap({ apiBase = '', onSolverData, onBack }) {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [solved, setSolved] = useState(false);
  const [selectedLinks, setSelectedLinks] = useState([]);
  const [hoveredId, setHoveredId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [solving, setSolving] = useState(false);
  const [focusedCourier, setFocusedCourier] = useState(null);

  const fetchMap = useCallback(async () => {
    try {
      const r = await fetch(`${apiBase}/api/map_init`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const uniqueNodeMap = new Map();
      (data.nodes || []).forEach(n => uniqueNodeMap.set(n.id, n));
      setNodes(Array.from(uniqueNodeMap.values()));
      setLinks(data.links || []);
      setLoading(false);
    } catch (err) {
      console.error('[TacticalMap] fetchMap error:', err);
      setLoading(false);
    }
  }, [apiBase]);

  useEffect(() => { fetchMap(); }, [fetchMap]);

  const runSolver = async () => {
    setSolving(true);
    try {
      const r = await fetch(`${apiBase}/api/solver`);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const sel = (data.selected || []).filter(s => s.assigned);
      setSelectedLinks(sel);
      setSolved(true);
      if (onSolverData) {
        onSolverData({ logs: data.logs || [], totalScore: data.total_score, assignedCount: data.assigned_count });
      }
    } catch {
      if (onSolverData) {
        onSolverData({ logs: ['[ERROR] Solver request failed'], totalScore: 0, assignedCount: 0 });
      }
    }
    setSolving(false);
  };

  const reset = () => {
    setSolved(false);
    setSelectedLinks([]);
    setFocusedCourier(null);
    setLoading(false);
    if (onSolverData) {
      onSolverData(null);
    }
  };

  const handleCourierClick = (courierId) => {
    setFocusedCourier(prev => prev === courierId ? null : courierId);
  };

  const { xMin, xMax, yMin, yMax, paddingX, paddingY, svgW, svgH } = useMemo(() => {
    if (nodes.length === 0) return { xMin: 0, xMax: 100, yMin: 0, yMax: 100, paddingX: 10, paddingY: 10, svgW: 100, svgH: 100 };
    const xs = nodes.map(n => n.x);
    const ys = nodes.map(n => n.y);
    const xMin = Math.min(...xs);
    const xMax = Math.max(...xs);
    const yMin = Math.min(...ys);
    const yMax = Math.max(...ys);
    const rangeX = xMax - xMin || 1;
    const rangeY = yMax - yMin || 1;
    return {
      xMin: xMin - rangeX * 0.1,
      xMax: xMax + rangeX * 0.1,
      yMin: yMin - rangeY * 0.1,
      yMax: yMax + rangeY * 0.1,
      paddingX: rangeX * 0.1,
      paddingY: rangeY * 0.1,
      svgW: (xMax - xMin) + rangeX * 0.2,
      svgH: (yMax - yMin) + rangeY * 0.2,
    };
  }, [nodes]);

  const viewBoxStr = useMemo(() => {
    return `${xMin - paddingX} ${yMin - paddingY} ${(xMax - xMin) + paddingX * 2} ${(yMax - yMin) + paddingY * 2}`;
  }, [xMin, xMax, yMin, yMax, paddingX, paddingY]);

  const taskNodes = useMemo(() => nodes.filter(n => n.type === 'task'), [nodes]);
  const courierNodes = useMemo(() => nodes.filter(n => n.type === 'courier'), [nodes]);

  const uniqueLinks = useMemo(() => {
    const seen = new Set();
    return links.filter(link => {
      const key = `${link.source}-${[...link.target].sort((a, b) => a - b).join(',')}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [links]);

  const hlOpacity = useMemo(() => {
    if (selectedLinks.length === 0) return 1;
    return Math.max(0.5, 1 - selectedLinks.length * 0.03);
  }, [selectedLinks.length]);

  return (
    <div className="relative w-full h-full bg-[#0A0A0A] font-mono overflow-hidden">
      {onBack && (
        <button
          onClick={onBack}
          className="absolute top-2 left-2 z-50 px-3 py-1.5 bg-[#141414]/90 border border-[#262626] text-[#737373] text-[10px] tracking-widest hover:border-[#FFD000]/50 hover:text-[#FFD000] transition-all"
        >
          ← BACK
        </button>
      )}

      <svg
        className="w-full h-full"
        viewBox={viewBoxStr}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <pattern id="grid50" width={50} height={50} patternUnits="userSpaceOnUse">
            <path d="M 50 0 L 0 0 0 50" fill="none" stroke="rgba(237,237,237,0.03)" strokeWidth={0.5} />
          </pattern>
          <radialGradient id="edgeDark" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor="transparent" />
            <stop offset="100%" stopColor="rgba(10,10,10,0.85)" />
          </radialGradient>
          <filter id="glowYellow">
            <feDropShadow dx="0" dy="0" stdDeviation="4" floodColor="#FFD000" floodOpacity="0.7" />
          </filter>
          <filter id="glowBlue">
            <feDropShadow dx="0" dy="0" stdDeviation="3" floodColor="#60A5FA" floodOpacity="0.5" />
          </filter>
          <style>{`
            @keyframes breathe {
              0%, 100% { opacity: 0.4; }
              50% { opacity: 1.0; }
            }
            @keyframes flowDash {
              0% { stroke-dashoffset: 24; }
              100% { stroke-dashoffset: 0; }
            }
            .courier-triangle {
              animation: breathe 2s ease-in-out infinite;
            }
            .flowing-line {
              animation: flowDash 1.2s linear infinite;
            }
          `}</style>
        </defs>

        <rect
          x={xMin - paddingX}
          y={yMin - paddingY}
          width={(xMax - xMin) + paddingX * 2}
          height={(yMax - yMin) + paddingY * 2}
          fill="#0A0A0A"
        />
        <rect
          x={xMin - paddingX}
          y={yMin - paddingY}
          width={(xMax - xMin) + paddingX * 2}
          height={(yMax - yMin) + paddingY * 2}
          fill="url(#grid50)"
        />
        <rect
          x={xMin - paddingX}
          y={yMin - paddingY}
          width={(xMax - xMin) + paddingX * 2}
          height={(yMax - yMin) + paddingY * 2}
          fill="url(#edgeDark)"
        />

        {uniqueLinks.map((link, i) => {
          const courier = nodes.find(n => n.id === link.source && n.type === 'courier');
          if (!courier) return null;
          const isSelected = selectedLinks.some(s => s.source === link.source);
          const isFocused = focusedCourier === link.source;
          return link.target.map((taskId, j) => {
            const task = nodes.find(n => n.id === taskId);
            if (!task) return null;
            const key = `${i}-${j}`;
            if (isFocused) {
              return (
                <line
                  key={key}
                  x1={courier.x} y1={courier.y}
                  x2={task.x} y2={task.y}
                  stroke="#60A5FA"
                  strokeWidth={1}
                  strokeOpacity={0.35}
                />
              );
            }
            if (isSelected && solved) {
              return (
                <line
                  key={key}
                  x1={courier.x} y1={courier.y}
                  x2={task.x} y2={task.y}
                  stroke="#FFD000"
                  strokeWidth={2}
                  strokeOpacity={hlOpacity}
                  strokeDasharray="8 4"
                  filter="url(#glowYellow)"
                  className="flowing-line"
                />
              );
            }
            return (
              <line
                key={key}
                x1={courier.x} y1={courier.y}
                x2={task.x} y2={task.y}
                stroke="#737373"
                strokeWidth={0.5}
                strokeOpacity={0.1}
              />
            );
          });
        })}

        {taskNodes.map(node => (
          <g key={node.id} onMouseEnter={() => setHoveredId(node.id)} onMouseLeave={() => setHoveredId(null)} className="cursor-pointer">
            <circle cx={node.x} cy={node.y} r={5} fill="none" stroke="#EDEDED" strokeWidth={1} />
            {hoveredId === node.id && (
              <text x={node.x + 8} y={node.y + 4} fill="#EDEDED" fontSize={10} className="pointer-events-none select-none">T:{node.id}</text>
            )}
          </g>
        ))}

        {courierNodes.map(node => (
          <g key={node.id} onMouseEnter={() => setHoveredId(node.id)} onMouseLeave={() => setHoveredId(null)} onClick={() => handleCourierClick(node.id)} className="cursor-pointer">
            <polygon
              points={`${node.x},${node.y - 6} ${node.x - 5},${node.y + 4} ${node.x + 5},${node.y + 4}`}
              fill="none"
              stroke="#737373"
              strokeWidth={1}
              className={`courier-triangle ${focusedCourier === node.id ? 'stroke-[#60A5FA]' : ''}`}
              style={{ transition: 'stroke 200ms' }}
            />
            {hoveredId === node.id && (
              <text x={node.x + 8} y={node.y + 4} fill="#A3A3A3" fontSize={10} className="pointer-events-none select-none">C:{node.id}</text>
            )}
          </g>
        ))}
      </svg>

      <div className="absolute bottom-3 right-3 flex gap-3">
        {!solved ? (
          <button
            onClick={runSolver}
            disabled={solving || loading}
            className="px-4 py-1.5 bg-[#FFD000]/10 border border-[#FFD000]/40 text-[#FFD000] text-[10px] tracking-widest hover:bg-[#FFD000]/20 transition-all disabled:opacity-30 font-mono"
          >
            {solving ? 'SOLVING...' : 'EXECUTE SOLVER'}
          </button>
        ) : (
          <button
            onClick={reset}
            disabled={solving}
            className="px-4 py-1.5 bg-white/5 border border-white/10 text-[#EDEDED] text-[10px] tracking-widest hover:bg-white/10 transition-all disabled:opacity-30 font-mono"
          >
            RESET
          </button>
        )}
      </div>

      <div className="absolute bottom-3 left-3 flex gap-3 text-[9px] font-mono text-[#404040]">
        <span>NODES: {nodes.length}</span>
        <span>LINKS: {uniqueLinks.length}</span>
        {solved && <span className="text-[#34D399]">ASSIGNED: {selectedLinks.length}</span>}
      </div>

      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0A0A0A]/80 text-[#737373] text-xs font-mono">
          Loading topology...
        </div>
      )}
    </div>
  );
}
