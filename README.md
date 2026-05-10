基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0

1. 系统简介 (软著申报专用说明)

本系统是一款面向半导体材料（Si/SiC）制造与检测环节的专业级工业软件。系统采用前沿的 前后端分离 (B/S) 架构：

前端 (Frontend)： 基于 Vue.js 3.0 框架构建，提供现代化的 Web 用户交互界面、数据导入向导、以及基于 ECharts 的高逼真度光谱数据与残差可视化分析。

后端 (Backend)： 基于 Python FastAPI 构建高性能算法服务 API。集成了自主优化的双光束干涉模型、多光束干涉判定与校正模型（Airy模型结合差分进化算法），实现亚微米级的高精度膜厚反演。

软著申请定位： 本项目拥有完整的用户交互闭环、独立可运行的服务端与客户端代码、以及具有高度独创性的干涉反演算法内核，完全符合中国计算机软件著作权申请标准。

2. 工程目录结构与模块说明

lowes-time/si/Si-zym/
├── frontend/                     # 🖥️ 前端工程 (Vue 3)
│   ├── package.json              # 前端依赖配置
│   ├── vite.config.js            # 构建工具配置
│   └── src/
│       ├── api/index.js          # 与后端的 HTTP 请求拦截与接口封装
│       ├── App.vue               # 前端主入口与页面核心视图 (集成Echarts图表)
│
├── src/si/                       # ⚙️ 后端工程 (Python)
│   ├── main.py                   # 后端服务主入口 (启动 FastAPI 服务)
│   ├── algorithms/               # 🌟 核心算法内核 (软著核心专利点)
│   │   ├── __init__.py
│   │   ├── preprocess.py         # 光谱平滑与极值提取算法
│   │   ├── optical_constants.py  # 材料色散模型 (Sellmeier / Drude-Lorentz)
│   │   └── models.py             # 双/多光束厚度反演核心数学模型
│   └── backend/                  # 🔌 API 接口与业务逻辑层
│       ├── exceptions.py         # 自定义异常处理类
│       └── api/                  # 路由控制器
│           ├── data.py           # 处理数据上传与解析 API
│           └── calculation.py    # 处理核心厚度反演 API
│
├── requirements.txt              # 后端依赖


3. 🚀 团队分工与当前缺失功能 (TODO List)

当前核心框架已经搭建完毕，核心数学模型（多光束差分进化算法等）已注入后端。为了打通全流程并冲击 3000 行代码，团队可继续完成以下填空与扩展：

👨‍💻 开发者 A：后端功能扩展与增强 (主攻 src/si/)

多光束自动判定逻辑： 在 algorithms/models.py 中，将原 判定模型硅.py 中的 4 项指标（振荡对比度、精细度、相干长度等）封装进 detect_interference_level 函数。

自动化 PDF 测量报告生成 (软著扩展点 1)： 在 backend/ 下新增 report_generator.py，使用 reportlab 库，接收计算结果生成带有图表、实验参数表格的正规工业级 PDF 报告。

数据库接入 (软著扩展点 2)： 引入 SQLite 或 PostgreSQL，使用 SQLAlchemy 将每一次的拟合结果（时间、厚度、R²）持久化存储。

👨‍💻 开发者 B：前端交互细化与组件拆分 (主攻 frontend/)

高级表单校验： 在 App.vue 的表单中，利用 Element Plus 的表单校验规则，限制“入射角”必须在 $0 \sim 90$ 度之间，“初估厚度”大于 0 等。

计算历史记录侧边栏： 开发一个 HistoryList.vue 组件，展示历史拟合记录，丰富系统完整度。

加载动画优化： 多光束差分进化算法耗时约 3~10 秒，需在前端引入高逼格的骨架屏或 Loading 蒙层。

4. 软著代码文档提取指南

由于采用了前后端分离，最终提交的 60页连续代码文档，建议按照以下顺序拼接：

前端交互与图表引擎：frontend/src/App.vue (包含大量 ECharts 配置项代码)。

后端路由控制器：src/si/main.py -> src/si/backend/api/calculation.py。

后端核心算法引擎：src/si/algorithms/models.py -> optical_constants.py (这部分含有密集的物理数学公式，是体现独创性的核心)。
(注意：复制到 Word 时，请删除空行，确保每页有效代码至少 50 行)