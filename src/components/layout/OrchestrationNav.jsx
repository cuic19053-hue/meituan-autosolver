import React from 'react';
import StatusDot from '../atoms/StatusDot';

const navLinks = ["时空拓扑", "运力矩阵", "效用归因"];

export default function OrchestrationNav({ brand = "AutoSolver", version = "云端智能运筹中枢", isError = false }) {
  return (
    <nav className="flex items-center justify-between rounded-xl px-4 py-2 bg-black/40 backdrop-blur-md border border-white/10">
      <div className="flex items-center gap-2">
        <span className="text-xl font-semibold tracking-[0.18em]">{brand}</span>
        <span className="font-mono text-[10px] uppercase tracking-wider text-white/40 border border-white/15 rounded px-1.5 py-0.5">
          {version}
        </span>
      </div>
      <div className="hidden md:flex items-center gap-8">
        {navLinks.map((l) => (
          <a
            key={l}
            href="javascript:void(0)"
            className="font-mono text-xs uppercase tracking-[0.15em] text-white/70 transition-colors hover:text-[#FFD000]"
          >
            {l}
          </a>
        ))}
      </div>
      <div className="flex items-center gap-2 font-mono text-xs text-white/50">
        <StatusDot color={isError ? "#FF4444" : "#00FF41"} />
        <span>{isError ? "引擎离线 · 等待重连" : "云网协同 · 全息推演中"}</span>
      </div>
    </nav>
  );
}
