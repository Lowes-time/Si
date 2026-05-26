# -*- coding: utf-8 -*-
"""CSV 光谱文件读取：波数列转波长(μm)"""

import csv
from pathlib import Path
from typing import List, Tuple, Union


def load_wavenumber_csv(path: Union[str, Path]) -> Tuple[List[float], List[float]]:
    """
    读取 wavenumber,reflectance 格式 CSV。
    反射率若大于 2 视为百分数并除以 100。
    """
    wl_um: List[float] = []
    ref: List[float] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            wn = float(row[0])
            rv = float(row[1])
            if rv > 2:
                rv /= 100.0
            wl_um.append(10000.0 / wn)
            ref.append(rv)
    return wl_um, ref
