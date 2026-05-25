# -*- coding: utf-8 -*-
"""材料光学常数：Sellmeier 色散与衬底折射率"""

import numpy as np
from typing import Dict, Tuple, Optional


class OpticalConstants:
    """Sellmeier 色散与衬底折射率"""
    
    # 材料折射率计算参数 (Sellmeier系数)
    _material_params: Dict[str, Dict] = {
        'SIC': {
            'name': '碳化硅 (4H-SiC)',
            'formula': 'SiC',
            'desc': '功率器件/射频',
            'A': 4.148,
            'B': 2.378,
            'lambda_sq': 0.0388,
            'temp_coef': 8e-5,
            'bandgap': 3.26,
            'n_substrate_scale': 1.015,
        },
        'SI': {
            'name': '硅 (Si)',
            'formula': 'Si',
            'desc': 'IC衬底/太阳能',
            'A': 3.41983,
            'B1': 0.159906,
            'B2': -0.123109,
            'B3': 1.26878e-6,
            'B4': -1.95104e-9,
            'lambda_base': 0.028,
            'temp_coef': 1.5e-4,
            'bandgap': 1.12,
            'n_substrate_scale': 1.008,
        },
        'GAN': {
            'name': '氮化镓 (GaN)',
            'formula': 'GaN',
            'desc': '蓝光LED/功率',
            'A': 2.275,
            'B': 3.057,
            'lambda_sq': 0.088**2,
            'temp_coef': 2.5e-4,
            'bandgap': 3.39,
            'n_substrate_scale': 1.012,
        },
        'ALN': {
            'name': '氮化铝 (AlN)',
            'formula': 'AlN',
            'desc': 'UVC LED/压电',
            'A': 1.0,
            'B1': 2.0768,
            'B2': 3.8260,
            'lambda1_sq': 0.1176**2,
            'lambda2_sq': 7.8925**2,
            'temp_coef': 1.8e-4,
            'bandgap': 6.2,
            'n_substrate_scale': 1.01,
        },
        'INP': {
            'name': '磷化铟 (InP)',
            'formula': 'InP',
            'desc': '光通信/激光',
            'A': 1.0,
            'B1': 7.2669,
            'B2': 0.22873,
            'lambda1_sq': 0.38954**2,
            'lambda2_sq': 31.130**2,
            'temp_coef': 3.2e-4,
            'bandgap': 1.35,
            'n_substrate_scale': 1.01,
        },
        'GAAS': {
            'name': '砷化镓 (GaAs)',
            'formula': 'GaAs',
            'desc': '射频/激光',
            'A': 1.0,
            'B1': 5.3724,
            'B2': 0.2127,
            'B3': 4.0597,
            'lambda1_sq': 0.443**2,
            'lambda2_sq': 0.874**2,
            'lambda3_sq': 36.916**2,
            'temp_coef': 2.8e-4,
            'bandgap': 1.42,
            'n_substrate_scale': 1.012,
        },
        'ZNO': {
            'name': '氧化锌 (ZnO)',
            'formula': 'ZnO',
            'desc': 'UV/压电',
            'A': 1.0,
            'B1': 1.9887,
            'B2': 2.3468,
            'lambda1_sq': 0.075**2,
            'lambda2_sq': 7.385**2,
            'temp_coef': 1.5e-4,
            'bandgap': 3.37,
            'n_substrate_scale': 1.008,
        },
        'C': {
            'name': '金刚石 (C)',
            'formula': 'C',
            'desc': '高功率/辐射探测',
            'A': 1.0,
            'B1': 0.3306,
            'B2': 4.0688,
            'lambda1': 0.175,
            'temp_coef': 0,
            'bandgap': 5.47,
            'n_substrate_scale': 1.01,
        },
        'GE': {
            'name': '锗 (Ge)',
            'formula': 'Ge',
            'desc': '红外光学/探测器',
            'A': 1.0,
            'B1': 6.728,
            'B2': 0.213,
            'lambda1_sq': 0.408**2,
            'temp_coef': 2.0e-4,
            'bandgap': 0.67,
            'n_substrate_scale': 1.012,
        },
        'GASB': {
            'name': '砷化镓锑 (GaSb)',
            'formula': 'GaSb',
            'desc': '红外探测器/激光',
            'A': 1.0,
            'B1': 8.881,
            'B2': 0.213,
            'lambda1_sq': 0.443**2,
            'temp_coef': 2.5e-4,
            'bandgap': 0.73,
            'n_substrate_scale': 1.01,
        },
        'INAS': {
            'name': '砷化铟 (InAs)',
            'formula': 'InAs',
            'desc': '中红外/高速器件',
            'A': 1.0,
            'B1': 8.350,
            'B2': 0.169,
            'lambda1_sq': 0.443**2,
            'temp_coef': 3.0e-4,
            'bandgap': 0.36,
            'n_substrate_scale': 1.01,
        },
        'SIO2': {
            'name': '二氧化硅 (SiO2)',
            'formula': 'SiO2',
            'desc': '栅氧/钝化层',
            'A': 1.0,
            'B1': 0.6961663,
            'B2': 0.4079426,
            'B3': 0.8974794,
            'lambda1_sq': 0.0684043**2,
            'lambda2_sq': 0.1162414**2,
            'lambda3_sq': 9.896161**2,
            'temp_coef': 0,
            'bandgap': 9.0,
            'n_substrate_scale': 1.005,
        },
        'SI3N4': {
            'name': '氮化硅 (Si3N4)',
            'formula': 'Si3N4',
            'desc': '应力缓冲/钝化',
            'A': 1.0,
            'B1': 2.893,
            'B2': 0.137,
            'lambda1_sq': 0.139**2,
            'temp_coef': 0,
            'bandgap': 5.0,
            'n_substrate_scale': 1.008,
        },
    }
    
    @staticmethod
    def calc_refractive_index(wavelength_um, material='SIC'):
        wavelength = np.asarray(wavelength_um)
        material = str(material).strip().upper()
        
        if material not in OpticalConstants._material_params:
            material = 'SIC'
        
        params = OpticalConstants._material_params[material]
        
        if material == 'SIC':
            # SiC: 基于论文中的折射率公式
            lambda_sq = wavelength ** 2
            denominator = lambda_sq - params['lambda_sq']
            denominator = np.where(np.abs(denominator) < 1e-5, 1e-5, denominator)
            n_sq = params['A'] + (params['B'] * lambda_sq) / denominator
            
        elif material == 'SI':
            # Si: Sellmeier公式
            ls = wavelength ** 2
            dn = ls - params['lambda_base']
            n_sq = params['A'] + params['B1']/dn + params['B2']/(dn**2) + params['B3']*ls + params['B4']*(ls**2)
            
        elif material == 'GAN':
            # GaN: 改进Sellmeier方程
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + (params['B'] * lambda_sq) / (lambda_sq - params['lambda_sq'])
            
        elif material == 'ALN':
            # AlN: 双振子模型
            lambda_um = wavelength
            n_sq = params['A'] + params['B1']*lambda_um**2/(lambda_um**2 - params['lambda1_sq']) \
                   + params['B2']*lambda_um**2/(lambda_um**2 - params['lambda2_sq'])
            
        elif material == 'INP':
            # InP: Cameron模型
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda2_sq'])
            
        elif material == 'GAAS':
            # GaAs: Skaifi模型
            lambda_um = wavelength
            n_sq = params['A'] + params['B1']*lambda_um**2/(lambda_um**2 - params['lambda1_sq']) \
                   + params['B2']*lambda_um**2/(lambda_um**2 - params['lambda2_sq']) \
                   + params['B3']*lambda_um**2/(lambda_um**2 - params['lambda3_sq'])
            
        elif material == 'ZNO':
            # ZnO: Sellmeier方程
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda2_sq'])
            
        elif material == 'C':
            lambda_um = wavelength
            n_sq = params['A'] + params['B1']*lambda_um**2/(lambda_um**2 - params['lambda1']**2) \
                   + params['B2']*lambda_um**2/(lambda_um**2 - params['lambda1']**2)**2

        elif material == 'GE':
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda1_sq'])

        elif material == 'GASB':
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda1_sq'])

        elif material == 'INAS':
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda1_sq'])

        elif material == 'SIO2':
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq']) \
                   + params['B2']*lambda_sq/(lambda_sq - params['lambda2_sq']) \
                   + params['B3']*lambda_sq/(lambda_sq - params['lambda3_sq'])

        elif material == 'SI3N4':
            lambda_sq = wavelength ** 2
            n_sq = params['A'] + params['B1']*lambda_sq/(lambda_sq - params['lambda1_sq'])
            
        else:
            n_sq = np.ones_like(wavelength) * 2.5
        
        n = np.sqrt(np.maximum(1.0, n_sq))
        
        # 添加温度修正
        if 'temp_coef' in params and params['temp_coef'] > 0:
            n = n + params['temp_coef'] * 0
        
        return np.real(n)
    
    @staticmethod
    def calc_substrate_index(wavelength_um, material='SIC'):
        """衬底折射率（外延层折射率乘以材料相关缩放系数）"""
        n_epi = OpticalConstants.calc_refractive_index(wavelength_um, material)
        mat = str(material).strip().upper()
        params = OpticalConstants._material_params.get(mat, OpticalConstants._material_params['SIC'])
        scale = params.get('n_substrate_scale', 1.01)
        return n_epi * scale
    
    @staticmethod
    def calc_complex_permittivity(wavenumber_cm, params):
        """
        Drude-Lorentz 复介电函数模型计算 (外延层)
        
        Args:
            wavenumber_cm: 波数 (cm^-1)
            params: 参数元组 (eps_inf, w_TO, G_TO, S_TO, w_p, G_p)
                - eps_inf: 高频介电常数
                - w_TO: TO声子频率 (cm^-1)
                - G_TO: TO阻尼 (cm^-1)
                - S_TO: TO振子强度
                - w_p: 等离子体频率 (cm^-1)
                - G_p: 等离子体阻尼 (cm^-1)
        
        Returns:
            (n_real, n_imag, eps_complex): 实部、虚部、复折射率
        """
        eps_inf, w_TO_cm, G_TO_cm, S_TO, w_p_cm, G_p_cm = params
        w = np.asarray(wavenumber_cm)
        
        # Lorentz项 (晶格振动)
        lorentz_term = (S_TO * w_TO_cm**2) / (w_TO_cm**2 - w**2 - 1j * G_TO_cm * w)
        
        # Drude项 (自由载流子)
        drude_term = (w_p_cm**2) / (w**2 + 1j * G_p_cm * w)
        
        # 总介电函数
        eps_complex = eps_inf + lorentz_term - drude_term
        
        # 折射率
        n_complex = np.sqrt(eps_complex)
        
        return np.real(n_complex), np.imag(n_complex), eps_complex
    
    @staticmethod
    def get_material_info(material: str) -> Dict:
        """获取材料的基本信息"""
        material = str(material).strip().upper()
        
        if material in OpticalConstants._material_params:
            params = OpticalConstants._material_params[material]
            return {
                'name': params.get('name', material),
                'bandgap_ev': params.get('bandgap', 0),
                'temp_coef': params.get('temp_coef', 0)
            }
        
        return {'name': '未知材料', 'bandgap_ev': 0, 'temp_coef': 0}
    
    @staticmethod
    def list_supported_materials() -> list:
        """列出所有支持的材料"""
        seen = set()
        materials = []
        for key, params in OpticalConstants._material_params.items():
            if key in seen:
                continue
            seen.add(key)
            materials.append({
                'key': key,
                'name': params.get('name', key),
                'formula': params.get('formula', key),
                'desc': params.get('desc', ''),
                'bandgap_ev': params.get('bandgap', 0),
            })
        return materials