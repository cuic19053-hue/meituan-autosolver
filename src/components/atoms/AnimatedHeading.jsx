import React, { useState, useEffect } from 'react';

export default function AnimatedHeading({ text, className = "", style = {} }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setVisible(true), 300);
    return () => clearTimeout(timer);
  }, []);

  const lines = text.split('\n');

  return (
    <h1
      className={`${className} transition-all duration-1000`}
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(20px)',
        ...style
      }}
    >
      {lines.map((line, i) => (
        <div key={i} className="leading-tight">
          {line}
        </div>
      ))}
    </h1>
  );
}
