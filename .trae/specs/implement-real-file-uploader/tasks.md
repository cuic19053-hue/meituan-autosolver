# Tasks

- [x] Task 1: 重写 DataUploader.jsx 实现真实文件读取
  - [x] 添加 `useRef` 引用隐藏 file input
  - [x] 添加 `<input type="file" accept=".txt,.csv" className="hidden" ref={fileInputRef} onChange={handleFileChange} />`
  - [x] 容器 onClick → `fileInputRef.current.click()`
  - [x] 保留 onDragOver/onDragLeave/onDrop 事件 + isDragging 高亮
  - [x] 实现 FileReader.readAsText(file) 解析
  - [x] 文件大小验证（5MB）+ 类型验证（.txt/.csv）
  - [x] reader.onload 中按行分割 + 过滤空行 + 计算真实节点数
  - [x] try-catch 捕获异常
  - [x] 成功态动态显示：`[系统] 成功挂载 {filename} (识别到 {nodeCount} 个真实计算节点)`
  - [x] 错误态显示红色提示
  - [x] 解析成功后调用 `onLoaded({ filename, nodeCount, rawData })`
  - [x] 保留所有 Framer Motion 动效

- [x] Task 2: 适配 App.jsx onDatasetLoaded 回调
  - [x] 将 `onDatasetLoaded={setDatasetLoaded}` 改为接收对象并设 `datasetLoaded = true`
  - [x] 保持 handleReset 中 `setDatasetLoaded(false)` 不变

# Task Dependencies
- 所有 Task 已完成