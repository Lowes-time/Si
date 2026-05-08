# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, find_peaks

class SpectrumPreprocessor:
    """光谱数据预处理模块"""
    
    @staticmethod
    def smooth_filter(df, method='sg', window=15, polyorder=3):
        """多滤波算法"""
        df_processed = df.copy()
        if method == 'sg':
            df_processed['ref_smooth'] = savgol_filter(df['reflectance'], window_length=window, polyorder=polyorder)
        elif method == 'ma':
            df_processed['ref_smooth'] = df['reflectance'].rolling(window=window, center=True, min_periods=1).mean()
        else:
            df_processed['ref_smooth'] = df['reflectance']
        return df_processed

    @staticmethod
    def baseline_correction(df):
        """基线校正 (简化实现：扣除最小值)"""
        df_processed = df.copy()
        min_val = df_processed['ref_smooth'].min()
        df_processed['ref_baseline'] = df_processed['ref_smooth'] - min_val
        return df_processed

    @staticmethod
    def find_extremum(df, col_name='ref_smooth', prominence=0.01):
        """极值点（波峰/波谷）自适应识别"""
        y = df[col_name].values
        x = df['wavelength'].values
        
        # 找波峰
        peaks, _ = find_peaks(y, prominence=prominence)
        # 找波谷 (对负值找波峰)
        valleys, _ = find_peaks(-y, prominence=prominence)
        
        extremum_info = {
            'peaks_x': x[peaks],
            'peaks_y': y[peaks],
            'valleys_x': x[valleys],
            'valleys_y': y[valleys]
        }
        return extremum_info

    @staticmethod
    def normalize(df, col_name='ref_smooth'):
        """数据归一化 [0, 1]"""
        df_processed = df.copy()
        min_val = df_processed[col_name].min()
        max_val = df_processed[col_name].max()
        df_processed['ref_norm'] = (df_processed[col_name] - min_val) / (max_val - min_val)
        return df_processed