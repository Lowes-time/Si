# -*- coding: utf-8 -*-
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from si.algorithms.preprocess import SpectrumPreprocessor

router = APIRouter(prefix="/api", tags=["preprocess"])


class PreprocessRequest(BaseModel):
    wavelength: List[float]
    reflectance: List[float]
    method: str = "sg"
    window: int = 15
    normalize: bool = False


@router.post("/preprocess")
def preprocess_spectrum(req: PreprocessRequest):
    """执行光谱预处理"""
    try:
        import pandas as pd

        df = pd.DataFrame({
            "wavelength": req.wavelength,
            "reflectance": req.reflectance,
        })

        df = SpectrumPreprocessor.smooth_filter(df, method=req.method, window=req.window)
        df = SpectrumPreprocessor.baseline_correction(df)

        if req.normalize:
            df = SpectrumPreprocessor.normalize(df, col_name="ref_smooth")

        extrema = SpectrumPreprocessor.find_extremum(df, col_name="ref_smooth")

        return {
            "success": True,
            "data": {
                "wavelength": df["wavelength"].tolist(),
                "ref_smooth": df["ref_smooth"].tolist(),
                "ref_baseline": df["ref_baseline"].tolist() if "ref_baseline" in df.columns else None,
                "ref_norm": df["ref_norm"].tolist() if "ref_norm" in df.columns else None,
                "peaks_wl": extrema["peaks_x"].tolist(),
                "peaks_ref": extrema["peaks_y"].tolist(),
                "valleys_wl": extrema["valleys_x"].tolist(),
                "valleys_ref": extrema["valleys_y"].tolist(),
            },
        }
    except Exception as e:
        return {"success": False, "error": f"预处理失败: {str(e)}"}
