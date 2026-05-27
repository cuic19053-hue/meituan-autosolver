import React from 'react';

export default function CityGrid() {
  return (
    <svg
      viewBox="0 0 800 600"
      preserveAspectRatio="xMidYMid slice"
      className="absolute inset-0 h-full w-full opacity-10 text-gray-800"
      aria-hidden="true"
    >
      <g fill="none" stroke="currentColor" strokeWidth="0.6">
        <circle cx="400" cy="300" r="60" />
        <circle cx="400" cy="300" r="110" />
        <circle cx="400" cy="300" r="170" />
        <circle cx="400" cy="300" r="240" />
        <circle cx="400" cy="300" r="310" />
      </g>
      <g stroke="currentColor" strokeWidth="0.5">
        <line x1="400" y1="0" x2="400" y2="600" />
        <line x1="0" y1="300" x2="800" y2="300" />
        <line x1="80" y1="60" x2="720" y2="540" />
        <line x1="720" y1="60" x2="80" y2="540" />
        <line x1="120" y1="300" x2="680" y2="300" transform="rotate(30 400 300)" />
        <line x1="120" y1="300" x2="680" y2="300" transform="rotate(-30 400 300)" />
      </g>
      <g fill="currentColor">
        {[
          [400, 300], [340, 240], [460, 240], [340, 360], [460, 360],
          [400, 180], [400, 420], [280, 300], [520, 300],
          [220, 200], [580, 200], [220, 400], [580, 400],
        ].map(([cx, cy], i) => (
          <circle key={i} cx={cx} cy={cy} r="2" />
        ))}
      </g>
      <g stroke="currentColor" strokeWidth="0.25" opacity="0.6">
        {Array.from({ length: 16 }).map((_, i) => (
          <line key={`v${i}`} x1={i * 50} y1="0" x2={i * 50} y2="600" />
        ))}
        {Array.from({ length: 12 }).map((_, i) => (
          <line key={`h${i}`} x1="0" y1={i * 50} x2="800" y2={i * 50} />
        ))}
      </g>
      <g stroke="#FFD000" strokeWidth="0.4" opacity="0.5" strokeDasharray="2 3">
        <line x1="400" y1="300" x2="220" y2="200" />
        <line x1="400" y1="300" x2="580" y2="200" />
        <line x1="400" y1="300" x2="220" y2="400" />
        <line x1="400" y1="300" x2="580" y2="400" />
        <line x1="400" y1="300" x2="400" y2="180" />
      </g>
    </svg>
  );
}
