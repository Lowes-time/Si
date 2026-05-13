# -*- coding: utf-8 -*-
# 软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0

import numpy as np
import pandas as pd

class AdvancedPreprocessor:
    """工业级高级光谱异常处理引擎"""

    @staticmethod
    def asymmetric_least_squares_baseline(y: np.ndarray, lam: float = 1e5, p: float = 0.01, n_iter: int = 10) -> np.ndarray:
        """
        非对称最小二乘法 (ALS) 复杂光谱基线校正
        用于消除半导体载流子吸收引起的漫反射基线漂移。
        Args:
            y: 原始反射率信号
            lam: 平滑度权重惩罚参数
            p: 非对称惩罚系数
        """
        try:
            from scipy import sparse
            from scipy.sparse.linalg import spsolve
            
            L = len(y)
            D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
            D = lam * D.dot(D.transpose())
            w = np.ones(L)
            
            for i in range(n_iter):
                W = sparse.spdiags(w, 0, L, L)
                Z = W + D
                # 求解稀疏线性方程组找到拟合基线
                z = spsolve(Z, w * y)
                # 根据当前残差动态更新权重
                w = p * (y > z) + (1 - p) * (y < z)
            return z
        except ImportError:
            # 回退机制
            return np.ones_like(y) * np.min(y)

    @staticmethod
    def mask_reststrahlen_band(df: pd.DataFrame, material: str = 'SiC') -> pd.DataFrame:
        """
        Reststrahlen 剩余射线高反射畸变带自动剔除算法
        根据声子共振频率自动切除无效干涉波段
        """
        df_clean = df.copy()
        
        # 碳化硅(SiC)的剩余射线带通常位于 10 μm - 12.5 μm (即 800 - 1000 cm^-1)
        if material.upper() == 'SIC':
            mask = (df_clean['wavelength'] >= 10.0) & (df_clean['wavelength'] <= 12.5)
            # 将该波段的反射率设为 NaN 以剔除
            df_clean.loc[mask, 'reflectance'] = np.nan
            
        # 单晶硅无强红外声子吸收带，无需遮罩
        
        return df_clean.dropna(subset=['reflectance']).reset_index(drop=True)