"""本地校验：内置样例光谱的厚度反演与 R²"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from si.algorithms.models import InterferenceModels
from si.algorithms.preprocess import SpectrumPreprocessor
from si.utils.csv_spectrum import load_wavenumber_csv
from si.utils.paths import SAMPLES_DIR

CASES = [
    ("test_sic_15um.csv", "SIC", 15.0),
    ("test_sic_30um.csv", "SIC", 30.0),
    ("test_si_2um.csv", "SI", 2.0),
    ("test_gaas_5um.csv", "GAAS", 5.0),
    ("test_ge_8um.csv", "GE", 8.0),
]


def run_one(fname, mat, expect):
    path = SAMPLES_DIR / fname
    wl, ref = load_wavenumber_csv(path)
    sg_win = SpectrumPreprocessor.suggest_smooth_window(wl, ref)
    df = SpectrumPreprocessor.smooth_filter(
        pd.DataFrame({"wavelength": wl, "reflectance": ref}),
        window=sg_win,
    )
    ex = SpectrumPreprocessor.find_extremum(df, "ref_smooth")
    inv = InterferenceModels.run_inversion(
        df["wavelength"].values,
        df["ref_smooth"].values,
        ex["peaks_x"],
        ex["valleys_x"],
        mat,
        10.0,
    )
    err = abs(inv["thickness_um"] - expect) / expect * 100
    ok = inv["r_squared"] > 0.85 and err < 15
    print(
        f"{fname}: d={inv['thickness_um']}um (目标{expect}) "
        f"R2={inv['r_squared']} err={err:.1f}% {'OK' if ok else 'WARN'}"
    )
    return ok


if __name__ == "__main__":
    ok_all = all(run_one(*c) for c in CASES)
    sys.exit(0 if ok_all else 1)
