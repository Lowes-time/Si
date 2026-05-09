# -*- coding: utf-8 -*-
"""
核心算法层：双光束与多光束干涉模型
（解决 ModuleNotFoundError 报错，请务必将此代码保存在 core/ 文件夹下的 models.py 中）
"""
import numpy as np
from scipy.optimize import least_squares
from si.algorithms.optical_constants import OpticalConstants

class InterferenceModels:
    
    @staticmethod
    def init_thickness_estimate(peaks_wl, valleys_wl, material, theta_deg):
        """利用干涉极值点估算初始厚度 (线性回归思想)"""
        all_extrema = np.sort(np.concatenate([peaks_wl, valleys_wl]))[::-1]
        if len(all_extrema) < 2:
            return 10.0 # 默认初值 10 um
            
        theta_rad = np.radians(theta_deg)
        thicknesses = []
        
        for i in range(len(all_extrema)-1):
            wl1 = all_extrema[i]
            wl2 = all_extrema[i+1]
            n_avg = np.mean([OpticalConstants.calc_refractive_index(wl1, material), 
                             OpticalConstants.calc_refractive_index(wl2, material)])
            
            cos_theta_t = np.sqrt(n_avg**2 - np.sin(theta_rad)**2)
            d = (wl1 * wl2) / (4 * cos_theta_t * abs(wl1 - wl2))
            thicknesses.append(d)
            
        return np.mean(thicknesses) if thicknesses else 10.0

    @staticmethod
    def two_beam_reflectance(wl_um, thickness, material, theta_deg):
        """双光束干涉反射率正演"""
        theta_rad = np.radians(theta_deg)
        n = OpticalConstants.calc_refractive_index(wl_um, material)
        cos_theta_t = np.sqrt(n**2 - np.sin(theta_rad)**2)
        
        delta = (4 * np.pi * thickness * cos_theta_t) / wl_um
        # 简化版反射率叠加模型，含半波损失
        R = 0.5 + 0.4 * np.cos(delta + np.pi) 
        return R

    @staticmethod
    def optimize_thickness(df_wl, df_ref, init_d, material, theta_deg):
        """非线性拟合求解厚度"""
        def residual(d_guess):
            r_fit = InterferenceModels.two_beam_reflectance(df_wl, d_guess[0], material, theta_deg)
            return r_fit - df_ref
            
        res = least_squares(residual, [init_d], bounds=(1.0, 50.0))
        
        ss_res = np.sum(res.fun**2)
        ss_tot = np.sum((df_ref - np.mean(df_ref))**2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return {
            'thickness_um': res.x[0],
            'r_squared': r_squared,
            'cost': res.cost
        }

    @staticmethod
    def detect_multi_beam(df_ref):
        """多光束干涉等级判定"""
        ref_max = np.max(df_ref)
        ref_min = np.min(df_ref)
        contrast = (ref_max - ref_min) / (ref_max + ref_min + 1e-6)
        
        if contrast > 0.4:
            return "强多光束干涉"
        elif contrast > 0.15:
            return "中等多光束干涉"
        else:
            return "弱/无多光束干涉"