import io
from typing import List, Optional, Dict, Any

import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from si.algorithms.models import InterferenceModels
from si.algorithms.preprocess import SpectrumPreprocessor
from si.algorithms.advanced_stats import StatisticalAnalyzer

router = APIRouter(prefix="/api", tags=["calculation"])


class CalculateRequest(BaseModel):
    wavelength: List[float] = Field(..., min_length=10, max_length=10000)
    reflectance: List[float] = Field(..., min_length=10, max_length=10000)
    material: str = Field(default="SIC")
    theta_deg: float = Field(default=10.0, ge=0, le=89)


class ExportRequest(BaseModel):
    result: Dict[str, Any]
    wavelength: Optional[List[float]] = None
    reflectance: Optional[List[float]] = None
    ref_fit: Optional[List[float]] = None


@router.post("/calculate")
def calculate_thickness(req: CalculateRequest):
    import pandas as pd
    from si.algorithms.optical_constants import OpticalConstants

    mat = str(req.material).strip().upper()
    if mat not in OpticalConstants._material_params:
        return {"success": False, "error": f"不支持的材料: {req.material}"}

    if len(req.wavelength) != len(req.reflectance):
        return {
            "success": False,
            "error": f"波长和反射率长度不一致: {len(req.wavelength)} vs {len(req.reflectance)}",
        }

    wl_arr = np.array(req.wavelength, dtype=np.float64)
    ref_arr = np.array(req.reflectance, dtype=np.float64)

    if np.any(np.isnan(wl_arr)) or np.any(np.isnan(ref_arr)):
        return {"success": False, "error": "数据包含 NaN 值"}
    if np.any(np.isinf(wl_arr)) or np.any(np.isinf(ref_arr)):
        return {"success": False, "error": "数据包含 Inf 值"}

    if wl_arr.max() - wl_arr.min() < 0.1:
        return {"success": False, "error": f"波长范围过小 ({wl_arr.max() - wl_arr.min():.3f} μm)"}

    if len(wl_arr) > 3000:
        step = max(1, len(wl_arr) // 2000)
        wl_arr = wl_arr[::step]
        ref_arr = ref_arr[::step]

    df = pd.DataFrame({"wavelength": wl_arr, "reflectance": ref_arr})
    sg_win = SpectrumPreprocessor.suggest_smooth_window(wl_arr, ref_arr)
    df = SpectrumPreprocessor.smooth_filter(df, method="sg", window=sg_win)
    extrema = SpectrumPreprocessor.find_extremum(df, col_name="ref_smooth", prominence=0.001)

    num_peaks = len(extrema["peaks_x"])
    num_valleys = len(extrema["valleys_x"])
    if num_peaks + num_valleys < 2:
        smooth_range = df["ref_smooth"].max() - df["ref_smooth"].min()
        return {
            "success": False,
            "error": f"极值点不足 (峰:{num_peaks}, 谷:{num_valleys})，平滑范围:{smooth_range:.4f}",
        }

    wl_vals = df["wavelength"].values
    ref_vals = df["ref_smooth"].values

    inv = InterferenceModels.run_inversion(
        wl_vals,
        ref_vals,
        extrema["peaks_x"],
        extrema["valleys_x"],
        mat,
        float(req.theta_deg),
    )

    fit_internal = inv.pop("_fit_internal", {})
    ref_fit = inv["ref_fit"]
    if hasattr(ref_fit, "tolist"):
        ref_fit = ref_fit.tolist()

    thickness_ci = None
    snr_db = None
    if fit_internal.get("jacobian") is not None and fit_internal.get("residuals") is not None:
        ci = StatisticalAnalyzer.calculate_confidence_intervals(
            fit_internal["residuals"],
            fit_internal["jacobian"],
        )
        if len(ci) > 0:
            thickness_ci = round(float(ci[0]), 4)
        noise = fit_internal["residuals"]
        snr_db = round(
            StatisticalAnalyzer.calculate_snr(ref_vals, noise),
            2,
        )

    return {
        "success": True,
        "result": {
            "init_thickness_um": inv["init_thickness_um"],
            "extrema_init_um": inv["extrema_init_um"],
            "fft_thickness_um": inv["fft_thickness_um"],
            "multi_beam_level": inv["multi_beam_level"],
            "fit_model": inv["fit_model"],
            "optimizer": inv["optimizer"],
            "metrics": inv["metrics"],
            "thickness_um": inv["thickness_um"],
            "thickness_ci": thickness_ci,
            "snr_db": snr_db,
            "r_squared": inv["r_squared"],
            "cost": inv["cost"],
            "ref_fit": ref_fit,
            "wavelength": wl_vals.tolist(),
            "reflectance": ref_vals.tolist(),
        },
    }


@router.post("/export")
def export_results(req: ExportRequest):
    try:
        import pandas as pd

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            summary_data = {
                "参数": [
                    "拟合厚度(μm)",
                    "拟合优度 R²",
                    "初估厚度(μm)",
                    "FFT厚度(μm)",
                    "多光束判定",
                    "拟合模型",
                ],
                "数值": [
                    req.result.get("thickness_um", ""),
                    req.result.get("r_squared", ""),
                    req.result.get("init_thickness_um", ""),
                    req.result.get("fft_thickness_um", ""),
                    req.result.get("multi_beam_level", ""),
                    req.result.get("fit_model", ""),
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
