# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import os

def generate_test_csv(filename, thickness_um, material="SiC"):
    # 模拟 1000-2000 cm-1 的波数范围
    wavenumbers = np.linspace(1000, 2000, 200)
    wavelengths = 10000.0 / wavenumbers
    
    # 简单的干涉模型: R = 0.5 + 0.4 * cos(4 * pi * d * n * cos(theta) / lambda)
    # 模拟 n=2.6 (SiC), theta=10deg
    n = 2.6 if material == "SiC" else 3.4
    theta_rad = np.radians(10)
    cos_theta_t = np.sqrt(n**2 - np.sin(theta_rad)**2)
    
    delta = (4 * np.pi * thickness_um * cos_theta_t) / wavelengths
    reflectance = 0.5 + 0.35 * np.cos(delta + np.pi)
    
    # 添加少量噪声
    reflectance += np.random.normal(0, 0.01, size=len(reflectance))
    
    df = pd.DataFrame({
        "wavenumber": wavenumbers,
        "reflectance": reflectance
    })
    
    df.to_csv(filename, index=False)
    print(f"已生成测试文件: {filename} (理论厚度: {thickness_um}um)")

if __name__ == "__main__":
    generate_test_csv("test_sic_15um.csv", 15.0, "SiC")
    generate_test_csv("test_si_2um.csv", 2.0, "Si")
    generate_test_csv("test_sic_30um.csv", 30.0, "SiC")
