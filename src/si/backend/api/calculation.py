# -*- coding: utf-8 -*-
import io
from typing import List, Optional, Dict, Any

import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from si.algorithms.models import InterferenceModels
from si.algorithms.preprocess import SpectrumPreprocessor

router = APIRouter(prefix="/api", tags=["calculation"])


class CalculateRequest(BaseModel):
    """计算请求模型"""
    wavelength: List[float] = Field(..., min_length=10, max_length=10000)
    reflectance: List[float] = Field(..., min_length=10, max_length=10000)
    material: str = Field(default="SiC", pattern="^(SIC|SI|GAN|ALN|INP|GAAS|ZNO|C)$")
    theta_deg: float = Field(default=10.0, ge=0, le=89)


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

        # 数据长度一致性验证
        if len(req.wavelength) != len(req.reflectance):
            return {"success": False, "error": f"波长和反射率数据长度不一致: {len(req.wavelength)} vs {len(req.reflectance)}"}

        wl_arr = np.array(req.wavelength, dtype=np.float64)
        ref_arr = np.array(req.reflectance, dtype=np.float64)

        # 检查是否有 NaN 或 Inf
        if np.any(np.isnan(wl_arr)) or np.any(np.isnan(ref_arr)):
            return {"success": False, "error": "数据包含 NaN 值"}
        
        if np.any(np.isinf(wl_arr)) or np.any(np.isinf(ref_arr)):
            return {"success": False, "error": "数据包含 Inf 值"}

        # 检查波长范围
        wl_min, wl_max = wl_arr.min(), wl_arr.max()
        if wl_max - wl_min < 0.1:
            return {"success": False, "error": f"波长范围太小 ({wl_max - wl_min:.3f} μm)，至少需要 0.1 μm"}

        # 自动降采样处理大数据
        if len(wl_arr) > 3000:
            step = max(1, len(wl_arr) // 2000)
            wl_arr = wl_arr[::step]
            ref_arr = ref_arr[::step]

        df = pd.DataFrame({"wavelength": wl_arr, "reflectance": ref_arr})
        df = SpectrumPreprocessor.smooth_filter(df, method="sg", window=15)
        
        # 检测极值点，使用自适应低prominence
        extrema = SpectrumPreprocessor.find_extremum(df, col_name="ref_smooth", prominence=0.001)

        # 验证极值点数量
        num_peaks = len(extrema["peaks_x"])
        num_valleys = len(extrema["valleys_x"])
        
        if num_peaks + num_valleys < 2:
            # 返回详细调试信息
            smooth_range = df['ref_smooth'].max() - df['ref_smooth'].min()
            return {
                "success": False, 
                "error": f"无法检测到足够的极值点 (波峰:{num_peaks}, 波谷:{num_valleys})，数据范围:{smooth_range:.4f}，建议检查数据质量或调整波长范围",
                "debug": {
                    "wl_range": f"{wl_arr.min():.3f}-{wl_arr.max():.3f}",
                    "ref_range": f"{ref_arr.min():.3f}-{ref_arr.max():.3f}",
                    "smooth_range": f"{smooth_range:.4f}",
                    "peaks": num_peaks,
                    "valleys": num_valleys
                }
            }

        init_d = InterferenceModels.init_thickness_estimate(
            extrema["peaks_x"].tolist(), 
            extrema["valleys_x"].tolist(), 
            req.material, 
            float(req.theta_deg)
        )

        multi_beam_level = InterferenceModels.detect_multi_beam(df["ref_smooth"].values)

        wl_vals = df["wavelength"].values
        ref_vals = df["ref_smooth"].values
        res = InterferenceModels.optimize_thickness(
            wl_vals, ref_vals, init_d, req.material, float(req.theta_deg)
        )

        ref_fit = InterferenceModels.two_beam_reflectance(
            wl_vals, res["thickness_um"], req.material, float(req.theta_deg)
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