# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# 设置中文字体防止乱码
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

class Visualizer:
    """全流程可视化功能开发"""
    
    @staticmethod
    def plot_spectrum_tk(frame, wl, ref, title="原始光谱数据"):
        """将图像嵌入到Tkinter Frame中"""
        # 清空frame
        for widget in frame.winfo_children():
            widget.destroy()
            
        fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
        ax.plot(wl, ref, label='Spectra', color='b', linewidth=1.5)
        ax.set_xlabel('波长 (μm)')
        ax.set_ylabel('反射率')
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return fig

    @staticmethod
    def plot_fit_result_tk(frame, wl, ref_exp, ref_fit, title="拟合结果对比"):
        """绘制实验数据与拟合曲线对比图"""
        for widget in frame.winfo_children():
            widget.destroy()
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 5), dpi=100, gridspec_kw={'height_ratios': [3, 1]})
        
        # 上图：拟合对比
        ax1.plot(wl, ref_exp, 'o', ms=3, label='实验数据', alpha=0.7)
        ax1.plot(wl, ref_fit, '-', label='模型拟合', linewidth=2, color='r')
        ax1.set_ylabel('反射率')
        ax1.set_title(title)
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.6)
        
        # 下图：残差分析
        residuals = ref_exp - ref_fit
        ax2.plot(wl, residuals, '.-', ms=4, color='g')
        ax2.axhline(0, color='black', linestyle='--', linewidth=1)
        ax2.set_xlabel('波长 (μm)')
        ax2.set_ylabel('残差')
        ax2.grid(True, linestyle='--', alpha=0.6)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        return fig