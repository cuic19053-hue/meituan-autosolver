# 数据处理器与原始数据 API Spec

## Why
当前后端 (`backend/main.py`) 使用硬编码的模拟数据（`SPATIAL_NODES` / `PART_CATALOG`），无法反映真实的物流调度场景。需要解析项目根目录的 `large_seed301.txt` 文件，将真实的 Task-Courier 分配数据转化为前端可消费的图结构 JSON，支撑空间运筹可视化。

## What Changes
- 新增 `backend/data_processor.py`：解析 `large_seed301.txt`，构建 nodes/links 图结构，自动分配空间坐标
- 修改 `backend/main.py`：新增 `GET /api/raw_data` 接口，返回解析后的 JSON
- 新增 `large_seed301.txt`：项目根目录的 tab 分隔原始数据文件（用户提供）

## Impact
- Affected specs: 前端 Command Center 的数据源从模拟数据切换为真实数据
- Affected code: `backend/main.py`（新增路由）、新增 `backend/data_processor.py`

## ADDED Requirements

### Requirement: 数据文件解析
系统 SHALL 提供 `data_processor.py` 模块，解析项目根目录下的 `large_seed301.txt` 文件。

- 文件格式：tab 分隔，4 列：`task_id_list`, `courier_id`, `total_score`, `willingness`
- `task_id_list` 列包含逗号分隔的多个 TaskID（如 `T0037,T0039`）
- 解析时 SHALL 处理编码问题（优先 `utf-8`，fallback `gbk`/`latin-1`）
- 解析成功后 SHALL 在控制台打印日志：文件路径、解析行数、唯一 TaskID 数、唯一 CourierID 数

#### Scenario: 正常解析
- **WHEN** `large_seed301.txt` 存在且格式正确
- **THEN** 返回包含 nodes 和 links 的字典，nodes 包含所有唯一 TaskID 和 CourierID，links 包含所有分配关系

#### Scenario: 文件编码异常
- **WHEN** 文件编码非 UTF-8
- **THEN** 自动尝试 GBK 和 Latin-1 编码，确保解析成功

#### Scenario: 文件不存在
- **WHEN** `large_seed301.txt` 不存在
- **THEN** 抛出 `FileNotFoundError` 并打印明确的错误日志

### Requirement: 空间坐标自动映射
系统 SHALL 为每个唯一的 TaskID 和 CourierID 自动分配 `(x, y)` 坐标。

- TaskID：随机分布在中心区域（坐标范围中心 ±30%）
- CourierID：均匀分布在边缘区域（坐标范围外圈 70%-100%）
- 坐标空间：归一化到 `[0, 1000]` 范围
- 同一 ID 多次出现时 SHALL 返回相同坐标（确定性映射）

#### Scenario: 坐标分配
- **WHEN** 解析到唯一 TaskID `T0037`
- **THEN** 为其分配一个中心区域的 `(x, y)` 坐标，且后续再次遇到 `T0037` 时返回相同坐标

#### Scenario: CourierID 坐标分配
- **WHEN** 解析到唯一 CourierID `C028`
- **THEN** 为其分配一个边缘区域的 `(x, y)` 坐标

### Requirement: 原始数据 API 接口
系统 SHALL 在 `main.py` 中提供 `GET /api/raw_data` 接口。

- 返回 JSON 格式：
  ```json
  {
    "nodes": [
      {"id": "T0037", "type": "task", "x": 450, "y": 520},
      {"id": "C028", "type": "courier", "x": 850, "y": 120}
    ],
    "links": [
      {"source": "C028", "target": ["T0037", "T0039"], "score": 52.016, "willingness": 0.582}
    ]
  }
  ```
- `nodes` 中每个节点包含 `id`、`type`（`task` 或 `courier`）、`x`、`y`
- `links` 中每条边包含 `source`（courier_id）、`target`（task_id_list 数组）、`score`（total_score）、`willingness`
- 接口 SHALL 在服务启动时解析文件并缓存结果，避免每次请求重新读取

#### Scenario: API 调用成功
- **WHEN** 客户端发送 `GET /api/raw_data`
- **THEN** 返回 HTTP 200 和上述 JSON 结构

#### Scenario: 数据文件缺失
- **WHEN** `large_seed301.txt` 不存在时调用 `GET /api/raw_data`
- **THEN** 返回 HTTP 500 和错误信息 `{"error": "数据文件未找到: ..."}`

## MODIFIED Requirements

### Requirement: CORS 配置
现有 CORS 中间件配置不变，`/api/raw_data` 接口自动受现有 CORS 策略保护。

## REMOVED Requirements

（无移除项）
