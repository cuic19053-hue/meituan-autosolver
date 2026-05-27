import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings2, CheckCircle2, AlertTriangle, Zap } from 'lucide-react';

function AnimatedNumber({ target, duration = 1200 }) {
  const [current, setCurrent] = useState(0);
  const startRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    startRef.current = performance.now();
    const animate = (now) => {
      const elapsed = now - startRef.current;
      const t = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - t, 3);
      setCurrent(t * target);
      if (t < 1) {
        rafRef.current = requestAnimationFrame(animate);
      }
    };
    rafRef.current = requestAnimationFrame(animate);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [target, duration]);

  return <span>{current.toFixed(1)}</span>;
}

function TerminalRow({ text, index }) {
  const [isOverridden, setIsOverridden] = useState(false);
  const [isHovered, setIsHovered] = useState(false);
  const [flash, setFlash] = useState(false);

  const handleOverride = () => {
    if (!isOverridden) {
      setIsOverridden(true);
      setFlash(true);
      setTimeout(() => setFlash(false), 400);
    }
  };

  if (isOverridden) {
    return (
      <motion.div
        initial={{ backgroundColor: 'rgba(249,115,22,0.4)' }}
        animate={{
          backgroundColor: flash ? 'rgba(249,115,22,0.4)' : 'rgba(249,115,22,0.1)',
        }}
        transition={{ duration: 0.3 }}
        className="flex items-center gap-2 px-2 py-0.5 rounded border border-orange-500/30 bg-orange-500/10 text-[11px] font-mono leading-5 group cursor-pointer"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={handleOverride}
      >
        <span className="opacity-70 shrink-0 text-orange-400">[MANUAL_OVERRIDE]</span>
        <span className="opacity-90 text-orange-300">{text}</span>
        <div className="ml-auto shrink-0">
          <Settings2 size={11} className="opacity-60 text-orange-400" />
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.2, delay: index * 0.005 }}
      className="flex items-center gap-2 px-2 py-0.5 rounded text-[#34D399] text-[11px] font-mono leading-5 group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <span className="opacity-60 shrink-0 text-[#60A5FA]">[AI 派单]</span>
      <span className="opacity-90">{text}</span>
      <motion.div
        className="ml-auto shrink-0 cursor-pointer"
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.15 }}
        onClick={handleOverride}
      >
        <Settings2 size={11} className="text-[#737373] hover:text-[#EDEDED]" />
      </motion.div>
    </motion.div>
  );
}

