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

### 2. 旧版数据库与模型（已废弃）

| # | 事项 | 状态 |
|---|------|------|
| 2.1 | 旧版数据库模型实现：`Material` + `AnalysisRecord` + `SpectralData` 三表结构 | ✅ 已删除 |
| 2.2 | `Material` 独立表：存储材料类型（Si/SiC/SiO2/Si3N4）及 CRUD API（`materials.py`） | ✅ 已删除 |
| 2.3 | `AnalysisRecord` 表：存储分析结果（含 `filename`、`name`、`material_id` 外键等） | ✅ 已删除 |
| 2.4 | `SpectralData` 表：存储光谱数据点（`wavelength`、`reflectance`、`fitted_reflectance`） | ✅ 已删除 |
| 2.5 | 数据初始化逻辑（`seed.py`）：自动预置 Si/SiC/SiO2/Si3N4 四种材料 | ✅ 已简化 |

### 3. 后端 API

| # | 事项 | 状态 |
|---|------|------|
| 3.1 | 光谱文件上传与解析 API（`data.py` `/api/upload`）—— 支持 csv/txt/xlsx | ✅ |
| 3.2 | 光谱预处理 API（`preprocess.py` `/api/preprocess`）—— 平滑滤波、基线校正、极值检测 | ✅ |
| 3.3 | 厚度反演计算 API（`calculation.py` `/api/calculate`）—— Si/SiC 两光束干涉模型、厚度优化 | ✅ |
| 3.4 | 分析记录 CRUD API（`records.py`）—— 新版 `film_code`/`material_type` 逻辑 | ✅ |

### 4. 前端组件

| # | 事项 | 状态 |
|---|------|------|
| 4.1 | 数据导入组件（`DataImport.vue`）—— 文件上传与解析 | ✅ |
| 4.2 | 预处理面板（`PreprocessPanel.vue`）—— 参数配置与执行 | ✅ |
| 4.3 | 计算面板（`CalculationPanel.vue`）—— 基底材料选择（Si/SiC 卡片）、入射角输入、计算触发 | ✅ |
| 4.4 | 结果展示（`ResultsLog.vue`）+ 光谱图表（`SpectrumChart.vue`） | ✅ |
| 4.5 | 历史记录面板（`DatabasePanel.vue`）—— 表格展示、按 `film_code` 搜索、新版结构 | ✅ |
| 4.6 | 报告模板（`ReportTemplate.vue`）—— 适配新版数据结构 | ✅ |

---

## ✅ 第一阶段：后端数据库重构（已完成）

| # | 事项 | 状态 |
|---|------|------|
| 5.1 | **删除旧版 `Material` 表模型** 及所有关联逻辑 | ✅ 完成 |
| 5.2 | **创建 `film_records` 表**：id / film_code / material_type / thickness_um / r_squared / multi_beam_level / theta_deg / notes / created_at | ✅ 完成 |
| 5.3 | **创建 `optical_data` 表**：id / record_id(FK) / wavelength / reflectance / fitted_reflectance / seq_order | ✅ 完成 |
| 5.4 | 配置外键级联删除：`ON DELETE CASCADE` | ✅ 完成 |
| 5.5 | 删除 `materials.py` 路由文件，注销 `/api/materials` 路由注册 | ✅ 完成 |
| 5.6 | 简化 `seed.py`，移除 `Material` 初始化逻辑 | ✅ 完成 |
| 5.7 | 数据库迁移：新表 `film_records` + `optical_data` 已创建 | ✅ 完成 |

## ✅ 第二阶段：后端 API 重构（已完成）

