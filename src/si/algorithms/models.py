# -*- coding: utf-8 -*-
"""
核心算法层：双光束与多光束干涉模型
"""
import numpy as np
from scipy.optimize import least_squares, minimize
from si.algorithms.optical_constants import OpticalConstants

class InterferenceModels:
    
    @staticmethod
    def init_thickness_estimate(peaks_wl, valleys_wl, material, theta_deg):
        """利用干涉极值点估算初始厚度 (线性回归思想)"""
        all_extrema = np.sort(np.concatenate([peaks_wl, valleys_wl]))[::-1]
        if len(all_extrema) < 2:
            return 10.0  # 默认初值 10 um
        
        theta_rad = np.radians(theta_deg)
        thicknesses = []
        
        for i in range(len(all_extrema)-1):
            wl1 = float(all_extrema[i])
            wl2 = float(all_extrema[i+1])
            if abs(wl1 - wl2) < 1e-6:
                continue
            
            n_avg = np.mean([
                float(OpticalConstants.calc_refractive_index(wl1, material)), 
                float(OpticalConstants.calc_refractive_index(wl2, material))
            ])
            
            sin_theta_sq = np.sin(theta_rad) ** 2
            cos_theta_t_sq = max(0, n_avg**2 - sin_theta_sq)
            cos_theta_t = np.sqrt(cos_theta_t_sq)
            
            if cos_theta_t <= 1e-6:
                continue
            d = (wl1 * wl2) / (4 * cos_theta_t * abs(wl1 - wl2))
            thicknesses.append(d)
        
        if thicknesses:
            init_d = float(np.median(thicknesses))
            # 确保初始值在合理范围内
            return max(1.5, min(45.0, init_d))
        return 10.0
    
    @staticmethod
    def two_beam_reflectance(wl_um, thickness, material, theta_deg):
        """双光束干涉反射率正演"""
        theta_rad = np.radians(theta_deg)
        
        # 处理标量或数组
        wl_arr = np.asarray(wl_um, dtype=np.float64)
        n = OpticalConstants.calc_refractive_index(wl_arr, material)
        cos_theta_t = np.sqrt(np.maximum(0, n**2 - np.sin(theta_rad)**2))
        
        delta = (4 * np.pi * thickness * cos_theta_t) / wl_arr
        # 简化版反射率叠加模型，含半波损失
        R = 0.5 + 0.4 * np.cos(delta + np.pi) 
        return R
    
    @staticmethod
    def optimize_thickness(df_wl, df_ref, init_d, material, theta_deg):
        """非线性拟合求解厚度"""
        # 确保输入是numpy数组
        wl_arr = np.asarray(df_wl, dtype=np.float64)
        ref_arr = np.asarray(df_ref, dtype=np.float64)
        
        def residual(d_guess):
            r_fit = InterferenceModels.two_beam_reflectance(wl_arr, d_guess[0], material, theta_deg)
            return r_fit - ref_arr
        
        # 确保初始值在边界内
        init_d = float(max(1.5, min(45.0, init_d)))
        
        # 使用 bounds 参数确保边界正确 (使用元组格式)
        try:
            res = least_squares(residual, [init_d], bounds=([1.5], [45.0]), method='trf')
        except Exception as e:
            # 如果失败，尝试使用 minimize
            def cost_func(d):
                r_fit = InterferenceModels.two_beam_reflectance(wl_arr, float(d[0]), material, theta_deg)
                return float(np.sum((r_fit - ref_arr)**2))
            try:
                result = minimize(cost_func, [init_d], bounds=[(1.5, 45.0)], method='L-BFGS-B')
                return {
                    'thickness_um': float(result.x[0]),
                    'r_squared': float(1 - result.fun / (np.var(ref_arr) * len(ref_arr) + 1e-10)),
                    'cost': float(result.fun)
                }
            except:
                # 最终fallback：返回初始值
                return {
                    'thickness_um': init_d,
                    'r_squared': 0.0,
                    'cost': 1.0
                }
        
        ss_res = float(np.sum(res.fun**2))
        ss_tot = float(np.sum((ref_arr - np.mean(ref_arr))**2))
        r_squared = 1 - (ss_res / (ss_tot + 1e-10))
        
        return {
            'thickness_um': float(res.x[0]),
            'r_squared': float(r_squared),
            'cost': float(res.cost)
        }
    
    @staticmethod
    def detect_multi_beam(df_ref):
        """多光束干涉等级判定"""
        ref_arr = np.asarray(df_ref)
        ref_max = float(np.max(ref_arr))
        ref_min = float(np.min(ref_arr))
        contrast = (ref_max - ref_min) / (ref_max + ref_min + 1e-6)
        
        if contrast > 0.4:
            return "强多光束干涉"
        elif contrast > 0.15:
            return "中等多光束干涉"
        else:
            return "弱/无多光束干涉"