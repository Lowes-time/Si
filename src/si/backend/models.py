# -*- coding: utf-8 -*-
"""
数据库模型层：薄膜分析记录表 + 光学数据表
用于存储半导体外延层厚度测量数据
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from si.backend.database import Base


class FilmRecord(Base):
    """薄膜分析记录表：存储每一次膜厚测量的核心数据"""
    __tablename__ = "film_records"

    id = Column(Integer, primary_key=True, index=True)
    film_code = Column(String(100), nullable=False, index=True)
    material_type = Column(String(10), nullable=False)
    thickness_um = Column(Float, nullable=True)
    r_squared = Column(Float, nullable=True)
    multi_beam_level = Column(String(50), nullable=True)
    theta_deg = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    optical_data = relationship("OpticalData", back_populates="record", cascade="all, delete-orphan")


class OpticalData(Base):
    """光学数据表：存储光谱数据点（波长、反射率、拟合值）"""
    __tablename__ = "optical_data"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("film_records.id", ondelete="CASCADE"), index=True, nullable=False)
    wavelength = Column(Float, nullable=False, index=True)
    reflectance = Column(Float, nullable=False)
    fitted_reflectance = Column(Float, nullable=True)
    seq_order = Column(Integer, default=0)

    record = relationship("FilmRecord", back_populates="optical_data")