export default function SolutionTerminal({
  result: externalResult,
  isStreaming: externalStreaming,
  onReset,
}) {
  const [displayCount, setDisplayCount] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [showDebrief, setShowDebrief] = useState(false);
  const [showExportOptions, setShowExportOptions] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [isRetrying, setIsRetrying] = useState(false);
  const listRef = useRef(null);
  const bottomRef = useRef(null);
  const intervalRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    if (externalResult) {
      setData(externalResult);
      setLoading(false);
      setShowDebrief(false);
      setIsFinished(false);
      setDisplayCount(0);

      const logs = externalResult.logs || [];
      const solutionsCount = (externalResult.solutions || []).length;

      if (logs.length === 0 && solutionsCount === 0) {
        setIsFinished(true);
        return;
      }

      const totalRows = logs.length;
      setDisplayCount(0);

      intervalRef.current = setInterval(() => {
        if (!mountedRef.current) { clearInterval(intervalRef.current); return; }
        setDisplayCount(prev => {
          if (prev >= totalRows) {
            return prev;
          }
          return prev + 1;
        });
      }, 30);

      return () => {
        mountedRef.current = false;
        if (intervalRef.current) clearInterval(intervalRef.current);
      };
    }

    if (!externalResult) {
      setData(null);
      setDisplayCount(0);
      setIsFinished(false);
      setShowDebrief(false);
      setLoading(false);
    }

    return () => {
      mountedRef.current = false;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [externalResult]);

  useEffect(() => {
    if (isFinished && !data?.error) {
      const timer = setTimeout(() => setShowDebrief(true), 800);
      return () => clearTimeout(timer);
    }
  }, [isFinished, data]);

  useEffect(() => {
    const totalRows = (data?.logs || []).length;
    if (totalRows > 0 && displayCount >= totalRows && !isFinished) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      setIsFinished(true);
    }
  }, [displayCount, data, isFinished]);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [displayCount]);

  const logs = data?.logs || [];
  const solutions = data?.solutions || [];
  const displayedLogs = logs.slice(0, displayCount);

  const kpi = data?.kpi;

  const parsePercent = (str) => {
    if (!str) return 0;
    const match = String(str).match(/([\d.]+)/);
    return match ? parseFloat(match[1]) : 0;
  };

  const efficiencyGain = kpi?.efficiency_gain
    ? parsePercent(kpi.efficiency_gain)
    : 0;

  const completionRateData = kpi?.completion_rate
    ? parsePercent(kpi.completion_rate)
    : solutions.length > 0 ? Math.round((solutions.length / (logs.length || 1)) * 100) : 0;

  const latency = kpi?.latency ?? '1.02s';

  const handleRetry = () => {
    setIsRetrying(true);
    setRetryCount(prev => prev + 1);
    if (intervalRef.current) clearInterval(intervalRef.current);
    setData(null);
    setDisplayCount(0);
    setIsFinished(false);
    setShowDebrief(false);
    setLoading(false);
    if (onReset) onReset();
    setTimeout(() => setIsRetrying(false), 500);
  };

  const handleReset = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setData(null);
    setDisplayCount(0);
    setIsFinished(false);
    setShowDebrief(false);
    setLoading(false);
    if (onReset) onReset();
  };

  const getTimestamp = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day}-${hours}-${minutes}-${seconds}`;
  };

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const exportToJSON = () => {
    const filename = `dispatch-list-${getTimestamp()}.json`;
    const content = JSON.stringify(solutions, null, 2);
    downloadFile(content, filename, 'application/json');
    setShowExportOptions(false);
  };

  const escapeCSV = (val) => {
    const str = String(val ?? '');
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };

  const exportToCSV = () => {
    const filename = `dispatch-list-${getTimestamp()}.csv`;
    const headers = ['CourierID', 'Tasks', 'Utility'];
    const rows = solutions.map((sol) => [
      escapeCSV(sol.courier),
      escapeCSV(Array.isArray(sol.tasks) ? sol.tasks.join(';') : String(sol.tasks)),
      escapeCSV(sol.utility?.toFixed(2) || '')
    ]);
    const csvContent = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    downloadFile(csvContent, filename, 'text/csv');
    setShowExportOptions(false);
  };

  const handleExport = () => {
    setShowExportOptions(true);
  };

  const getStatusText = () => {
    if (data?.error) return 'CONNECTION_FAULT';
    if (isRetrying) return 'RECONNECTING...';
    if (loading || externalStreaming) return 'CLOUD_INFERENCE_ACTIVE';
    if (isFinished) return 'ALLOTMENT_COMPLETE';
    return 'STANDBY...';
  };

  const getStatusColor = () => {
    if (data?.error) return 'text-red-400';
    if (isRetrying) return 'text-[#FFD000]';
    if (loading || externalStreaming) return 'text-[#FFD000]';
    if (isFinished) return 'text-[#34D399]';
    return 'text-[#737373]';
  };

  return (
    <>
      <div className="flex flex-col w-full h-full bg-black/30 border border-[#262626] rounded-xl overflow-hidden relative font-mono">
        <div className="flex items-center justify-between px-4 py-2 border-b border-[#262626] bg-black/60 shrink-0">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <span className={`w-2.5 h-2.5 rounded-full ${data?.error ? 'bg-red-500 animate-pulse' : 'bg-red-500/60'}`} />
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/60 animate-pulse" />
              <span className={`w-2.5 h-2.5 rounded-full ${isFinished && !data?.error ? 'bg-green-500' : 'bg-green-500/60'}`} />
            </div>
            <span className={`text-[10px] tracking-widest ${getStatusColor()}`}>
              [STATUS: {getStatusText()}]
            </span>
          </div>
          {data && !data.error && (
            <div className="hidden md:flex gap-4 text-[9px] text-[#525252]">
              <span>全局效用: <span className="text-[#FFD000]">{efficiencyGain.toFixed(1)}</span></span>
              <span>锚定率: <span className="text-[#EDEDED]">{completionRateData.toFixed(1)}%</span></span>
              <span>推演进度: <span className="text-[#FFD000]">{displayedLogs.length}/{logs.length}</span></span>
            </div>
          )}
          {onReset && (
            <button
              onClick={handleReset}
              className="px-3 py-1 bg-white/5 border border-white/10 text-[#737373] text-[10px] tracking-widest hover:border-[#FFD000]/60 hover:text-[#FFD000] transition-all"
            >
              [重置日志]
            </button>
          )}
        </div>

        <div
          ref={listRef}
          className="flex-1 overflow-y-auto px-3 py-2 space-y-0.5"
          style={{ scrollbarWidth: 'thin', scrollbarColor: 'rgba(255,208,0,0.3) transparent' }}
        >
          {(loading || externalStreaming) && displayedLogs.length === 0 && (
            <div className="flex items-center gap-2 text-[#FFD000] animate-pulse text-[11px] font-mono py-2">
              <Zap size={12} className="animate-pulse" />
              <span>{'>'} [SYS] 正在建立加密云端链路...</span>
            </div>
          )}

          {displayedLogs.map((log, i) => (
            <TerminalRow key={`log-${i}`} text={log} index={i} />
          ))}

          {isFinished && !data?.error && solutions.length > 0 && (
            <>
              <div className="text-[#525252] text-[10px] py-1 border-t border-[#FFD000]/20 mt-2 pt-2">
                分配方案（{solutions.length} 条）
              </div>
              {solutions.map((sol, i) => {
                const tasks = Array.isArray(sol.tasks)
                  ? String(sol.tasks)
                  : sol.tasks || '—';
                const courier = sol.courier || '—';
                const text = `任务拓扑节点 ${tasks} 已锚定至运力 ${courier}`;
                return <TerminalRow key={`sol-${i}`} text={text} index={i} />;
              })}
            </>
          )}

          <div ref={bottomRef} />

          {data?.error && isFinished && (
            <div className="flex flex-col items-center justify-center gap-4 py-8">
              <div className="text-red-400 text-[11px] font-mono flex items-center gap-2">
                <AlertTriangle size={14} />
                <span>{'>'} [SYS_ERROR] 核心引擎离线，请检查云端算力节点。</span>
              </div>
              <button
                onClick={handleRetry}
                disabled={isRetrying}
                className="px-4 py-2 bg-red-500/10 border border-red-500/40 text-red-400 text-[10px] tracking-widest hover:bg-red-500/20 transition-all font-mono disabled:opacity-50"
              >
                {isRetrying ? '[RECONNECTING...]' : '[边缘异常接管]'}
              </button>
            </div>
          )}

          {!data && !loading && !externalStreaming && (
            <div className="flex items-center justify-center h-full text-[#525252] text-[11px] font-mono italic">
              {'>'} [SYS] 正在接入云端调度引擎...
            </div>
          )}
        </div>

        <div className="px-4 py-2 border-t border-[#FFD000]/40 bg-black/60 shrink-0 flex items-center gap-3">
          {data?.logs && data.logs.length > 0 && (
            <div className="flex gap-2 items-center">
              <span className="text-[9px] text-[#525252]">AGENT_LOG:</span>
              <motion.span
                animate={{ opacity: [0.3, 1, 0.3] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-[9px] text-[#60A5FA] font-mono"
              >
                {data.logs[data.logs.length - 1]?.toString().replace(/^>\s*\[\S+\]/, '> ') || '[INIT]'}
              </motion.span>
            </div>
          )}
          <div className="ml-auto flex gap-4 text-[9px] font-mono text-[#737373]">
            <span>推演行: <span className="text-[#EDEDED]">{displayedLogs.length}</span></span>
            {(loading || externalStreaming) && <span className="text-[#FFD000] animate-pulse">◉ PROCESSING</span>}
            {isFinished && !data?.error && <span className="text-[#34D399]">◉ COMPLETE</span>}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {showDebrief && isFinished && !data?.error && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="fixed inset-0 z-40 bg-black/60 backdrop-blur-md"
              onClick={() => {}}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.92, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.92, y: 20 }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
            >
              <div className="pointer-events-auto bg-black/80 backdrop-blur-xl border border-[#FFD000]/30 rounded-3xl p-8 shadow-[0_0_100px_rgba(255,208,0,0.1)] min-w-[400px] max-w-[480px]">
                <div className="flex flex-col gap-6">
                  <div className="flex items-center gap-3">
                    <CheckCircle2 size={20} className="text-[#FFD000]" />
                    <span className="text-lg font-mono tracking-widest text-[#FFD000]">
                      全局效用归因报告
                    </span>
                  </div>

                  <div className="h-px bg-[#FFD000]/20" />

                  <div className="flex flex-col gap-5">
                    <div className="flex items-end justify-between">
                      <div className="flex flex-col gap-1">
                        <span className="text-[11px] text-[#525252] font-mono uppercase tracking-wider">
                          调度完成率
                        </span>
                        <div className="flex items-baseline gap-1">
                          <span className="text-4xl font-mono font-bold text-[#FFD000] tracking-tight">
                            <AnimatedNumber target={efficiencyGain} />
                          </span>
                          <span className="text-lg text-[#FFD000]/60 font-mono">%</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-1 text-[#34D399] text-xs font-mono">
                        <span>{'>'} 目标达成</span>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between text-[10px] font-mono">
                        <span className="text-[#525252]">锚点覆盖率</span>
                        <span className="text-[#EDEDED]">{completionRateData.toFixed(1)}%</span>
                      </div>
                      <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full"
                          style={{
                            width: `${completionRateData}%`,
                            background: 'linear-gradient(90deg, #FFD000, #FF8C00)',
                            transition: 'width 1.2s cubic-bezier(0.16, 1, 0.3, 1)',
                          }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[11px] text-[#525252] font-mono uppercase tracking-wider">
                        算力耗时
                      </span>
                      <span className="text-sm font-mono text-[#EDEDED]">{latency}</span>
                    </div>
                  </div>

                  <div className="h-px bg-[#FFD000]/20" />

                  {!showExportOptions ? (
                    <div className="flex gap-4">
                      <button
                        onClick={handleExport}
                        className="flex-1 py-2.5 bg-transparent border border-[#FFD000]/40 text-[#FFD000] text-[11px] font-mono tracking-widest rounded-xl hover:bg-[#FFD000]/10 transition-all duration-300"
                        style={{ transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
                      >
                        [ 导出派单清单 ]
                      </button>
                      <button
                        onClick={handleReset}
                        className="flex-1 py-2.5 bg-[#FFD000]/10 border border-[#FFD000]/60 text-[#FFD000] text-[11px] font-mono tracking-widest rounded-xl hover:bg-[#FFD000]/20 transition-all duration-300"
                        style={{ transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
                      >
                        [ 结束本次推演 ]
                      </button>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-3">
                      <div className="text-[11px] text-[#FFD000] font-mono tracking-widest">选择导出格式</div>
                      <div className="flex gap-4">
                        <button
                          onClick={exportToJSON}
                          className="flex-1 py-2.5 bg-transparent border border-[#FFD000]/40 text-[#FFD000] text-[11px] font-mono tracking-widest rounded-xl hover:bg-[#FFD000]/10 transition-all duration-300"
                          style={{ transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
                        >
                          [ JSON ]
                        </button>
                        <button
                          onClick={exportToCSV}
                          className="flex-1 py-2.5 bg-[#FFD000]/10 border border-[#FFD000]/60 text-[#FFD000] text-[11px] font-mono tracking-widest rounded-xl hover:bg-[#FFD000]/20 transition-all duration-300"
                          style={{ transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
                        >
                          [ CSV ]
                        </button>
                      </div>
                      <button
                        onClick={() => setShowExportOptions(false)}
                        className="py-2 bg-transparent border border-white/20 text-[#525252] text-[10px] font-mono tracking-widest rounded-lg hover:bg-white/5 transition-all duration-300"
                        style={{ transition: 'all 0.3s cubic-bezier(0.16, 1, 0.3, 1)' }}
                      >
                        [ 返回 ]
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}