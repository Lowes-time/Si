"""高级预处理：ALS 基线与 Reststrahlen 带剔除"""

import numpy as np
import pandas as pd


class AdvancedPreprocessor:

    @staticmethod
    def asymmetric_least_squares_baseline(y, lam=1e5, p=0.01, n_iter=10):
        try:
            from scipy import sparse
            from scipy.sparse.linalg import spsolve

            y = np.asarray(y, dtype=float)
            L = len(y)
            D = sparse.diags([1, -2, 1], [0, -1, -2], shape=(L, L - 2))
            D = lam * D.dot(D.transpose())
            w = np.ones(L)
            for _ in range(n_iter):
                W = sparse.spdiags(w, 0, L, L)
                Z = W + D
                z = spsolve(Z, w * y)
                w = p * (y > z) + (1 - p) * (y < z)
            return z
        except ImportError:
            return np.ones_like(y) * np.min(y)

    @staticmethod
    def mask_reststrahlen_band(df, material="SiC"):
        df_clean = df.copy()
        if str(material).upper() == "SIC":
            mask = (df_clean["wavelength"] >= 10.0) & (df_clean["wavelength"] <= 12.5)
            df_clean.loc[mask, "reflectance"] = np.nan
        return df_clean.dropna(subset=["reflectance"]).reset_index(drop=True)
