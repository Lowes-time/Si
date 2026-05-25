"""分析结果统计：置信区间与信噪比"""

import numpy as np
from scipy import stats


class StatisticalAnalyzer:

    @staticmethod
    def calculate_confidence_intervals(residuals, jacobian, confidence_level=0.95):
        if jacobian is None or residuals is None:
            return np.zeros(1)

        n_data = len(residuals)
        n_params = jacobian.shape[1]
        dof = max(1, n_data - n_params)
        mse = np.sum(residuals ** 2) / dof

        try:
            j_t_j = np.dot(jacobian.T, jacobian)
            cov = mse * np.linalg.inv(j_t_j)
            std_err = np.sqrt(np.maximum(0, np.diag(cov)))
        except np.linalg.LinAlgError:
            std_err = np.zeros(n_params)

        t_val = stats.t.ppf((1 + confidence_level) / 2.0, dof)
        return t_val * std_err

    @staticmethod
    def calculate_snr(signal, noise):
        signal_power = np.mean(np.asarray(signal) ** 2)
        noise_power = np.mean(np.asarray(noise) ** 2)
        if noise_power == 0:
            return float("inf")
        return 10 * np.log10(signal_power / noise_power)
