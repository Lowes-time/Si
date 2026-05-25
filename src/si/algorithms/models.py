"""薄膜干涉厚度反演：双光束 / Airy 多光束 / FFT 校验"""

import numpy as np
from scipy.optimize import least_squares, differential_evolution
from scipy.stats import kurtosis
from si.algorithms.optical_constants import OpticalConstants


class InterferenceModels:
    """外延层反射光谱正演与厚度反演"""

    THICKNESS_MIN = 0.5
    THICKNESS_MAX = 50.0

    @staticmethod
    def _snell_cos(n, theta_deg):
        theta_rad = np.radians(theta_deg)
        sin_t = np.sin(theta_rad) / np.maximum(n, 1e-6)
        return np.sqrt(np.maximum(0.0, 1.0 - sin_t ** 2))

    @staticmethod
    def _fresnel_rs(n_i, n_j, cos_i, cos_j):
        return (n_i * cos_i - n_j * cos_j) / (n_i * cos_i + n_j * cos_j + 1e-12)

    @staticmethod
    def _fresnel_rp(n_i, n_j, cos_i, cos_j):
        return (n_j * cos_i - n_i * cos_j) / (n_j * cos_i + n_i * cos_j + 1e-12)

    @classmethod
    def _fresnel_R(cls, n_i, n_j, cos_i, cos_j):
        rs = cls._fresnel_rs(n_i, n_j, cos_i, cos_j)
        rp = cls._fresnel_rp(n_i, n_j, cos_i, cos_j)
        return 0.5 * (rs ** 2 + rp ** 2)

    @classmethod
    def _interface_reflectivity(cls, n1, n2, theta_deg):
        """界面能量反射率，n1/n2 可为数组"""
        n1 = np.asarray(n1, dtype=np.float64)
        n2 = np.asarray(n2, dtype=np.float64)
        theta_rad = np.radians(theta_deg)
        cos_i = np.cos(theta_rad)
        if n1.ndim == 0:
            cos_t1 = cls._snell_cos(float(n1), theta_deg)
        else:
            cos_t1 = cls._snell_cos(n1, theta_deg)
        cos_t2 = cls._snell_cos(n2, theta_deg)
        return cls._fresnel_R(n1, n2, cos_i if np.isscalar(n1) else cos_t1, cos_t2)

    @classmethod
    def two_beam_reflectance(cls, wl_um, thickness, material, theta_deg):
        """两光束干涉：空气-外延层-衬底"""
        wl_arr = np.asarray(wl_um, dtype=np.float64)
        n_film = OpticalConstants.calc_refractive_index(wl_arr, material)
        n_sub = OpticalConstants.calc_substrate_index(wl_arr, material)
        cos_f = cls._snell_cos(n_film, theta_deg)
        delta = 4 * np.pi * thickness * n_film * cos_f / wl_arr

        R01 = cls._interface_reflectivity(1.0, n_film, theta_deg)
        R12 = cls._interface_reflectivity(n_film, n_sub, theta_deg)
        amp = np.sqrt(np.clip(R01 * (1 - R01) ** 2 * R12, 0, 1))
        R = R01 + (1 - R01) ** 2 * R12 + 2 * amp * np.cos(delta)
        return np.clip(R, 0.0, 1.0)

    @classmethod
    def airy_reflectance(cls, wl_um, thickness, material, theta_deg):
        """Airy 多光束公式（Fabry-Perot 近似）"""
        wl_arr = np.asarray(wl_um, dtype=np.float64)
        n_film = OpticalConstants.calc_refractive_index(wl_arr, material)
        n_sub = OpticalConstants.calc_substrate_index(wl_arr, material)
        n0 = 1.0

        cos_f = cls._snell_cos(n_film, theta_deg)
        delta = 4 * np.pi * thickness * n_film * cos_f / wl_arr

        r01 = np.sqrt(np.clip(cls._interface_reflectivity(n0, n_film, theta_deg), 0, 0.99))
        r12 = np.sqrt(np.clip(cls._interface_reflectivity(n_film, n_sub, theta_deg), 0, 0.99))

        num = r01 ** 2 + r12 ** 2 + 2 * r01 * r12 * np.cos(delta)
        den = 1 + (r01 * r12) ** 2 + 2 * r01 * r12 * np.cos(delta)
        return np.clip(num / (den + 1e-12), 0.0, 1.0)

    @classmethod
    def reflectance(cls, wl_um, thickness, material, theta_deg, model="two_beam"):
        if model == "airy":
            return cls.airy_reflectance(wl_um, thickness, material, theta_deg)
        return cls.two_beam_reflectance(wl_um, thickness, material, theta_deg)

    @staticmethod
    def fft_thickness_estimate(wl_um, ref_arr, material, theta_deg):
        """FFT 光程差域峰值估计厚度（MMAA 思路）"""
        wl = np.asarray(wl_um, dtype=np.float64)
        y = np.asarray(ref_arr, dtype=np.float64)
        if len(y) < 32:
            return None

        y = y - np.mean(y)
        sigma = 1.0 / wl
        ds = np.mean(np.diff(sigma))
        if ds <= 0:
            return None

        n_avg = float(np.mean(OpticalConstants.calc_refractive_index(wl, material)))
        cos_t = float(np.mean(InterferenceModels._snell_cos(n_avg, theta_deg)))

        fft_mag = np.abs(np.fft.rfft(y))
        freqs = np.fft.rfftfreq(len(y), d=ds)
        fft_mag[0] = 0

        if len(freqs) < 2:
            return None
        peak_idx = int(np.argmax(fft_mag[1:]) + 1)
        opd = freqs[peak_idx]
        if opd <= 0:
            return None

        d = opd / (2 * n_avg * cos_t + 1e-12)
        if InterferenceModels.THICKNESS_MIN <= d <= InterferenceModels.THICKNESS_MAX:
            return float(d)
        return None

    @staticmethod
    def init_thickness_estimate(peaks_wl, valleys_wl, material, theta_deg):
        """极值间距法估算初值"""
        all_extrema = np.sort(np.concatenate([peaks_wl, valleys_wl]))[::-1]
        if len(all_extrema) < 2:
            return 10.0

        theta_rad = np.radians(theta_deg)
        thicknesses = []
        for i in range(len(all_extrema) - 1):
            wl1, wl2 = float(all_extrema[i]), float(all_extrema[i + 1])
            if abs(wl1 - wl2) < 1e-6:
                continue
            n_avg = np.mean([
                OpticalConstants.calc_refractive_index(wl1, material),
                OpticalConstants.calc_refractive_index(wl2, material),
            ])
            cos_t = np.sqrt(max(0, n_avg ** 2 - np.sin(theta_rad) ** 2))
            if cos_t <= 1e-6:
                continue
            thicknesses.append((wl1 * wl2) / (4 * cos_t * abs(wl1 - wl2)))

        if thicknesses:
            init_d = float(np.median(thicknesses))
            return float(np.clip(init_d, InterferenceModels.THICKNESS_MIN, InterferenceModels.THICKNESS_MAX))
        return 10.0

    @classmethod
    def merge_initial_thickness(cls, extrema_init, fft_init):
        candidates = [extrema_init]
        if fft_init is not None:
            candidates.append(fft_init)
        return float(np.median(candidates))

    @classmethod
    def detect_multi_beam(cls, ref_arr, wl_um, material, theta_deg):
        """四指标多光束判定：对比度、峰度、精细度、相干长度比"""
        y = np.asarray(ref_arr, dtype=np.float64)
        wl = np.asarray(wl_um, dtype=np.float64)

        r_max, r_min = float(np.max(y)), float(np.min(y))
        contrast = (r_max - r_min) / (r_max + r_min + 1e-6)

        kurt = float(kurtosis(y, fisher=False)) if len(y) > 8 else 1.5

        n_film = OpticalConstants.calc_refractive_index(wl, material)
        n_sub = OpticalConstants.calc_substrate_index(wl, material)
        r01 = float(np.mean(np.sqrt(cls._interface_reflectivity(1.0, n_film, theta_deg))))
        r12 = float(np.mean(np.sqrt(cls._interface_reflectivity(n_film, n_sub, theta_deg))))
        finesse = np.pi * np.sqrt(r01 * r12) / (1 - r01 * r12 + 1e-6)

        peaks, _ = cls._find_peaks_simple(y)
        if len(peaks) >= 2:
            fringe_period = float(np.mean(np.diff(wl[peaks])))
            lc_ratio = fringe_period / (wl[-1] - wl[0] + 1e-6)
        else:
            lc_ratio = 0.0

        score = 0
        if contrast > 0.15:
            score += 1
        if kurt > 2.0:
            score += 1
        if finesse > 1.5:
            score += 1
        if lc_ratio < 0.05 and contrast > 0.1:
            score += 1

        if score >= 3:
            level = "强多光束干涉"
            model = "airy"
        elif score >= 2:
            level = "中等多光束干涉"
            model = "airy"
        else:
            level = "弱/无多光束干涉"
            model = "two_beam"

        return {
            "level": level,
            "recommended_model": model,
            "contrast": round(contrast, 4),
            "kurtosis": round(kurt, 4),
            "finesse": round(float(finesse), 4),
            "coherence_ratio": round(lc_ratio, 4),
            "score": score,
        }

    @staticmethod
    def _find_peaks_simple(y):
        from scipy.signal import find_peaks
        peaks, props = find_peaks(y, prominence=max(0.001, (y.max() - y.min()) * 0.02))
        valleys, _ = find_peaks(-y, prominence=max(0.001, (y.max() - y.min()) * 0.02))
        return peaks, valleys

    @classmethod
    def optimize_thickness(cls, wl_um, ref_arr, init_d, material, theta_deg, model="two_beam", bounds=None):
        wl_arr = np.asarray(wl_um, dtype=np.float64)
        ref_arr = np.asarray(ref_arr, dtype=np.float64)
        lo = cls.THICKNESS_MIN if bounds is None else bounds[0]
        hi = cls.THICKNESS_MAX if bounds is None else bounds[1]
        init_d = float(np.clip(init_d, lo, hi))

        def residual(d_guess):
            r_fit = cls.reflectance(wl_arr, d_guess[0], material, theta_deg, model=model)
            return r_fit - ref_arr

        def cost_scalar(d_val):
            r_fit = cls.reflectance(wl_arr, float(d_val), material, theta_deg, model=model)
            return float(np.sum((r_fit - ref_arr) ** 2))

        jacobian = None
        optimizer = "least_squares"

        if model == "airy":
            optimizer = "differential_evolution"
            de_bounds = [(lo, hi)]
            de_res = differential_evolution(
                lambda x: cost_scalar(x[0]),
                de_bounds,
                seed=42,
                maxiter=80,
                popsize=12,
                tol=1e-4,
                polish=True,
            )
            init_d = float(de_res.x[0])
            optimizer = "de+lm"

        try:
            res = least_squares(residual, [init_d], bounds=([lo], [hi]), method="trf")
            jacobian = res.jac
            ss_res = float(np.sum(res.fun ** 2))
            ss_tot = float(np.sum((ref_arr - np.mean(ref_arr)) ** 2))
            r_squared = 1 - (ss_res / (ss_tot + 1e-10))
            return {
                "thickness_um": float(res.x[0]),
                "r_squared": float(r_squared),
                "cost": float(ss_res),
                "jacobian": jacobian,
                "residuals": res.fun,
                "optimizer": optimizer,
            }
        except Exception:
            from scipy.optimize import minimize
            result = minimize(lambda x: cost_scalar(x[0]), [init_d], bounds=[(lo, hi)], method="L-BFGS-B")
            ss_res = result.fun
            ss_tot = float(np.sum((ref_arr - np.mean(ref_arr)) ** 2))
            return {
                "thickness_um": float(result.x[0]),
                "r_squared": float(1 - ss_res / (ss_tot + 1e-10)),
                "cost": float(ss_res),
                "jacobian": None,
                "residuals": None,
                "optimizer": "lbfgs",
            }

    @classmethod
    def run_inversion(cls, wl_um, ref_arr, peaks_wl, valleys_wl, material, theta_deg):
        """完整反演流程：判定 → 初值 → 拟合"""
        beam = cls.detect_multi_beam(ref_arr, wl_um, material, theta_deg)
        model = beam["recommended_model"]

        ext_init = cls.init_thickness_estimate(peaks_wl, valleys_wl, material, theta_deg)
        fft_init = cls.fft_thickness_estimate(wl_um, ref_arr, material, theta_deg)
        init_d = cls.merge_initial_thickness(ext_init, fft_init)

        bounds = (cls.THICKNESS_MIN, cls.THICKNESS_MAX)
        if fft_init is not None:
            half = max(1.0, fft_init * 0.2)
            bounds = (
                max(cls.THICKNESS_MIN, fft_init - half),
                min(cls.THICKNESS_MAX, fft_init + half),
            )

        fit_two = cls.optimize_thickness(
            wl_um, ref_arr, init_d, material, theta_deg, model="two_beam", bounds=bounds
        )
        fit_airy = cls.optimize_thickness(
            wl_um, ref_arr, init_d, material, theta_deg, model="airy", bounds=bounds
        )
        if fit_airy["r_squared"] > fit_two["r_squared"] + 0.02:
            fit = fit_airy
            model = "airy"
        else:
            fit = fit_two
            model = "two_beam"
            if beam["recommended_model"] == "airy":
                beam = {**beam, "level": "弱/无多光束干涉", "recommended_model": "two_beam"}

        ref_fit = cls.reflectance(wl_um, fit["thickness_um"], material, theta_deg, model=model)

        return {
            "init_thickness_um": round(init_d, 4),
            "extrema_init_um": round(ext_init, 4),
            "fft_thickness_um": round(fft_init, 4) if fft_init else None,
            "multi_beam_level": beam["level"],
            "fit_model": model,
            "metrics": {
                "contrast": beam["contrast"],
                "kurtosis": beam["kurtosis"],
                "finesse": beam["finesse"],
                "coherence_ratio": beam["coherence_ratio"],
            },
            "thickness_um": round(fit["thickness_um"], 4),
            "r_squared": round(fit["r_squared"], 4),
            "cost": round(fit["cost"], 6),
            "optimizer": fit["optimizer"],
            "ref_fit": ref_fit,
            "_fit_internal": fit,
        }
