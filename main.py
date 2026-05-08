# -*- coding: utf-8 -*-
import sys
import os

# 【关键修复】强制将当前项目的根目录加入系统路径，解决 ModuleNotFoundError
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import tkinter as tk
from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("半导体薄膜厚度光学测量分析系统 V1.0")
    root.geometry("1024x768")
    
    # 设置全局字体，防止中文乱码
    root.option_add('*Font', 'Microsoft_YaHei 10')
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()