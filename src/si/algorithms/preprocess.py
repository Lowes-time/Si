import numpy as np
import pandas as pd
from scipy.signal import savgol_filter, find_peaks

class SpectrumPreprocessor:
    @staticmethod
    def smooth_filter(df, method='sg', window=15, poly_deg=3):
        df_out = df.copy()
        n_points = len(df['reflectance'])
        
        if method == 'sg':
            if n_points < window:
                window = n_points if n_points % 2 == 1 else n_points - 1
            if window < 3:
                window = 3
            
            real_poly_deg = min(poly_deg, window - 1)
            if real_poly_deg < 0:
                real_poly_deg = 0
                
            df_out['ref_smooth'] = savgol_filter(df['reflectance'], window_length=window, polyorder=real_poly_deg)
        elif method == 'ma':
            df_out['ref_smooth'] = df['reflectance'].rolling(window=window, center=True, min_periods=1).mean()
        else:
            df_out['ref_smooth'] = df['reflectance']
            
        return df_out
    
    @staticmethod
    def baseline_correction(df):
        df_out = df.copy()
        min_val = df_out['ref_smooth'].min()
        df_out['ref_baseline'] = df_out['ref_smooth'] - min_val
        return df_out
    
    @staticmethod
    def find_extremum(df, col_name='ref_smooth', prominence=None):
        y_vals = df[col_name].values
        x_vals = df['wavelength'].values
        
        if prominence is None:
            y_span = y_vals.max() - y_vals.min()
            prominence = max(0.001, y_span * 0.01)
        
        peaks, _ = find_peaks(y_vals, prominence=prominence)
        valleys, _ = find_peaks(-y_vals, prominence=prominence)
        
        if len(peaks) + len(valleys) < 2 and prominence > 0.001:
            fallback_proms = [0.05, 0.02, 0.01, 0.005, 0.002, 0.001, 0.0005, 0.0001]
            for p in fallback_proms:
                peaks, _ = find_peaks(y_vals, prominence=p)
                valleys, _ = find_peaks(-y_vals, prominence=p)
                if len(peaks) + len(valleys) >= 2:
                    prominence = p
                    break
        
        return {
            'peaks_x': x_vals[peaks],
            'peaks_y': y_vals[peaks],
            'valleys_x': x_vals[valleys],
            'valleys_y': y_vals[valleys]
        }
    
    @staticmethod
    def normalize(df, col_name='ref_smooth'):
        df_out = df.copy()
        col_min = df_out[col_name].min()
        col_max = df_out[col_name].max()
        df_out['ref_norm'] = (df_out[col_name] - col_min) / (col_max - col_min)
        return df_out
