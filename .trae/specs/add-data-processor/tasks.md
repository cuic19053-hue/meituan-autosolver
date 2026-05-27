# Tasks

- [x] Task 1: 创建 `backend/data_processor.py` 数据解析模块
  - [x] SubTask 1.1: 实现 `parse_seed_file()` 函数，解析 `large_seed301.txt`（tab 分隔，4 列），处理编码 fallback（utf-8 → gbk → latin-1）
  - [x] SubTask 1.2: 实现 `assign_coordinates()` 函数，为唯一 TaskID 分配中心区域坐标，为唯一 CourierID 分配边缘区域坐标，确保确定性映射（同一 ID 返回相同坐标）
  - [x] SubTask 1.3: 实现 `build_graph_data()` 主函数，整合解析 + 坐标映射，返回 `{nodes: [...], links: [...]}` 字典
  - [x] SubTask 1.4: 添加控制台日志打印（文件路径、解析行数、唯一 TaskID/CourierID 数量）

- [x] Task 2: 修改 `backend/main.py`，新增 `GET /api/raw_data` 接口
  - [x] SubTask 2.1: 在模块顶层导入 `data_processor` 并调用 `build_graph_data()` 初始化缓存
  - [x] SubTask 2.2: 实现 `GET /api/raw_data` 路由，返回缓存的 nodes/links JSON
  - [x] SubTask 2.3: 处理文件缺失异常，返回错误信息

- [x] Task 3: 创建 `large_seed301.txt` 样本数据文件
  - [x] SubTask 3.1: 将用户提供的样本数据写入项目根目录 `large_seed301.txt`

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] independent, can run in parallel with Task 1
