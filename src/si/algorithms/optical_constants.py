# -*- coding: utf-8 -*-
import numpy as np

class OpticalConstants:
    """材料光学常数计算模块"""
    
    @staticmethod
    def calc_refractive_index(wavelength_um, material='SiC'):
        """
        计算折射率
        支持硅(Si)和碳化硅(SiC)的Sellmeier/经验公式
        """
        lambda_sq = np.asarray(wavelength_um)**2
        
        if material == 'SiC':
            # 基于论文中的SiC基底折射率公式
            n_sq = 4.148 + (2.378 * lambda_sq) / (lambda_sq - 0.0388)
            n = np.sqrt(n_sq)
        elif material == 'Si':
            # 基于论文代码中硅的公式
            n_sq = 1 + (10.668 * lambda_sq) / (lambda_sq - 0.301) + \
                   (0.003 * lambda_sq) / (lambda_sq - 1.134) + \
                   (1.541 * lambda_sq) / (lambda_sq - 1104)
            n = np.sqrt(n_sq)
        else:
            n = np.ones_like(wavelength_um) * 1.5 # 默认值
            
        return np.real(n)

    @staticmethod
    def calc_complex_permittivity(wavenumber_cm, params):
        """
        Drude-Lorentz 复介电函数模型计算 (外延层)
        params: eps_inf, w_TO, G_TO, S_TO, w_p, G_p
        """
        eps_inf, w_TO_cm, G_TO_cm, S_TO, w_p_cm, G_p_cm = params
        w = np.asarray(wavenumber_cm)
        
        # Lorentz项 (晶格振动)
        lorentz_term = (S_TO * w_TO_cm**2) / (w_TO_cm**2 - w**2 - 1j * G_TO_cm * w)
        # Drude项 (自由载流子)
        drude_term = (w_p_cm**2) / (w**2 + 1j * G_p_cm * w)
        
        eps_complex = eps_inf + lorentz_term - drude_term
        
        n_complex = np.sqrt(eps_complex)
        return np.real(n_complex), np.imag(n_complex), eps_complex