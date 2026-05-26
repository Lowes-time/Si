# -*- coding: utf-8 -*-
"""项目路径：样例数据目录等"""

from pathlib import Path

# Si 项目根目录（src/si/utils -> 上三级）
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# 样例光谱唯一源目录；生成脚本会同步到 frontend/public/samples 供页面加载
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
FRONTEND_SAMPLES_DIR = PROJECT_ROOT / "frontend" / "public" / "samples"
