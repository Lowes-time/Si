# 基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0

面向 Si / SiC 等半导体外延层的 **FTIR 反射光谱膜厚反演** Web 系统。用户导入光谱 → 预处理 → 自适应干涉模型拟合 → 结果入库、导出与报告。

技术栈：**FastAPI + Vue3 + ECharts + SQLAlchemy + SQLite**

---

## 1. 系统功能

| 模块 | 功能 |
|------|------|
| 数据导入 | CSV/TXT/XLSX 上传，内置样例，手动粘贴 |
| 预处理 | SG/MA 滤波、波长裁剪、自动最优区间、ALS 基线、SiC Reststrahlen 剔除 |
| 厚度反演 | 双光束 / Airy 多光束自适应、FFT 初值、差分进化 + LM 精修 |
| 可视化 | 原始/拟合/残差图，框选波长范围，dataZoom 缩放 |
| 数据管理 | SQLite 持久化，按薄膜编号检索，重测，Excel/PDF/打印报告 |

---

## 2. 目录结构

```
Si/
├── frontend/                 # Vue3 前端
│   ├── src/
│   │   ├── App.vue           # 主布局、流程状态、双视图切换
│   │   ├── api/index.js      # HTTP 接口封装
│   │   ├── main.js           # 入口
│   │   └── components/
│   │       ├── DataImport.vue       # 数据导入
│   │       ├── PreprocessPanel.vue  # 预处理参数
│   │       ├── CalculationPanel.vue # 材料、入射角、计算
│   │       ├── ResultsLog.vue       # 结果指标与保存/导出
│   │       ├── SpectrumChart.vue    # ECharts 光谱图
│   │       ├── DatabasePanel.vue    # 历史记录 CRUD
│   │       └── ReportTemplate.vue   # 浏览器打印报告
│   └── vite.config.js        # 开发代理 /api → :8000
├── src/si/                   # Python 后端
│   ├── main.py               # FastAPI 入口、路由注册
│   ├── algorithms/
│   │   ├── models.py         # 干涉正演与反演核心
│   │   ├── optical_constants.py  # Sellmeier 折射率
│   │   ├── preprocess.py     # 平滑、极值检测
│   │   ├── advanced_preprocess.py # ALS、Reststrahlen
│   │   └── advanced_stats.py # 置信区间、SNR
│   ├── backend/
│   │   ├── api/
│   │   │   ├── data.py       # 文件上传解析
│   │   │   ├── preprocess.py # 预处理 API
│   │   │   ├── calculation.py# 厚度反演 API
│   │   │   ├── records.py    # 记录 CRUD + PDF
│   │   │   └── materials.py  # 材料列表
│   │   ├── models.py         # ORM：film_records / optical_data
│   │   ├── database.py       # SQLite 连接
│   │   ├── config.py         # 应用配置
│   │   ├── exceptions.py     # 异常处理
│   │   └── seed.py           # 数据库初始化
│   └── utils/
│       └── pdf_generator.py  # fpdf2 报告生成
├── test_api.py               # 接口联调脚本
├── test_si_2um.csv           # 样例数据
├── test_sic_15um.csv
├── test_sic_30um.csv
├── pyproject.toml
└── requirements.txt
```

---

## 3. 算法说明

### 3.1 流程

```
原始光谱 → SG 平滑 → 极值检测 + FFT 光程差初值
         → 四指标多光束判定（对比度/峰度/精细度/相干比）
         → 弱干涉: 双光束 + least_squares
         → 中强干涉: Airy + differential_evolution + least_squares
         → 输出厚度、R²、置信半径、拟合曲线
```

### 3.2 核心公式

- **相位差**：δ = 4π n d cosθ / λ
- **双光束**：界面 Fresnel 反射叠加近似
- **Airy 多光束**：R = (r₀₁² + r₁₂² + 2r₀₁r₁₂cosδ) / (1 + r₀₁²r₁₂² + 2r₀₁r₁₂cosδ)
- **FFT 厚度**：对去均值光谱做 FFT，光程差峰 → d = OPD / (2n cosθ)

参考文献思路：MDPI Sensors 2026（SiC 多光束校正）、MMAA FFT 峰度判定、Transfer Matrix / Airy 多光束拟合。

---

## 4. API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传光谱文件 |
| POST | `/api/preprocess` | 预处理（可选 ALS、Reststrahlen） |
| POST | `/api/calculate` | 厚度反演 |
| POST | `/api/export` | 导出 Excel |
| GET | `/api/materials` | 材料列表 |
| POST | `/api/records/` | 新建记录 |
| GET | `/api/records/` | 分页列表（search=薄膜编号） |
| GET | `/api/records/{id}` | 记录详情 |
| GET | `/api/records/{id}/report` | 下载 PDF |
| DELETE | `/api/records/{id}` | 删除记录 |

**计算请求示例：**

```json
{
  "wavelength": [5.0, 5.1, 5.2],
  "reflectance": [0.45, 0.52, 0.48],
  "material": "SIC",
  "theta_deg": 10.0
}
```

数据库文件：`~/.si_thickness/si_data.db`

---

## 5. 启动方式

### 后端

```bash
cd Si
pip install -r requirements.txt
# 若项目路径含中文，勿使用 pip install -e .，改用 PYTHONPATH：
# Windows: set PYTHONPATH=%CD%\src
# Linux/macOS: export PYTHONPATH=$PWD/src
python -m uvicorn si.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd Si/frontend
npm install
npm run dev
# 浏览器 http://localhost:5173
```

### 构建

```bash
cd frontend && npm run build
```

### 接口测试

```bash
# 先启动后端
python test_api.py
```

---

## 6. 软著代码文档提取建议

共约 60 页 × 50 行，推荐顺序：

1. **前端交互**（约 20 页）：`App.vue` → `SpectrumChart.vue` → `CalculationPanel.vue`
2. **后端 API**（约 15 页）：`main.py` → `calculation.py` → `records.py`
3. **算法内核**（约 25 页）：`models.py` → `optical_constants.py` → `preprocess.py`

复制到 Word 时删除空行，保证每页有效代码 ≥ 50 行。

---

## 7. 版本信息

- 版本：V1.0
- Python：≥ 3.12
- 前端：Vue 3 + Element Plus + ECharts 5
