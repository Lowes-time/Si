# -*- coding: utf-8 -*-
# 软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0
# 软件功能：反演结果可靠性评估与参数敏感度分析引擎

import numpy as np
from scipy import stats

class StatisticalAnalyzer:
    """干涉拟合结果高级统计分析引擎"""

    @staticmethod
    def calculate_confidence_intervals(residuals: np.ndarray, jacobian: np.ndarray, confidence_level: float = 0.95) -> np.ndarray:
        """
        基于雅可比矩阵计算反演参数的置信区间 (Confidence Intervals)
        Args:
            residuals: 拟合残差数组
            jacobian: 最小二乘拟合返回的雅可比矩阵 (J)
            confidence_level: 置信度水平 (默认 95%)
        Returns:
            np.ndarray: 参数的置信区间半径
        """
        if jacobian is None or residuals is None:
            return np.zeros(1)

        n_data_points = len(residuals)
        n_parameters = jacobian.shape[1]
        degrees_of_freedom = max(1, n_data_points - n_parameters)

        # 计算均方误差 (MSE)
        mse = np.sum(residuals ** 2) / degrees_of_freedom

        # 计算协方差矩阵近似: C = MSE * (J^T * J)^-1
        try:
            j_t_j = np.dot(jacobian.T, jacobian)
            covariance_matrix = mse * np.linalg.inv(j_t_j)
            parameter_variances = np.diag(covariance_matrix)
            standard_errors = np.sqrt(np.maximum(0, parameter_variances)) # 确保方差非负
        except np.linalg.LinAlgError:
            # 奇异矩阵处理
            standard_errors = np.zeros(n_parameters)

        # 使用 t 分布计算临界值
        t_value = stats.t.ppf((1 + confidence_level) / 2.0, degrees_of_freedom)
        
        # 返回置信区间半径 (Margin of Error)
        return t_value * standard_errors

    @staticmethod
    def calculate_sensitivity_matrix(wl_um: np.ndarray, ref_exp: np.ndarray, fit_func, base_params: list, perturbation: float = 1e-4) -> dict:
        """
        参数灵敏度分析 (Sensitivity Analysis)
        评估单参数微小扰动对整体反射率光谱的影响程度
        """
        base_fit = fit_func(*base_params)
        sensitivities = {}
        
        param_names = ["thickness_d", "k0", "k1", "k2", "sigma"]
        
        for i in range(len(base_params)):
            # 正向扰动
            perturbed_params_plus = list(base_params)
            perturbed_params_plus[i] += perturbation
            fit_plus = fit_func(*perturbed_params_plus)
            
            # 反向扰动
            perturbed_params_minus = list(base_params)
            perturbed_params_minus[i] -= perturbation
            fit_minus = fit_func(*perturbed_params_minus)
            
            # 计算中心差分导数 (∂R / ∂p_i)
            gradient = (fit_plus - fit_minus) / (2 * perturbation)
            
            # 计算灵敏度指标 (相对均方根变化)
            sensitivity_score = np.sqrt(np.mean(gradient ** 2))
            
            name = param_names[i] if i < len(param_names) else f"param_{i}"
            sensitivities[name] = float(sensitivity_score)
            
        return sensitivities

    @staticmethod
    def calculate_snr(signal: np.ndarray, noise: np.ndarray) -> float:
        """计算光谱信噪比 (Signal-to-Noise Ratio)"""
        signal_power = np.mean(signal ** 2)
        noise_power = np.mean(noise ** 2)
        if noise_power == 0:
            return float('inf')
        # 以 dB 为单位返回
        return 10 * np.log10(signal_power / noise_power)