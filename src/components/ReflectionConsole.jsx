import React, { useState, useEffect, useRef } from 'react';

function getLineStyle(tag) {
  if (!tag) return 'text-[#737373]';
  if (tag === 'ASSIGN') return 'text-[#34D399]';
  if (tag === 'CONFLICT') return 'text-[#FFD000]';
  if (tag === 'REFLECTION') return 'text-[#C084FC]';
  if (tag === 'WARN') return 'text-[#F87171]';
  if (tag === 'EFFICIENCY') return 'text-[#60A5FA]';
  if (tag === 'INIT') return 'text-[#60A5FA]';
  if (tag === 'SUMMARY') return 'text-[#C084FC]';
  if (tag === 'SKIP') return 'text-[#737373]';
  return 'text-[#737373]';
}

function getLineIcon(tag) {
  if (tag === 'ASSIGN') return '▸';
  if (tag === 'CONFLICT') return '◂';
  if (tag === 'REFLECTION') return '◈';
  if (tag === 'WARN') return '⚠';
  if (tag === 'EFFICIENCY') return '◎';
  if (tag === 'INIT') return '→';
  if (tag === 'SUMMARY') return '◼';
  if (tag === 'SKIP') return '·';
  return '·';
}

export default function ReflectionConsole({ logs = [], stats = null, onClose }) {
  const [displayedLogs, setDisplayedLogs] = useState([]);
  const containerRef = useRef(null);
  const timerRef = useRef(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    const prevLen = displayedLogs.length;
    if (logs.length <= prevLen) return;
    let idx = prevLen;
    const step = () => {
      if (idx < logs.length) {
        setDisplayedLogs(logs.slice(0, idx + 1));
        idx++;
        timerRef.current = setTimeout(step, 50);
      }
    };
    step();
    return () => { if (timerRef.current) clearTimeout(timerRef.current); };
  }, [logs]);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [displayedLogs]);

  const conflictCount = logs.filter(l => l.includes('[CONFLICT #')).length;
  const assignedCount = logs.filter(l => l.includes('[ASSIGN]')).length;
  const totalScoreMatch = logs.find(l => l.includes('[SUMMARY]'));
  const totalScore = totalScoreMatch
    ? (totalScoreMatch.match(/Total score:\s*([\d.]+)/)?.[1] || '—')
    : '—';

  const assignedStats = stats?.assignedCount ?? assignedCount;
  const scoreStats = stats?.totalScore ?? totalScore;

  return (
    <div className="flex flex-col w-72 h-full bg-black/70 border-l border-[#262626] backdrop-blur-md font-mono overflow-hidden">
      <div className="flex items-center justify-between px-3 py-2 border-b border-[#262626] bg-black/40">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#C084FC] animate-pulse" />
          <span className="text-[9px] text-[#C084FC] tracking-widest uppercase">Reflection Console</span>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-[9px] text-[#525252] hover:text-[#737373] transition-colors tracking-widest"
          >
            [CLOSE]
          </button>
        )}
      </div>

      <div
        ref={containerRef}
        className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5"
        style={{
          fontSize: '11px',
          lineHeight: '1.6',
          scrollbarWidth: 'thin',
          scrollbarColor: 'rgba(192,132,252,0.3) transparent',
        }}
      >
        {displayedLogs.map((line, i) => {
          const tagMatch = line.match(/\[(ASSIGN|CONFLICT|REFLECTION|WARN|EFFICIENCY|INIT|SUMMARY|SKIP)\]/);
          const tag = tagMatch ? tagMatch[1] : null;
          const prefix = tag ? `[${tag}]` : '';
          return (
            <div key={i} className={`flex gap-1 ${getLineStyle(tag)} transition-opacity duration-200`}>
              <span className="opacity-60">{getLineIcon(tag)}</span>
              <span className="opacity-80">{line}</span>
            </div>
          );
        })}
        {displayedLogs.length === 0 && (
          <div className="text-[#404040] text-[10px] italic py-4 text-center">
            Awaiting solver input...
          </div>
        )}
      </div>

      <div className="px-3 py-2 border-t border-[#262626] bg-black/40 space-y-1">
        <div className="flex justify-between text-[9px]">
          <span className="text-[#525252]">ASSIGNED</span>
          <span className="text-[#34D399]">{assignedStats}</span>
        </div>
        <div className="flex justify-between text-[9px]">
          <span className="text-[#525252]">CONFLICTS</span>
          <span className="text-[#FFD000]">{conflictCount}</span>
        </div>
        <div className="flex justify-between text-[9px]">
          <span className="text-[#525252]">TOTAL_SCORE</span>
          <span className="text-[#EDEDED]">{scoreStats}</span>
        </div>
      </div>
    </div>
  );
}
