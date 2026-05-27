# DataUploader 真实本地文件读取与动态解析 Spec

## Why
当前 DataUploader 组件是纯 Mock 实现（点击直接设 loaded=true，硬编码显示 "large_seed301.txt (301 个拓扑节点)"），无法读取真实文件。需要利用 HTML5 FileReader API 实现真实的拖拽/点击上传与动态解析。

## What Changes
- **`DataUploader.jsx`**：添加隐藏 file input + FileReader 解析 + 动态节点计数 + 错误处理
- **`App.jsx`**：`onDatasetLoaded` 回调从 `setDatasetLoaded(true)` 改为接收解析结果对象

## Impact
- Affected code:
  - `d:\美团\src\components\DataUploader.jsx`
  - `d:\美团\src\App.jsx`（微调 onDatasetLoaded 回调）

## ADDED Requirements

### Requirement 1: 隐藏文件输入 (Hidden Input & Ref)
系统 SHALL 在 DataUploader 内部添加 `<input type="file" accept=".txt,.csv" className="hidden" ref={fileInputRef} onChange={handleFileChange} />`。
系统 SHALL 在容器 onClick 时调用 `fileInputRef.current.click()` 唤起文件选择器。

#### Scenario: 点击上传
- **WHEN** 用户点击 DataUploader 容器
- **THEN** 浏览器文件选择器弹出
- **AND** 用户选择 .txt 或 .csv 文件后触发 handleFileChange

### Requirement 2: 拖拽接驳 (Drag & Drop)
系统 SHALL 为容器绑定 onDragOver、onDragLeave、onDrop 事件。
系统 SHALL 在 onDragOver 和 onDrop 中调用 `e.preventDefault()`。
系统 SHALL 使用 `isDragging` 状态控制容器高亮反馈。

#### Scenario: 拖拽上传
- **WHEN** 用户拖拽文件到容器上方
- **THEN** 容器高亮为荧光黄
- **WHEN** 用户释放文件
- **THEN** 触发文件解析流程

### Requirement 3: FileReader 沙盒解析
系统 SHALL 验证文件大小（5MB 以内）和类型（.txt/.csv）。
系统 SHALL 使用 `FileReader.readAsText(file)` 读取文件。
系统 SHALL 在 `reader.onload` 中按行分割文本，过滤空行，计算真实节点数。
系统 SHALL 使用 try-catch 捕获文件读取异常。

#### Scenario: 解析成功
- **WHEN** 用户上传有效的 .txt 文件
- **THEN** 组件进入绿色成功态
- **AND** 显示 `[系统] 成功挂载 {filename} (识别到 {nodeCount} 个真实计算节点)`

#### Scenario: 文件过大
- **WHEN** 用户上传超过 5MB 的文件
- **THEN** 显示红色错误提示 `[SYS_ERROR] 文件体积超限，最大支持 5MB`

#### Scenario: 文件类型错误
- **WHEN** 用户上传非 .txt/.csv 文件
- **THEN** 显示红色错误提示 `[SYS_ERROR] 不支持的文件格式`

### Requirement 4: 状态联级汇报 (State Uplift)
系统 SHALL 在解析成功后调用 `onLoaded({ filename, nodeCount, rawData })`。
App.jsx 的 `onDatasetLoaded` 回调 SHALL 接收此对象并设置 `datasetLoaded = true`。

#### Scenario: 上传成功后按钮可用
- **WHEN** DataUploader 解析成功
- **THEN** `datasetLoaded` 变为 true
- **AND** `[ 启动云端全息推演 ]` 按钮变为可点击

### Requirement 5: 约束保证
系统 MUST 保留所有 Framer Motion 发光与呼吸动效。
系统 MUST 保留现有的 CSS 样式和 Tailwind 类名。