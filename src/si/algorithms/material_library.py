# -*- coding: utf-8 -*-
"""
软件名称：基于多光束干涉校正的半导体外延层厚度光谱反演系统 V1.0
软件功能：半导体材料光学色散特性参数库
包含多种半导体材料的光学常数计算模型
"""

import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseMaterial(ABC):
    """半导体材料基类定义"""
    
    @abstractmethod
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算指定波长下的折射率"""
        pass
    
    @abstractmethod
    def get_bandgap(self) -> float:
        """获取材料带隙能量 (eV)"""
        pass
    
    @abstractmethod
    def get_material_info(self) -> Dict:
        """获取材料基本信息"""
        pass


class Silicon(BaseMaterial):
    """单晶硅 (Si) 光学模型
    
    适用于近红外至中红外波段的折射率计算
    使用高精度Sellmeier经验公式，含温度补偿修正
    """
    
    def __init__(self):
        self.name_cn = "硅"
        self.name_en = "Silicon"
        self.formula = "Si"
        self.crystal_structure = "金刚石立方"
        self.bandgap_ev = 1.12
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """使用Sellmeier方程计算Si的折射率，适用于 1.2-15 μm 波段"""
        wavelength = np.asarray(wavelength_um)
        ls = wavelength ** 2
        
        dn = ls - 0.028
        t1 = 0.159906 / dn
        t2 = -0.123109 / (dn ** 2)
        t3 = 1.26878e-6 * ls
        t4 = -1.95104e-9 * (ls ** 2)
        
        n_base = 3.41983 + t1 + t2 + t3 + t4
        temp_correction = 1.5e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_base)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "太阳能电池、IC衬底、MEMS"
        }


class SiliconCarbide(BaseMaterial):
    """碳化硅 (4H-SiC) 光学模型
    
    适用于紫外至红外波段的高功率器件材料
    使用修正Sellmeier公式计算折射率
    """
    
    def __init__(self):
        self.name_cn = "碳化硅"
        self.name_en = "Silicon Carbide"
        self.formula = "SiC"
        self.polytype = "4H"
        self.crystal_structure = "六方纤锌矿"
        self.bandgap_ev = 3.26
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """使用Sellmeier方程计算4H-SiC的折射率，适用于 0.4-12 μm 波段"""
        wavelength = np.asarray(wavelength_um)
        lambda_sq = wavelength ** 2
        
        denominator = lambda_sq - 0.0388
        denominator = np.where(np.abs(denominator) < 1e-5, 1e-5, denominator)
        
        n_sq = 4.148 + (2.378 * lambda_sq) / denominator
        temp_correction = 8e-5 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "polytype": self.polytype,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "功率器件、射频器件、LED衬底"
        }


class GalliumNitride(BaseMaterial):
    """氮化镓 (GaN) 光学模型
    
    适用于蓝光/紫外LED和功率器件
    基于Zhao等人提出的色散公式
    """
    
    def __init__(self):
        self.name_cn = "氮化镓"
        self.name_en = "Gallium Nitride"
        self.formula = "GaN"
        self.crystal_structure = "六方纤锌矿"
        self.bandgap_ev = 3.39
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """使用改进Sellmeier方程计算GaN的折射率，适用于 0.36-10 μm 波段"""
        wavelength = np.asarray(wavelength_um)
        lambda_sq = wavelength ** 2
        
        n_sq = 2.275 + (3.057 * lambda_sq) / (lambda_sq - 0.088**2)
        temp_correction = 2.5e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "蓝光LED、激光器、功率器件"
        }


class AluminumNitride(BaseMaterial):
    """氮化铝 (AlN) 光学模型
    
    适用于UVC LED和高温电子器件
    宽禁带半导体
    """
    
    def __init__(self):
        self.name_cn = "氮化铝"
        self.name_en = "Aluminum Nitride"
        self.formula = "AlN"
        self.crystal_structure = "六方纤锌矿"
        self.bandgap_ev = 6.2
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算AlN的折射率 - UV到红外波段"""
        wavelength = np.asarray(wavelength_um)
        lambda_um = wavelength
        
        n_sq = 1.0 + 2.0768 * lambda_um**2 / (lambda_um**2 - 0.1176**2) \
               + 3.8260 * lambda_um**2 / (lambda_um**2 - 7.8925**2)
        
        temp_correction = 1.8e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "UVC LED、滤波器、高功率器件"
        }


class IndiumPhosphide(BaseMaterial):
    """磷化铟 (InP) 光学模型
    
    适用于光通信器件和红外探测器
    直接带隙半导体
    """
    
    def __init__(self):
        self.name_cn = "磷化铟"
        self.name_en = "Indium Phosphide"
        self.formula = "InP"
        self.crystal_structure = "闪锌矿"
        self.bandgap_ev = 1.35
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算InP的折射率 - 近红外到中红外"""
        wavelength = np.asarray(wavelength_um)
        lambda_sq = wavelength ** 2
        
        n_sq = 1.0 + 7.2669 * lambda_sq / (lambda_sq - 0.38954**2) \
               + 0.22873 * lambda_sq / (lambda_sq - 31.130**2)
        
        temp_correction = 3.2e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "光通信激光器、探测器、太阳能电池"
        }


class GalliumArsenide(BaseMaterial):
    """砷化镓 (GaAs) 光学模型
    
    适用于微波/毫米波和红外器件
    直接带隙半导体
    """
    
    def __init__(self):
        self.name_cn = "砷化镓"
        self.name_en = "Gallium Arsenide"
        self.formula = "GaAs"
        self.crystal_structure = "闪锌矿"
        self.bandgap_ev = 1.42
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算GaAs的折射率 - 近红外到太赫兹"""
        wavelength = np.asarray(wavelength_um)
        lambda_um = wavelength
        
        n_sq = 1.0 + 5.3724 * lambda_um**2 / (lambda_um**2 - 0.443**2) \
               + 0.2127 * lambda_um**2 / (lambda_um**2 - 0.874**2) \
               + 4.0597 * lambda_um**2 / (lambda_um**2 - 36.916**2)
        
        temp_correction = 2.8e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "射频器件、红外激光器、太阳能电池"
        }


