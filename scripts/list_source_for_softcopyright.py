# -*- coding: utf-8 -*-
"""
软著源代码提取清单：按《计算机软件著作权登记办法》建议顺序输出文件行数。
鉴别材料要求：源程序前后各连续 30 页，每页不少于 50 行有效代码；不足 60 页则交全部。
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from si.backend.config import SOFTWARE_FULL_NAME, APP_VERSION

# 前 30 页优先：入口 + 界面 + 核心 API + 算法
SOURCE_ORDER = [
    "src/si/main.py",
    "frontend/src/main.js",
    "frontend/src/App.vue",
    "frontend/src/components/DataImport.vue",
    "frontend/src/components/PreprocessPanel.vue",
    "frontend/src/components/CalculationPanel.vue",
    "frontend/src/components/SpectrumChart.vue",
    "frontend/src/components/ResultsLog.vue",
    "frontend/src/components/DatabasePanel.vue",
    "src/si/backend/api/calculation.py",
    "src/si/backend/api/preprocess.py",
    "src/si/backend/api/records.py",
    "src/si/backend/api/data.py",
    "src/si/algorithms/models.py",
    "src/si/algorithms/optical_constants.py",
    "src/si/algorithms/preprocess.py",
    "src/si/algorithms/advanced_preprocess.py",
    "src/si/algorithms/advanced_stats.py",
    "src/si/utils/pdf_generator.py",
    "src/si/backend/models.py",
    "src/si/backend/database.py",
]


def count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0


def main():
    print(f"软件名称: {SOFTWARE_FULL_NAME} V{APP_VERSION}")
    print("-" * 60)
    total = 0
    for rel in SOURCE_ORDER:
        p = ROOT / rel.replace("/", "\\") if "\\" in str(ROOT) else ROOT / rel
        n = count_lines(p)
        total += n
        print(f"{n:5d}  {rel}")
    print("-" * 60)
    print(f"合计约 {total} 行（复制到 Word 时删除多余空行，保证每页≥50行有效代码）")
    print("注释建议：模块头 1～3 行中文说明即可，单函数一行注释，注释占比宜低于 30%。")


if __name__ == "__main__":
    main()
