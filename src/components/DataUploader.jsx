import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, CheckCircle2, AlertTriangle } from 'lucide-react';

const MAX_FILE_SIZE = 5 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ['.txt', '.csv'];

export default function DataUploader({ onLoaded }) {
  const [loaded, setLoaded] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState(null);
  const [filename, setFilename] = useState('');
  const [nodeCount, setNodeCount] = useState(0);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    if (!file) return '未检测到文件';
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) return '不支持的文件格式';
    if (file.size > MAX_FILE_SIZE) return '文件体积超限，最大支持 5MB';
    return null;
  };

  const parseFile = (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const text = e.target.result;
        const lines = text.split('\n').filter((line) => line.trim().length > 0);
        const dataLines = lines.slice(1);
        const realCount = dataLines.length;

        setFilename(file.name);
        setNodeCount(realCount);
        setLoaded(true);
        setError(null);

        if (onLoaded) {
          onLoaded({ filename: file.name, nodeCount: realCount, rawData: text });
        }
      } catch (err) {
        setError('文件解析异常：' + err.message);
      }
    };
    reader.onerror = () => {
      setError('文件读取失败');
    };
    reader.readAsText(file);
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) parseFile(file);
  };

  const handleClick = () => {
    if (loaded) return;
    setError(null);
    fileInputRef.current?.click();
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) parseFile(file);
  };

  if (error) {
    return (
      <motion.div
        initial={{ opacity: 0.6, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full border border-red-500/60 bg-black/20 backdrop-blur-xl rounded-lg px-4 py-3 flex items-center gap-3 cursor-pointer"
        style={{
          boxShadow: '0 0 15px rgba(239,68,68,0.2), inset 0 0 12px rgba(239,68,68,0.08)',
        }}
        onClick={() => { setError(null); setLoaded(false); setTimeout(() => fileInputRef.current?.click(), 100); }}
      >
        <AlertTriangle size={16} className="text-red-400 shrink-0" style={{ filter: 'drop-shadow(0 0 6px rgba(239,68,68,0.6))' }} />
        <span className="text-[11px] font-mono text-red-400" style={{ textShadow: '0 0 8px rgba(239,68,68,0.4)' }}>
          [SYS_ERROR] {error}
        </span>
        <input
          type="file"
          accept=".txt,.csv"
          className="hidden"
          ref={fileInputRef}
          onChange={handleFileChange}
        />
      </motion.div>
    );
  }

  if (loaded) {
    return (
      <motion.div
        initial={{ opacity: 0.6, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-full border bg-black/20 backdrop-blur-xl rounded-lg px-4 py-3 flex items-center gap-3 cursor-default"
        style={{
          borderStyle: 'solid',
          borderColor: 'rgba(0,255,157,0.6)',
          boxShadow: '0 0 15px rgba(0,255,157,0.2), inset 0 0 12px rgba(0,255,157,0.08)',
        }}
      >
        <CheckCircle2 size={16} className="text-[#00ff9d] shrink-0" style={{ filter: 'drop-shadow(0 0 6px rgba(0,255,157,0.6))' }} />
        <span className="text-[11px] font-mono text-[#00ff9d]" style={{ textShadow: '0 0 8px rgba(0,255,157,0.4)' }}>
          [系统] 成功挂载 {filename} (识别到 {nodeCount} 个真实计算节点)
        </span>
        <button
          onClick={(e) => { e.stopPropagation(); setLoaded(false); setFilename(''); setNodeCount(0); if (onLoaded) onLoaded(null); }}
          className="ml-auto text-[10px] font-mono text-white/30 hover:text-white/60 transition-colors"
        >
          [重新上传]
        </button>
      </motion.div>
    );
  }

  const isHovered = dragOver;

  return (
    <motion.div
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      animate={
        isHovered
          ? {
              borderColor: 'rgba(255,208,0,1)',
              boxShadow: '0 0 50px rgba(255,208,0,0.5), inset 0 0 20px rgba(255,208,0,0.15)',
              scale: 1.02,
            }
          : {
              borderColor: ['rgba(255,208,0,0.3)', 'rgba(255,208,0,0.7)', 'rgba(255,208,0,0.3)'],
              boxShadow: [
                '0 0 10px rgba(255,208,0,0.1), inset 0 0 15px rgba(255,208,0,0.1)',
                '0 0 25px rgba(255,208,0,0.3), inset 0 0 15px rgba(255,208,0,0.1)',
                '0 0 10px rgba(255,208,0,0.1), inset 0 0 15px rgba(255,208,0,0.1)',
              ],
              scale: 1,
            }
      }
      transition={
        isHovered
          ? { duration: 0.2 }
          : { duration: 3, repeat: Infinity, ease: 'easeInOut' }
      }
      className="w-full bg-black/20 backdrop-blur-xl rounded-lg px-4 py-4 flex items-center justify-center gap-3 cursor-pointer"
      style={{
        borderStyle: isHovered ? 'solid' : 'dashed',
        borderWidth: '1px',
      }}
    >
      <input
        type="file"
        accept=".txt,.csv"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
      />
      <Upload
        size={16}
        className="shrink-0"
        style={{
          color: isHovered ? '#FFD000' : 'rgba(255,208,0,0.5)',
          filter: isHovered ? 'drop-shadow(0 0 8px rgba(255,208,0,0.8))' : 'drop-shadow(0 0 4px rgba(255,208,0,0.3))',
          transition: 'color 0.2s, filter 0.2s',
        }}
      />
      <span
        className="text-[11px] font-mono"
        style={{
          color: isHovered ? '#FFD000' : 'rgba(255,208,0,0.5)',
          textShadow: isHovered ? '0 0 8px rgba(255,208,0,0.8)' : '0 0 4px rgba(255,208,0,0.2)',
          transition: 'color 0.2s, text-shadow 0.2s',
        }}
      >
        [ 拖拽或点击上传时空拓扑数据集 (.txt / .csv) ]
      </span>
    </motion.div>
  );
}
