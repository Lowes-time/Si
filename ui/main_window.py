# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np

# 导入核心层和工具层
from utils.data_io import DataIO
from core.preprocess import SpectrumPreprocessor
from core.models import InterferenceModels
from utils.visualization import Visualizer

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.data_df = None
        self.processed_df = None
        self.current_material = tk.StringVar(value="SiC")
        self.current_angle = tk.DoubleVar(value=10.0)
        
        self._build_ui()
        
    def _build_ui(self):
        """构建界面布局"""
        control_frame = ttk.Frame(self.root, width=320, padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.plot_frame = ttk.Frame(self.root, padding=10)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 1. 数据导入区
        lf_data = ttk.LabelFrame(control_frame, text="1. 数据导入", padding=10)
        lf_data.pack(fill=tk.X, pady=5)
        ttk.Button(lf_data, text="选择光谱文件...", command=self.load_data).pack(fill=tk.X)
        self.lbl_file = ttk.Label(lf_data, text="未加载文件", foreground="gray")
        self.lbl_file.pack(pady=5)
        
        # 2. 预处理配置区
        lf_prep = ttk.LabelFrame(control_frame, text="2. 预处理设置", padding=10)
        lf_prep.pack(fill=tk.X, pady=5)
        ttk.Label(lf_prep, text="滤波窗口大小:").grid(row=0, column=0, sticky=tk.W)
        self.spin_window = ttk.Spinbox(lf_prep, from_=5, to=51, increment=2, width=10)
        self.spin_window.set(15)
        self.spin_window.grid(row=0, column=1, pady=5)
        
        # 【修复点1】将 fill=tk.X 改为 sticky=tk.EW
        ttk.Button(lf_prep, text="执行平滑与极值提取", command=self.preprocess_data).grid(row=1, columnspan=2, sticky=tk.EW, pady=5)
        
        # 3. 参数与计算区
        lf_calc = ttk.LabelFrame(control_frame, text="3. 膜厚反演参数", padding=10)
        lf_calc.pack(fill=tk.X, pady=5)
        ttk.Label(lf_calc, text="基底材料:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(lf_calc, textvariable=self.current_material, values=["SiC", "Si"], width=10).grid(row=0, column=1)
        ttk.Label(lf_calc, text="入射角(°):").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(lf_calc, textvariable=self.current_angle, width=13).grid(row=1, column=1, pady=5)
        
        # 【修复点2】将 fill=tk.X 改为 sticky=tk.EW
        ttk.Button(lf_calc, text="执行厚度拟合与反演", command=self.calculate_thickness).grid(row=2, columnspan=2, sticky=tk.EW, pady=10)
        
        # 4. 结果展示区
        lf_res = ttk.LabelFrame(control_frame, text="4. 分析结果日志", padding=10)
        lf_res.pack(fill=tk.BOTH, expand=True, pady=5)
        self.txt_result = tk.Text(lf_res, height=15, width=30)
        self.txt_result.pack(fill=tk.BOTH, expand=True)

    def load_data(self):
        filepath = filedialog.askopenfilename(filetypes=[("Data Files", "*.csv *.txt *.xlsx")])
        if not filepath:
            return
        success, res = DataIO.read_spectrum_data(filepath)
        if success:
            self.data_df = res
            self.lbl_file.config(text=filepath.split('/')[-1])
            messagebox.showinfo("成功", f"数据加载成功，共 {len(self.data_df)} 行数据。")
            Visualizer.plot_spectrum_tk(self.plot_frame, self.data_df['wavelength'], self.data_df['reflectance'], "导入的原始光谱")
        else:
            messagebox.showerror("错误", res)

    def preprocess_data(self):
        if self.data_df is None:
            messagebox.showwarning("警告", "请先导入数据！")
            return
        window = int(self.spin_window.get())
        self.processed_df = SpectrumPreprocessor.smooth_filter(self.data_df, method='sg', window=window)
        Visualizer.plot_spectrum_tk(self.plot_frame, self.processed_df['wavelength'], self.processed_df['ref_smooth'], "滤波平滑后的光谱")
        self.txt_result.insert(tk.END, "预处理完成。\n")

    def calculate_thickness(self):
        if self.processed_df is None:
            messagebox.showwarning("警告", "请先执行预处理！")
            return
        material = self.current_material.get()
        theta = self.current_angle.get()
        
        extrema = SpectrumPreprocessor.find_extremum(self.processed_df)
        init_d = InterferenceModels.init_thickness_estimate(extrema['peaks_x'], extrema['valleys_x'], material, theta)
        self.txt_result.insert(tk.END, f"干涉条纹初估厚度: {init_d:.3f} μm\n")
        
        interf_type = InterferenceModels.detect_multi_beam(self.processed_df['ref_smooth'].values)
        self.txt_result.insert(tk.END, f"检测到: {interf_type}\n")
        
        wl = self.processed_df['wavelength'].values
        ref_exp = self.processed_df['ref_smooth'].values
        
        res = InterferenceModels.optimize_thickness(wl, ref_exp, init_d, material, theta)
        d_final = res['thickness_um']
        r2 = res['r_squared']
        
        self.txt_result.insert(tk.END, f"模型拟合厚度: {d_final:.4f} μm\n")
        self.txt_result.insert(tk.END, f"拟合优度 R²: {r2:.4f}\n")
        self.txt_result.insert(tk.END, "-"*20 + "\n")
        
        ref_fit = InterferenceModels.two_beam_reflectance(wl, d_final, material, theta)
        Visualizer.plot_fit_result_tk(self.plot_frame, wl, ref_exp, ref_fit, f"外延层厚度拟合结果 (d={d_final:.2f}μm)")
        self.txt_result.see(tk.END)