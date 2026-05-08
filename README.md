基于多光束干涉校正的半导体外延层厚度光谱反演软件 V1.0

1. 项目简介

本项目旨在将数模比赛中针对 Si/SiC 半导体外延层厚度测量的算法（双光束干涉模型、多光束干涉 Airly 模型、Sellmeier 色散模型等）重构为一款具备完整图形界面（GUI）的正规软件。
主要目的： 用于申请中国计算机软件著作权，并提供直观的可视化分析工具。

2. 目录结构与当前状态

项目采用了标准的 MVC/三层架构思想，当前目录结构及文件分工如下：

Si/
├── main.py                # 【已完成】程序唯一主入口，负责环境初始化与页面调度。
├── requirements.txt       # 【已完成】项目依赖包列表。
├── sample_data.csv        # 【已完成】用于开发测试的模拟光谱数据。
├── README.md              # 【已完成】本协作说明书。
├── core/                  # 🌟 核心算法层 (软著独创性核心，需要重点开发)
│   ├── __init__.py
│   ├── preprocess.py      # 【已完成基础】光谱平滑与极值提取。
│   ├── optical_constants.py # 【需完善】材料折射率/介电常数计算。
│   └── models.py          # 【需完善】当前仅含基础双光束模型，多光束差分进化算法待移入。
├── ui/                    # 🖥️ GUI交互层
│   ├── __init__.py
│   └── main_window.py     # 【已完成基础】Tkinter主界面、按钮交互、绘图区。
└── utils/                 # 🛠️ 通用工具层
    ├── __init__.py
    ├── data_io.py         # 【已完成】txt/csv/xlsx 格式数据读取校验。
    └── visualization.py   # 【已完成】Matplotlib 绘图并嵌入 Tkinter 界面。


3. 快速启动与测试指南

配置环境： 在当前目录打开终端（PowerShell / CMD），运行：
pip install -r requirements.txt

运行软件：
在终端运行：
python main.py

功能测试流程：
界面启动后 -> 点击 选择光谱文件 导入 sample_data.csv -> 点击 执行平滑与极值提取 -> 点击 执行厚度拟合与反演，观察右侧图像和左侧日志输出。

4. 🚀 团队协作分工与 TODO List

目前软件框架已经搭好，界面和数据流已彻底打通，但内核的物理模型目前是简化版。为了达到论文的精度并顺利申请软著，需要队友将我们原先在 Jupyter/Python 脚本里的完整代码“填空”到对应的模块中。

📌 任务一：完善光学常数计算（负责同学 A）

目标文件： core/optical_constants.py

需要做什么： * 将论文中硅（Si）的 Sellmeier 经验公式（原代码 si多光束干涉.py 中的 n_sm 函数）完整移植到该文件中。

将碳化硅（SiC）的 Drude-Lorentz 模型参数计算公式补充完整。

对接说明： 保证 calc_refractive_index(wavelength_um, material) 方法能根据传入的材料正确返回对应的折射率数组。

📌 任务二：接入多光束干涉与差分进化算法（负责同学 B）

目标文件： core/models.py

需要做什么： * 目前 models.py 里的 two_beam_reflectance 只是简化版。你需要把论文里的 Airy 多光束干涉反射率模型 加进来。

将 si多光束干涉.py 中的 差分进化算法 (differential_evolution) 求解逻辑封装成一个方法，例如 optimize_multi_beam(...)。

完善 detect_multi_beam (干涉等级判定)：把 判定模型硅.py 中的振荡对比度、精细度等 4 项指标判定逻辑迁移过来。

对接说明： 算法封装好后，同伴 C 可以在 UI 界面上加一个“多光束校正”按钮直接调用。

📌 任务三：丰富 UI 界面与报告导出（负责同学 C）

目标文件： ui/main_window.py 及 utils/report_gen.py (需新建)

需要做什么：

在 UI 界面上增加一个 Checkbox（复选框），让用户选择“是否启用多光束校正”。

新建 utils/report_gen.py：开发一键导出报告功能。可以利用 pandas 将计算的残差数据导出为 .xlsx，或者利用 reportlab/python-docx 将当前厚度结果和图片导出为 PDF/Word（这部分对于软著非常有加分）。

5. 代码提交规范 (给队友的提示)

不要破坏现有接口： main_window.py 依赖 core 和 utils 里的方法。你在 core 里修改算法时，输入参数和返回值的格式请尽量保持和现在一致（比如返回字典格式 {'thickness_um': 10.5, 'r_squared': 0.99}），这样 UI 层就不会报错。

注重注释： 软著申请需要提交代码，代码里必须要有中文注释解释你的公式和逻辑。