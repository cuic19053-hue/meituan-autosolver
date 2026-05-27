import React from 'react';

export default function StatusDot({ active = true, color = "#00FF41", size = "sm" }) {
  const sizeMap = { sm: "h-2 w-2", md: "h-3 w-3", lg: "h-4 w-4" };
  return (
    <span className="relative flex">
      {active && (
        <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75`}
          style={{ backgroundColor: color }} />
      )}
      <span className={`relative inline-flex rounded-full ${sizeMap[size]}`}
        style={{ backgroundColor: active ? color : "#525252" }} />
    </span>
  );
}
