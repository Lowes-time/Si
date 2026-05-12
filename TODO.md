# 半导体薄膜厚度光学测量分析系统 —— 数据库重构 TODO

> 目标：重构数据库为两个表（`film_records` 薄膜分析记录表 + `optical_data` 光学数据表），以薄膜编号/名称（`film_code`）作为核心标识，替代原有的文件名（`filename`）和独立的 `Material` 表。

---

## ✅ 已完成

### 1. 项目基础框架

| # | 事项 | 状态 |
|---|------|------|
| 1.1 | FastAPI 后端服务搭建（`main.py`、`config.py`、`exceptions.py`） | ✅ |
| 1.2 | SQLAlchemy 数据库连接配置（`database.py`，SQLite 存储于 `~/.si_thickness/si_data.db`） | ✅ |
| 1.3 | 前端 Vue 项目搭建（Vite + Element Plus） | ✅ |
| 1.4 | 前端页面布局与路由（`App.vue` 双视图：实时分析 / 历史记录） | ✅ |
| 1.5 | 前端 API 封装（`frontend/src/api/index.js`） | ✅ |

### 2. 旧版数据库与模型（将被废弃）

| # | 事项 | 状态 |
|---|------|------|
| 2.1 | 旧版数据库模型实现：`Material` + `AnalysisRecord` + `SpectralData` 三表结构 | ✅ |
| 2.2 | `Material` 独立表：存储材料类型（Si/SiC/SiO2/Si3N4）及 CRUD API（`materials.py`） | ✅ |
| 2.3 | `AnalysisRecord` 表：存储分析结果（含 `filename`、`name`、`material_id` 外键等） | ✅ |
| 2.4 | `SpectralData` 表：存储光谱数据点（`wavelength`、`reflectance`、`fitted_reflectance`） | ✅ |
| 2.5 | 数据初始化逻辑（`seed.py`）：自动预置 Si/SiC/SiO2/Si3N4 四种材料 | ✅ |

### 3. 后端 API（旧逻辑）

| # | 事项 | 状态 |
|---|------|------|
| 3.1 | 光谱文件上传与解析 API（`data.py` `/api/upload`）—— 支持 csv/txt/xlsx，返回 filename + 数据数组 | ✅ |
| 3.2 | 光谱预处理 API（`preprocess.py` `/api/preprocess`）—— 平滑滤波、基线校正、极值检测 | ✅ |
| 3.3 | 厚度反演计算 API（`calculation.py` `/api/calculate`）—— Si/SiC 两光束干涉模型、厚度优化 | ✅ |
| 3.4 | 分析记录 CRUD API（`records.py`）—— 保存/查询/详情/删除，关联 Material 表 | ✅ |

### 4. 前端组件（旧逻辑）

| # | 事项 | 状态 |
|---|------|------|
| 4.1 | 数据导入组件（`DataImport.vue`）—— 文件上传与解析 | ✅ |
| 4.2 | 预处理面板（`PreprocessPanel.vue`）—— 参数配置与执行 | ✅ |
| 4.3 | 计算面板（`CalculationPanel.vue`）—— 基底材料选择（Si/SiC 卡片）、入射角输入、计算触发 | ✅ |
| 4.4 | 结果展示（`ResultsLog.vue`）+ 光谱图表（`SpectrumChart.vue`） | ✅ |
| 4.5 | 历史记录面板（`DatabasePanel.vue`）—— 表格展示、按 filename 搜索、打印报告、删除、重测 | ✅ |

---

## ⏳ 待完成（按执行顺序排列）

### 第一阶段：后端数据库重构

| # | 事项 | 状态 |
|---|------|------|
| 5.1 | **删除旧版 `Material` 表模型** 及所有关联逻辑（`models.py`、`materials.py`、`seed.py`） | ⏳ |
| 5.2 | **创建 `film_records` 表（薄膜分析记录表）**：字段 `id` / `film_code`(VARCHAR,NN,Index) / `material_type`(VARCHAR,NN) / `thickness_um` / `r_squared` / `multi_beam_level` / `theta_deg` / `notes` / `created_at` | ⏳ |
| 5.3 | **创建 `optical_data` 表（光学数据表）**：字段 `id` / `record_id`(FK→film_records.id,CASCADE,Index) / `wavelength`(NN) / `reflectance`(NN) / `fitted_reflectance`(nullable) / `seq_order` | ⏳ |
| 5.4 | 配置外键级联删除：`ON DELETE CASCADE`，确保删除 `film_records` 记录时自动清理关联的 `optical_data` | ⏳ |
| 5.5 | 删除 `materials.py` 路由文件，并在 `main.py` 中注销 `/api/materials` 路由注册 | ⏳ |
| 5.6 | 删除 `seed.py` 中的 `Material` 初始化逻辑，简化 `main.py` 启动时不再调用 `seed_materials()` | ⏳ |
| 5.7 | 处理数据库迁移：由于表结构完全变更，旧版 `si_data.db` 需要删除重建（或增加检测自动重建逻辑） | ⏳ |

### 第二阶段：后端 API 重构

