# -*- coding: utf-8 -*-
import io
from typing import List, Optional, Dict, Any

import numpy as np
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from si.algorithms.models import InterferenceModels
from si.algorithms.preprocess import SpectrumPreprocessor

router = APIRouter(prefix="/api", tags=["calculation"])


class CalculateRequest(BaseModel):
    wavelength: List[float]
    reflectance: List[float]
    material: str = "SiC"
    theta_deg: float = 10.0


class ExportRequest(BaseModel):
    result: Dict[str, Any]
    wavelength: Optional[List[float]] = None
    reflectance: Optional[List[float]] = None
    ref_fit: Optional[List[float]] = None


@router.post("/calculate")
def calculate_thickness(req: CalculateRequest):
    """执行厚度反演计算"""
    try:
        import pandas as pd

        df_wl = pd.Series(req.wavelength)
        df_ref = pd.Series(req.reflectance)

        df = pd.DataFrame({"wavelength": df_wl, "reflectance": df_ref})
        df = SpectrumPreprocessor.smooth_filter(df, method="sg", window=15)
        extrema = SpectrumPreprocessor.find_extremum(df, col_name="ref_smooth")

        init_d = InterferenceModels.init_thickness_estimate(
            extrema["peaks_x"], extrema["valleys_x"], req.material, req.theta_deg
        )

        multi_beam_level = InterferenceModels.detect_multi_beam(df["ref_smooth"].values)

        wl_vals = df["wavelength"].values
        ref_vals = df["ref_smooth"].values
        res = InterferenceModels.optimize_thickness(
            wl_vals, ref_vals, init_d, req.material, req.theta_deg
        )

        ref_fit = InterferenceModels.two_beam_reflectance(
            wl_vals, res["thickness_um"], req.material, req.theta_deg
        )

        return {
            "success": True,
            "result": {
                "init_thickness_um": round(float(init_d), 4),
                "multi_beam_level": multi_beam_level,
                "thickness_um": round(float(res["thickness_um"]), 4),
                "r_squared": round(float(res["r_squared"]), 4),
                "cost": round(float(res["cost"]), 6),
                "ref_fit": ref_fit.tolist(),
                "wavelength": wl_vals.tolist(),
                "reflectance": ref_vals.tolist(),
            },
        }
    except Exception as e:
        return {"success": False, "error": f"计算失败: {str(e)}"}


@router.post("/export")
def export_results(req: ExportRequest):
    """导出计算结果为 Excel"""
    try:
        import pandas as pd

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            summary_data = {
                "参数": ["拟合厚度(μm)", "拟合优度 R²", "初估厚度(μm)", "多光束判定"],
                "数值": [
                    req.result.get("thickness_um", ""),
                    req.result.get("r_squared", ""),
                    req.result.get("init_thickness_um", ""),
                    req.result.get("multi_beam_level", ""),
                ],
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name="结果摘要", index=False)

            if req.wavelength and req.reflectance and req.ref_fit:
                detail_data = {
                    "波长(μm)": req.wavelength,
                    "实测反射率": req.reflectance,
                    "拟合反射率": req.ref_fit,
                    "残差": [exp - fit for exp, fit in zip(req.reflectance, req.ref_fit)],
                }
                pd.DataFrame(detail_data).to_excel(writer, sheet_name="拟合详情", index=False)

        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=thickness_result.xlsx"},
        )
    except Exception as e:
        return {"success": False, "error": f"导出失败: {str(e)}"}
