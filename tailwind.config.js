/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          gold: '#FFD000',
          'ai-blue': '#00d4ff',
          'ai-green': '#34D399',
          orange: '#ff6b35',
          purple: '#C084FC',
          red: '#F87171',
          blue: '#60A5FA',
        },
        surface: {
          'bg': '#0A0A0A',
          'card': 'rgba(0,0,0,0.4)',
          'glass': 'rgba(0,0,0,0.7)',
        },
        line: {
          dim: '#262626',
          subtle: 'rgba(255,255,255,0.1)',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      animation: {
        'breathe': 'breathe 2s ease-in-out infinite',
        'flow-dash': 'flowDash 1.2s linear infinite',
        'blink': 'blink 0.8s step-end infinite',
        'ping-slow': 'ping 2.5s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { opacity: '0.4' },
          '50%': { opacity: '1.0' },
        },
        flowDash: {
          '0%': { strokeDashoffset: '24' },
          '100%': { strokeDashoffset: '0' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
      boxShadow: {
        'glow-gold': '0 0 20px rgba(255,208,0,0.1), 0 0 40px rgba(255,208,0,0.05)',
        'glow-cyan': '0 0 30px rgba(0,212,255,0.2)',
        'glow-orange': '0 0 20px rgba(255,107,53,0.15), 0 0 60px rgba(255,107,53,0.05)',
      },
    },
  },
  plugins: [],
}