class ZincOxide(BaseMaterial):
    """氧化锌 (ZnO) 光学模型
    
    适用于UV LED和压电器件
    宽禁带半导体
    """
    
    def __init__(self):
        self.name_cn = "氧化锌"
        self.name_en = "Zinc Oxide"
        self.formula = "ZnO"
        self.crystal_structure = "六方纤锌矿"
        self.bandgap_ev = 3.37
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算ZnO的折射率 - 紫外到红外"""
        wavelength = np.asarray(wavelength_um)
        lambda_sq = wavelength ** 2
        
        n_sq = 1.0 + 1.9887 * lambda_sq / (lambda_sq - 0.075**2) \
               + 2.3468 * lambda_sq / (lambda_sq - 7.385**2)
        
        temp_correction = 1.5e-4 * (temp_k - 300.0)
        
        return np.sqrt(np.maximum(1.0, n_sq)) + temp_correction
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "UV LED、声表面波器件、透明导电薄膜"
        }


class Diamond(BaseMaterial):
    """金刚石 (Diamond) 光学模型
    
    适用于高功率器件和深紫外探测
    超宽禁带半导体
    """
    
    def __init__(self):
        self.name_cn = "金刚石"
        self.name_en = "Diamond"
        self.formula = "C"
        self.crystal_structure = "金刚石立方"
        self.bandgap_ev = 5.47
    
    def get_refractive_index(self, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """计算金刚石的折射率 - 紫外到红外"""
        wavelength = np.asarray(wavelength_um)
        lambda_um = wavelength
        
        n_sq = 1.0 + 0.3306 * lambda_um**2 / (lambda_um**2 - 0.175**2) \
               + 4.0688 * lambda_um**2 / (lambda_um**2 - 0.175**2)**2
        
        return np.sqrt(np.maximum(1.0, n_sq))
    
    def get_bandgap(self) -> float:
        return self.bandgap_ev
    
    def get_material_info(self) -> Dict:
        return {
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "formula": self.formula,
            "crystal_structure": self.crystal_structure,
            "bandgap_ev": self.bandgap_ev,
            "application": "高功率器件、辐射探测器、热沉材料"
        }


class MaterialFactory:
    """半导体材料工厂类
    
    负责材料的注册、实例化和查询
    使用单例模式确保材料对象不重复创建
    """
    
    _registry: Dict[str, BaseMaterial] = {}
    _initialized = False
    
    @classmethod
    def _initialize(cls):
        """初始化材料注册表"""
        if cls._initialized:
            return
        
        cls._registry = {
            'SI': Silicon(),
            'SIC': SiliconCarbide(),
            'GAN': GalliumNitride(),
            'ALN': AluminumNitride(),
            'INP': IndiumPhosphide(),
            'GAAS': GalliumArsenide(),
            'ZNO': ZincOxide(),
            'C': Diamond(),
            
            'SILICON': Silicon(),
            'SILICON_CARBIDE': SiliconCarbide(),
            'GALLIUM_NITRIDE': GalliumNitride(),
            'ALUMINUM_NITRIDE': AluminumNitride(),
            'INDIUM_PHOSPHIDE': IndiumPhosphide(),
            'GALLIUM_ARSENIDE': GalliumArsenide(),
            'ZINC_OXIDE': ZincOxide(),
            'DIAMOND': Diamond(),
        }
        
        cls._initialized = True
    
    @classmethod
    def get_refractive_index(cls, material_name: str, wavelength_um: np.ndarray, temp_k: float = 300.0) -> np.ndarray:
        """获取指定材料的折射率"""
        cls._initialize()
        
        mat_key = str(material_name).strip().upper()
        
        if mat_key in cls._registry:
            return cls._registry[mat_key].get_refractive_index(wavelength_um, temp_k)
        
        return cls._registry['SIC'].get_refractive_index(wavelength_um, temp_k)
    
    @classmethod
    def get_material(cls, material_name: str) -> Optional[BaseMaterial]:
        """获取材料实例"""
        cls._initialize()
        
        mat_key = str(material_name).strip().upper()
        return cls._registry.get(mat_key)
    
    @classmethod
    def list_materials(cls) -> list:
        """列出所有可用的材料"""
        cls._initialize()
        
        materials = []
        seen = set()
        for key, mat in cls._registry.items():
            if isinstance(mat, BaseMaterial) and key not in seen:
                seen.add(key)
                materials.append({
                    'key': key,
                    'name_cn': mat.name_cn,
                    'name_en': mat.name_en,
                    'formula': mat.formula,
                    'bandgap_ev': mat.bandgap_ev,
                    'application': mat.get_material_info()['application']
                })
        
        return materials
    
    @classmethod
    def is_supported(cls, material_name: str) -> bool:
        """检查材料是否支持"""
        cls._initialize()
        
        mat_key = str(material_name).strip().upper()
        return mat_key in cls._registry and isinstance(cls._registry[mat_key], BaseMaterial)