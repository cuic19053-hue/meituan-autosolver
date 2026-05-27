import { useState, useCallback, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || '';

const STATE = {
  IDLE: 'IDLE',
  FETCHING: 'FETCHING',
  ERROR: 'ERROR',
};

const PRESET_LOGS = [
  '> [SYS] 正在建立加密云端链路...',
  '> [SYS] 云端调度引擎握手成功，正在下发推演指令...',
  '> [SYS] 时空拓扑数据已注入，效用矩阵启动计算...',
];

const ERROR_RESULT = {
  status: 'error',
  error: true,
  logs: [
    '> [SYS] 正在建立加密云端链路...',
    '> [SYS_ERROR] 核心引擎离线，请检查云端算力节点。',
  ],
  solutions: [],
  kpi: null,
};

export default function useSolverEngine() {
  const [status, setStatus] = useState(STATE.IDLE);
  const [result, setResult] = useState(null);
  const abortRef = useRef(null);
  const timerRef = useRef(null);

  const initiate = useCallback((payload = null) => {
    if (status === STATE.FETCHING) return;

    if (abortRef.current) abortRef.current.abort();
    if (timerRef.current) clearTimeout(timerRef.current);

    const controller = new AbortController();
    abortRef.current = controller;
    setStatus(STATE.FETCHING);

    setResult({
      status: 'loading',
      logs: [...PRESET_LOGS],
      solutions: [],
      kpi: null,
    });

    fetch(`${API_URL}/api/execute_solve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload || { use_llm: false }),
      signal: controller.signal,
    })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) => {
        if (controller.signal.aborted) return;
        setResult(data);
        setStatus(STATE.IDLE);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        setResult(ERROR_RESULT);
        setStatus(STATE.ERROR);
        timerRef.current = setTimeout(() => {
          setStatus(prev => prev === STATE.ERROR ? STATE.IDLE : prev);
        }, 5000);
      });
  }, [status]);

  const reset = useCallback(() => {
    if (abortRef.current) abortRef.current.abort();
    if (timerRef.current) clearTimeout(timerRef.current);
    setStatus(STATE.IDLE);
    setResult(null);
  }, []);

  return {
    status,
    result,
    isExecuting: status === STATE.FETCHING,
    isError: status === STATE.ERROR,
    initiate,
    reset,
    kpi: result?.kpi ?? null,
  };
}
