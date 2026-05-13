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
        data_len = len(df['reflectance'])
        
        if method == 'sg':
            # 确保window_length是奇数且不大于数据长度
            if data_len < window:
                window = data_len if data_len % 2 == 1 else data_len - 1
            if window < 3:
                window = 3
            # 确保polyorder < window
            effective_polyorder = min(polyorder, window - 1)
            if effective_polyorder < 0:
                effective_polyorder = 0
            df_processed['ref_smooth'] = savgol_filter(df['reflectance'], window_length=window, polyorder=effective_polyorder)
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
    def find_extremum(df, col_name='ref_smooth', prominence=None):
        """极值点（波峰/波谷）自适应识别"""
        y = df[col_name].values
        x = df['wavelength'].values
        
        # 自动计算prominence（基于数据范围）
        if prominence is None:
            y_range = y.max() - y.min()
            prominence = max(0.001, y_range * 0.01)  # 使用数据范围的1%，最小0.001
        
        # 找波峰
        peaks, _ = find_peaks(y, prominence=prominence)
        # 找波谷 (对负值找波峰)
        valleys, _ = find_peaks(-y, prominence=prominence)
        
        # 如果prominence太高导致找不到极值，尝试降低
        if len(peaks) + len(valleys) < 2 and prominence > 0.001:
            for p in [0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0001]:
                peaks, _ = find_peaks(y, prominence=p)
                valleys, _ = find_peaks(-y, prominence=p)
                if len(peaks) + len(valleys) >= 2:
                    prominence = p
                    break
        
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