import React from 'react';

export default function Sparkline() {
  const points = [3, 5, 2, 6, 4, 7, 5, 8, 6, 9, 7, 10];
  const max = Math.max(...points);
  const w = 44;
  const h = 8;
  const step = w / (points.length - 1);
  const d = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${(i * step).toFixed(1)},${(h - (p / max) * h).toFixed(1)}`)
    .join(" ");
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      <path d={d} fill="none" stroke="#00FF41" strokeWidth="1" strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}
