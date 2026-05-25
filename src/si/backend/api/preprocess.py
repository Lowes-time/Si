# -*- coding: utf-8 -*-
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from si.algorithms.preprocess import SpectrumPreprocessor
from si.algorithms.advanced_preprocess import AdvancedPreprocessor

router = APIRouter(prefix="/api", tags=["preprocess"])


class PreprocessRequest(BaseModel):
    wavelength: List[float]
    reflectance: List[float]
    material: str = "SIC"
    method: str = "sg"
    window: int = 0
    normalize: bool = False
    use_als: bool = False
    mask_reststrahlen: bool = False


@router.post("/preprocess")
def preprocess_spectrum(req: PreprocessRequest):
    try:
        import pandas as pd

        df = pd.DataFrame({
            "wavelength": req.wavelength,
            "reflectance": req.reflectance,
        })

        if req.mask_reststrahlen:
            df = AdvancedPreprocessor.mask_reststrahlen_band(df, req.material)

        win = req.window
        if win <= 0:
            win = SpectrumPreprocessor.suggest_smooth_window(
                df["wavelength"].values, df["reflectance"].values
            )

        df = SpectrumPreprocessor.smooth_filter(df, method=req.method, window=win)

        if req.use_als:
            baseline = AdvancedPreprocessor.asymmetric_least_squares_baseline(
                df["reflectance"].values.astype(float)
            )
            df["ref_smooth"] = df["reflectance"].values - baseline + baseline.min()

        df = SpectrumPreprocessor.baseline_correction(df)

        if req.normalize:
            df = SpectrumPreprocessor.normalize(df, col_name="ref_smooth")

        extrema = SpectrumPreprocessor.find_extremum(df, col_name="ref_smooth")

        return {
            "success": True,
            "used_window": win,
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
