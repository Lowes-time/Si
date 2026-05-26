"""用与反演一致的光学模型生成演示用 CSV 样例"""

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from si.algorithms.models import InterferenceModels
from si.utils.paths import FRONTEND_SAMPLES_DIR, SAMPLES_DIR

THETA = 10.0
N_PTS = 320

CASES = [
    ("test_sic_15um.csv", "SIC", 15.0, 1000, 2000, 0.002),
    ("test_sic_30um.csv", "SIC", 30.0, 1000, 2000, 0.002),
    ("test_si_2um.csv", "SI", 2.0, 2000, 4500, 0.0008),
    ("test_gaas_5um.csv", "GAAS", 5.0, 1000, 2000, 0.002),
    ("test_ge_8um.csv", "GE", 8.0, 1000, 2000, 0.0015),
]


def build_spectrum(material, thickness_um, wn_min=1000, wn_max=2000, n_pts=N_PTS, noise=0.002):
    wavenumbers = np.linspace(wn_min, wn_max, n_pts)
    wavelengths = 10000.0 / wavenumbers
    ref = InterferenceModels.two_beam_reflectance(wavelengths, thickness_um, material, THETA)
    ref = ref + np.random.normal(0, noise, size=len(ref))
    ref = np.clip(ref, 0.02, 0.98)
    return wavenumbers, ref


def write_csv(path, wn, ref):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["wavenumber", "reflectance"])
        for a, b in zip(wn, ref):
            w.writerow([f"{a:.6f}", f"{b:.8f}"])


def main():
    np.random.seed(42)
    out_dirs = [SAMPLES_DIR, FRONTEND_SAMPLES_DIR]
    for d in out_dirs:
        d.mkdir(parents=True, exist_ok=True)

    for fname, mat, thick, wn0, wn1, noise in CASES:
        wn, ref = build_spectrum(mat, thick, wn0, wn1, noise=noise)
        for d in out_dirs:
            write_csv(d / fname, wn, ref)
        print(f"{fname}: {mat} {thick}um -> {d / fname}")

    print("done")


if __name__ == "__main__":
    main()
