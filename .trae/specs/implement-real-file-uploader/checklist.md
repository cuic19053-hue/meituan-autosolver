# Checklist

- [x] DataUploader.jsx: 隐藏 file input 存在且可触发
- [x] DataUploader.jsx: 点击容器唤起文件选择器
- [x] DataUploader.jsx: 拖拽文件到容器时高亮
- [x] DataUploader.jsx: 拖拽释放触发文件解析
- [x] DataUploader.jsx: FileReader.readAsText 正确读取文件
- [x] DataUploader.jsx: 文件大小验证（5MB 限制）
- [x] DataUploader.jsx: 文件类型验证（.txt/.csv）
- [x] DataUploader.jsx: 真实节点数动态计算
- [x] DataUploader.jsx: 成功态显示真实文件名和节点数
- [x] DataUploader.jsx: 错误态显示红色提示
- [x] DataUploader.jsx: try-catch 捕获异常
- [x] DataUploader.jsx: onLoaded 传递 { filename, nodeCount, rawData }
- [x] DataUploader.jsx: Framer Motion 动效保留
- [x] App.jsx: onDatasetLoaded 正确接收对象并设 datasetLoaded=true