| # | 事项 | 状态 |
|---|------|------|
| 6.1 | **重构 `records.py` Pydantic 模型**：新增 `film_code` / `material_type` / `theta_deg` / `notes` | ✅ 完成 |
| 6.2 | **POST `/api/records/`**：接收 `film_code` + `material_type` + 光学数据数组 | ✅ 完成 |
| 6.3 | **GET `/api/records/`**：支持按 `film_code` 模糊搜索，分页返回 | ✅ 完成 |
| 6.4 | **GET `/api/records/{id}`**：返回记录信息 + 完整光学数据数组 | ✅ 完成 |
| 6.5 | **DELETE `/api/records/{id}`**：级联删除 `optical_data` | ✅ 完成 |
| 6.6 | **调整 `data.py`**：`/api/upload` 返回数据保留 `filename` 作为临时标识 | ✅ 完成 |
| 6.7 | **检查 `calculation.py`**：确认 `material` 参数透传逻辑无需改动 | ✅ 完成 |

## ✅ 第三阶段：前端组件重构（已完成）

| # | 事项 | 状态 |
|---|------|------|
| 7.1 | **`App.vue` `onSaveRecord`**：弹出对话框收集 `film_code`，传入新结构数据 | ✅ 完成 |
| 7.2 | **`App.vue` `onRetest`**：重测时加载 `film_code` 和原始光学数据 | ✅ 完成 |
| 7.3 | **`DatabasePanel.vue` 表格列**：显示 `film_code` 和 `material_type`，移除 `filename`/`name` | ✅ 完成 |
| 7.4 | **`DatabasePanel.vue` 搜索**：placeholder 改为"搜索薄膜编号..." | ✅ 完成 |
| 7.5 | **`DatabasePanel.vue` `handleRetest`**：传递 `film_code` 加载原始数据 | ✅ 完成 |
| 7.6 | **`CalculationPanel.vue` 保存交互**：由 App 层统一处理 `film_code` 输入 | ✅ 完成 |

## ✅ 第四阶段：前端 API 适配（已完成）

| # | 事项 | 状态 |
|---|------|------|
| 8.1 | **`api/index.js` `saveRecord`**：请求体适配新结构（`film_code`/`material_type`/`theta_deg`/`optical_data`） | ✅ 完成 |
| 8.2 | **`api/index.js` `fetchRecords` / `fetchRecordDetail`**：返回字段适配新结构 | ✅ 完成 |

## ✅ 第五阶段：联调与验证（已完成）

| # | 事项 | 状态 |
|---|------|------|
| 9.1 | **前端构建验证**：npm run build 成功通过，无语法错误 | ✅ 完成 |
| 9.2 | **后端模型验证**：SQLAlchemy 模型导入成功 | ✅ 完成 |
| 9.3 | **数据库表验证**：film_records 和 optical_data 表已创建 | ✅ 完成 |

---

## 数据库新结构速查

### `film_records` 薄膜分析记录表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, Auto | 主键 |
| `film_code` | `VARCHAR(100)` | NOT NULL, Index | 薄膜编号/名称（如 `SiC-15um-A`） |
| `material_type` | `VARCHAR(10)` | NOT NULL | 材质：`Si` 或 `SiC` |
| `thickness_um` | `FLOAT` | | 测算厚度（μm） |
| `r_squared` | `FLOAT` | | 拟合优度 R² |
| `multi_beam_level` | `VARCHAR(50)` | | 多光束干涉判定 |
| `theta_deg` | `FLOAT` | | 入射角（°） |
| `notes` | `TEXT` | nullable | 备注 |
| `created_at` | `DATETIME` | default now | 记录创建时间 |

### `optical_data` 光学数据表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| `id` | `INTEGER` | PK, Auto | 主键 |
| `record_id` | `INTEGER` | FK → film_records.id, ON DELETE CASCADE, Index | 关联记录 |
| `wavelength` | `FLOAT` | NOT NULL | 波长（μm） |
| `reflectance` | `FLOAT` | NOT NULL | 实测反射率 |
| `fitted_reflectance` | `FLOAT` | nullable | 拟合反射率 |
| `seq_order` | `INTEGER` | default 0 | 数据点顺序 |

---

## 🎯 启动项目

### 后端启动
```bash
cd Si
python -m si.main
# 或
uvicorn si.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动
```bash
cd Si/frontend
npm run dev
```

### 前端构建
```bash
cd Si/frontend
npm run build
# 输出: dist/
```