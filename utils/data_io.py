# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

class DataIO:
    """数据导入与校验模块"""
    
    @staticmethod
    def read_spectrum_data(filepath, skip_rows=1):
        """读取多格式光谱数据"""
        try:
            _, ext = os.path.splitext(filepath)
            if ext.lower() in ['.txt', '.csv']:
                # 兼容不同分隔符，尝试读取
                df = pd.read_csv(filepath, sep=None, engine='python', skiprows=skip_rows, names=['wavenumber', 'reflectance'])
            elif ext.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath, skiprows=skip_rows, names=['wavenumber', 'reflectance'])
            else:
                return False, "不支持的文件格式，仅支持txt/csv/xlsx"
            
            # 基础转换：波数(cm^-1) 转 波长(um)
            if 'wavenumber' in df.columns:
                df['wavelength'] = 10000.0 / df['wavenumber']
                
            return True, df
        except Exception as e:
            return False, f"数据读取失败: {str(e)}"

    @staticmethod
    def validate_data(df):
        """数据有效性校验与异常值处理"""
        if df is None or df.empty:
            return False, "数据集为空"
        
        # 剔除NaN和无穷大
        df = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # 反射率范围校验 (0-100% 或 0-1)
        if df['reflectance'].max() > 2.0:  # 假设是以百分比表示
            df['reflectance'] = df['reflectance'] / 100.0
            
        return True, df

    @staticmethod
    def filter_band(df, min_wl, max_wl):
        """自定义波段筛选，例如排除Reststrahlen高反射区"""
        filtered_df = df[(df['wavelength'] >= min_wl) & (df['wavelength'] <= max_wl)].copy()
        return filtered_df