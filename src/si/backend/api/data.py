# -*- coding: utf-8 -*-
import os
import tempfile

import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/api", tags=["data"])


@router.post("/upload")
async def upload_spectrum_file(file: UploadFile = File(...)):
    """上传光谱文件并返回解析后的数据"""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".csv", ".txt", ".xlsx", ".xls"):
        return {"success": False, "error": f"不支持的文件格式: {ext}，仅支持 csv/txt/xlsx"}

    try:
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        if ext in (".csv", ".txt"):
            df = pd.read_csv(tmp_path, sep=None, engine="python", skiprows=1,
                             names=["wavenumber", "reflectance"])
        else:
            df = pd.read_excel(tmp_path, skiprows=1, names=["wavenumber", "reflectance"])

        os.unlink(tmp_path)

        if "wavenumber" in df.columns:
            df["wavelength"] = 10000.0 / df["wavenumber"]

        # 数据清洗
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        if df.empty:
            return {"success": False, "error": "清洗后数据为空，请检查文件内容"}

        if df["reflectance"].max() > 2.0:
            df["reflectance"] = df["reflectance"] / 100.0

        return {
            "success": True,
            "data": {
                "filename": file.filename,
                "row_count": len(df),
                "wavelength": df["wavelength"].tolist(),
                "reflectance": df["reflectance"].tolist(),
                "wl_min": round(float(df["wavelength"].min()), 4),
                "wl_max": round(float(df["wavelength"].max()), 4),
            },
        }
    except Exception as e:
        return {"success": False, "error": f"数据读取失败: {str(e)}"}