| # | 事项 | 状态 |
|---|------|------|
| 6.1 | **重构 `records.py` Pydantic 模型**：`RecordCreate` / `RecordResponse`，去掉 `filename`/`name`，新增 `film_code` / `material_type` / `theta_deg` / `notes` | ⏳ |
| 6.2 | **POST `/api/records/`**：接收 `film_code` + `material_type` + 计算结果 + `optical_data` 数组，先写 `film_records` 再批量写 `optical_data` | ⏳ |
| 6.3 | **GET `/api/records/`**：查询列表，支持按 `film_code` 模糊搜索，分页返回 `skip`/`limit` | ⏳ |
| 6.4 | **GET `/api/records/{id}`**：查询详情，返回记录信息 + 关联的完整光学数据数组（wavelength/reflectance/fitted_reflectance） | ⏳ |
| 6.5 | **DELETE `/api/records/{id}`**：删除记录，依赖外键级联自动清理 `optical_data` | ⏳ |
| 6.6 | **调整 `data.py`**：`/api/upload` 返回数据中去掉 `filename` 字段，仅保留解析后的光学数组和统计信息（`row_count`、`wl_min`、`wl_max`） | ⏳ |
| 6.7 | **检查 `calculation.py`**：确认 `material` 参数透传逻辑（Si/SiC）无需改动，确保与新模型无冲突 | ⏳ |

### 第三阶段：前端组件重构

| # | 事项 | 状态 |
|---|------|------|
| 7.1 | **`App.vue` `onSaveRecord` 改造**：保存前弹出对话框收集 `film_code`（薄膜编号），向服务端传入 `film_code` + `material_type` + `theta_deg` + 计算结果 + 光学数据，替代原有的 `filename` | ⏳ |
| 7.2 | **`App.vue` `onRetest` 改造**：重测时从服务端获取 `film_code` 和原始光学数据，不再拼接 `filename`，将 `film_code` 带入分析视图供复用 | ⏳ |
| 7.3 | **`DatabasePanel.vue` 表格列改造**：去掉 `filename` 列和 `name` 列，新增 `film_code`（薄膜编号）列和 `material_type`（材质标签）列，调整列宽和格式化 | ⏳ |
| 7.4 | **`DatabasePanel.vue` 搜索改造**：搜索框 placeholder 改为"搜索薄膜编号..."，搜索参数指向 `film_code` 模糊匹配 | ⏳ |
| 7.5 | **`DatabasePanel.vue` `handleRetest` 改造**：重测时传递 `film_code` 而非 `filename`，加载原始 `wavelength` + `reflectance`（不含 fitted） | ⏳ |
| 7.6 | **`CalculationPanel.vue` 保存交互**：点击"保存入库"时，若 App 层面未提供 `film_code`，提示用户先输入薄膜编号 | ⏳ |

### 第四阶段：前端 API 适配

| # | 事项 | 状态 |
|---|------|------|
| 8.1 | **`api/index.js` `saveRecord`**：确认请求体结构调整，新增 `film_code` / `material_type` / `theta_deg` / `notes`，去掉 `filename` | ⏳ |
| 8.2 | **`api/index.js` `fetchRecords` / `fetchRecordDetail`**：确认返回字段适配新结构（`film_code`、`material_type` 替代 `filename`、`material`） | ⏳ |

### 第五阶段：联调与验证

| # | 事项 | 状态 |
|---|------|------|
| 9.1 | **端到端测试**：上传 `test_sic_15um.csv` → 输入薄膜编号（如 `SiC-15um-标样A`）→ 选择 SiC → 计算 → 保存 → 在历史记录中查询到该记录 | ⏳ |
| 9.2 | **重测流程验证**：在历史记录面板点击"重测" → 加载原始光学数据到分析视图 → 调整入射角重新计算 → 保存为新记录，验证 `film_code` 被保留 | ⏳ |
| 9.3 | **删除流程验证**：删除某条记录 → 验证 `film_records` 和关联的 `optical_data` 均被清理 | ⏳ |
| 9.4 | **材质区分验证**：分别用 Si 和 SiC 材质上传不同 CSV，验证 `material_type` 正确保存且计算模型调用正确 | ⏳ |

---

## 数据库新结构速查

### `film_records` 薄膜分析记录表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, Auto | 主键 |
| `film_code` | `VARCHAR(100)` | NOT NULL, Index | 薄膜编号/名称（用户命名，如 `SiC-15um-A`）|
| `material_type` | `VARCHAR(10)` | NOT NULL | 材质：`Si` 或 `SiC` |
| `thickness_um` | `FLOAT` | | 测算厚度（μm）|
| `r_squared` | `FLOAT` | | 拟合优度 R² |
| `multi_beam_level` | `VARCHAR(50)` | | 多光束干涉判定 |
| `theta_deg` | `FLOAT` | | 入射角（°）|
| `notes` | `TEXT` | nullable | 备注 |
| `created_at` | `DATETIME` | default now | 记录创建/计算时间 |

### `optical_data` 光学数据表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, Auto | 主键 |
| `record_id` | `INTEGER` | FK → `film_records.id`, ON DELETE CASCADE, Index | 关联到历史记录表 |
| `wavelength` | `FLOAT` | NOT NULL | 波长（μm）|
| `reflectance` | `FLOAT` | NOT NULL | 实测反射率 |
| `fitted_reflectance` | `FLOAT` | nullable | 拟合反射率（可选）|
| `seq_order` | `INTEGER` | default 0 | 数据点顺序 |
